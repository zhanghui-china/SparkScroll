import base64
import binascii
import contextlib
import hmac
import io
import json
import logging
import os
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone

from flask import Flask, g, has_request_context, jsonify, request, send_from_directory, url_for
from PIL import Image, UnidentifiedImageError


API_KEY_ENV = "DASHSCOPE_API_KEY"
MODEL_DIR_ENV = "QWEN_IMAGE_MODEL_DIR"
DEVICE_ENV = "QWEN_IMAGE_DEVICE"
SUPPORTED_MODELS_ENV = "QWEN_IMAGE_SUPPORTED_MODELS"
SKIP_INIT_ENV = "QWEN_IMAGE_SERVICE_SKIP_INIT"

#DEFAULT_MODEL_DIR = "/home1/zhanghui/models/Qwen/Qwen-Image-Edit-2511"
DEFAULT_MODEL_DIR = "/home1/zhanghui/models/FireRedTeam/FireRed-Image-Edit-1___1"
DEFAULT_SUPPORTED_MODELS = ("wan2.6-image", "Qwen-Image-Edit-2511")
DEFAULT_NEGATIVE_PROMPT = " "
DEFAULT_NUM_INFERENCE_STEPS = 40
DEFAULT_GUIDANCE_SCALE = 1.0
DEFAULT_TRUE_CFG_SCALE = 4.0
DEFAULT_IMAGE_COUNT = 1
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MIN_IMAGE_DIMENSION = 240
MAX_IMAGE_DIMENSION = 8000
MAX_INPUT_IMAGES = 4
OVERLOADED_MESSAGE = "API server is overloaded and cannot process new requests at this time."

OUTPUT_FOLDER = os.path.abspath(os.getenv("QWEN_IMAGE_OUTPUT_DIR", "outputs"))

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pipeline = None
pipeline_lock = threading.Lock()
service_ready = False
inference_lock = threading.Lock()
_torch_module = None


def configure_logger():
    logger = logging.getLogger("qwen_image_service")
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger


logger = configure_logger()


class ServiceError(Exception):
    def __init__(self, status_code, code, message, stage, log_event="request_failed", log_level="warning", **log_fields):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.stage = stage
        self.log_event = log_event
        self.log_level = log_level
        self.log_fields = log_fields


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_supported_models():
    raw_value = os.getenv(SUPPORTED_MODELS_ENV)
    if not raw_value:
        return set(DEFAULT_SUPPORTED_MODELS)
    return {item.strip() for item in raw_value.split(",") if item.strip()}


SUPPORTED_MODELS = get_supported_models()


def resolve_device():
    configured_device = os.getenv(DEVICE_ENV)
    if configured_device:
        return configured_device

    torch = get_torch()
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_torch():
    global _torch_module
    if _torch_module is None:
        import torch

        _torch_module = torch
    return _torch_module


def emit_log(level, event, request_id=None, **fields):
    payload = {
        "timestamp": utc_now_iso(),
        "level": level.upper(),
        "event": event,
    }

    if request_id:
        payload["request_id"] = request_id

    if has_request_context():
        payload.setdefault("path", request.path)
        payload.setdefault("method", request.method)
        payload.setdefault("client_ip", get_client_ip())

    for key, value in fields.items():
        if value is not None:
            payload[key] = value

    logger.log(getattr(logging, level.upper(), logging.INFO), json.dumps(payload, ensure_ascii=False, default=str))


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def get_request_id():
    if has_request_context() and hasattr(g, "request_id"):
        return g.request_id
    return uuid.uuid4().hex


def current_elapsed_ms():
    if has_request_context() and hasattr(g, "request_started_at"):
        return round((time.perf_counter() - g.request_started_at) * 1000, 2)
    return None


def make_json_response(payload, status_code):
    response = jsonify(payload)
    response.status_code = status_code
    response.headers["X-Request-Id"] = get_request_id()
    return response


def error_response(status_code, code, message, stage, log_event="request_failed", log_level="warning", **log_fields):
    request_id = get_request_id()
    emit_log(
        log_level,
        log_event,
        request_id,
        stage=stage,
        status_code=status_code,
        duration_ms=current_elapsed_ms(),
        **log_fields,
    )
    return make_json_response(
        {
            "request_id": request_id,
            "code": code,
            "message": message,
        },
        status_code,
    )


def ensure_service_ready():
    if not service_ready or pipeline is None:
        raise ServiceError(
            503,
            "api_error",
            "The image service is not ready.",
            "startup",
            log_level="error",
        )


def authenticate_request():
    expected_api_key = app.config.get("API_KEY", "")
    auth_header = request.headers.get("Authorization", "").strip()

    if not expected_api_key:
        raise ServiceError(
            500,
            "api_error",
            "The image service is not configured with an API key.",
            "auth",
            log_level="error",
        )

    if not auth_header:
        raise ServiceError(
            403,
            "authentication_error",
            "API key is missing or invalid.",
            "auth",
            log_event="auth_failed",
            reason="missing_authorization_header",
        )

    auth_scheme, _, token = auth_header.partition(" ")
    if auth_scheme.lower() != "bearer" or not token.strip():
        raise ServiceError(
            403,
            "authentication_error",
            "API key is missing or invalid.",
            "auth",
            log_event="auth_failed",
            reason="invalid_authorization_header",
        )

    if not hmac.compare_digest(token.strip(), expected_api_key):
        raise ServiceError(
            403,
            "authentication_error",
            "API key is missing or invalid.",
            "auth",
            log_event="auth_failed",
            reason="invalid_api_key",
        )

    emit_log("info", "auth_passed", get_request_id(), stage="auth")


def require_json_body():
    if not request.is_json:
        raise ServiceError(
            400,
            "invalid_request_error",
            "Content-Type must be application/json.",
            "validation",
            content_type=request.content_type,
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ServiceError(
            400,
            "invalid_request_error",
            "Request body must be a valid JSON object.",
            "validation",
        )
    return payload


def parse_int_parameter(parameters, key, default_value, minimum=None, maximum=None):
    value = parameters.get(key, default_value)
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ServiceError(
            400,
            "invalid_request_error",
            f"parameters.{key} must be an integer.",
            "validation",
        )

    if minimum is not None and value < minimum:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"parameters.{key} must be greater than or equal to {minimum}.",
            "validation",
        )
    if maximum is not None and value > maximum:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"parameters.{key} must be less than or equal to {maximum}.",
            "validation",
        )
    return value


def parse_float_parameter(parameters, key, default_value, minimum=None):
    value = parameters.get(key, default_value)
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ServiceError(
            400,
            "invalid_request_error",
            f"parameters.{key} must be a number.",
            "validation",
        )

    if minimum is not None and value < minimum:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"parameters.{key} must be greater than or equal to {minimum}.",
            "validation",
        )
    return value


def extract_prompt_and_images(input_payload):
    messages = input_payload.get("messages")
    if isinstance(messages, list) and messages:
        if len(messages) != 1:
            raise ServiceError(
                400,
                "invalid_request_error",
                "input.messages must contain exactly one user message.",
                "validation",
            )

        message = messages[0]
        if not isinstance(message, dict):
            raise ServiceError(
                400,
                "invalid_request_error",
                "input.messages[0] must be an object.",
                "validation",
            )

        if message.get("role") != "user":
            raise ServiceError(
                400,
                "invalid_request_error",
                "input.messages[0].role must be 'user'.",
                "validation",
            )

        content_items = message.get("content")
        if not isinstance(content_items, list) or not content_items:
            raise ServiceError(
                400,
                "invalid_request_error",
                "input.messages[0].content must be a non-empty array.",
                "validation",
            )

        prompt = None
        images = []
        for item in content_items:
            if not isinstance(item, dict):
                raise ServiceError(
                    400,
                    "invalid_request_error",
                    "Each content item must be an object.",
                    "validation",
                )

            if "text" in item:
                prompt = item["text"]
            if "image" in item:
                images.append(item["image"])

        return prompt, images

    prompt = input_payload.get("prompt")
    images = input_payload.get("images")
    if prompt is None and images is None:
        raise ServiceError(
            400,
            "invalid_request_error",
            "input.messages is required.",
            "validation",
        )

    return prompt, images


def parse_generation_request(payload):
    model = payload.get("model")
    if not isinstance(model, str) or not model.strip():
        raise ServiceError(
            400,
            "invalid_request_error",
            "model is required and must be a string.",
            "validation",
        )

    if model not in SUPPORTED_MODELS:
        raise ServiceError(
            404,
            "not_found_error",
            f"Model '{model}' is not supported by this service.",
            "validation",
            supported_models=sorted(SUPPORTED_MODELS),
        )

    input_payload = payload.get("input")
    if not isinstance(input_payload, dict):
        raise ServiceError(
            400,
            "invalid_request_error",
            "input must be an object.",
            "validation",
        )

    prompt, input_images = extract_prompt_and_images(input_payload)
    if not isinstance(prompt, str) or not prompt.strip():
        raise ServiceError(
            400,
            "invalid_request_error",
            "A non-empty text prompt is required.",
            "validation",
        )

    if not isinstance(input_images, list) or not input_images:
        raise ServiceError(
            400,
            "invalid_request_error",
            "At least one input image is required.",
            "validation",
        )

    if len(input_images) > MAX_INPUT_IMAGES:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"At most {MAX_INPUT_IMAGES} input images are supported.",
            "validation",
        )

    parameters = payload.get("parameters") or {}
    if not isinstance(parameters, dict):
        raise ServiceError(
            400,
            "invalid_request_error",
            "parameters must be an object.",
            "validation",
        )

    if parameters.get("stream") is True:
        raise ServiceError(
            400,
            "invalid_request_error",
            "stream=true is not supported by this local deployment.",
            "validation",
        )

    if parameters.get("enable_interleave") is True:
        raise ServiceError(
            400,
            "invalid_request_error",
            "enable_interleave=true is not supported by this local deployment.",
            "validation",
        )

    generation_config = {
        "negative_prompt": str(parameters.get("negative_prompt", DEFAULT_NEGATIVE_PROMPT)),
        "num_inference_steps": parse_int_parameter(parameters, "num_inference_steps", DEFAULT_NUM_INFERENCE_STEPS, minimum=1),
        "guidance_scale": parse_float_parameter(parameters, "guidance_scale", DEFAULT_GUIDANCE_SCALE, minimum=0.0),
        "true_cfg_scale": parse_float_parameter(parameters, "true_cfg_scale", DEFAULT_TRUE_CFG_SCALE, minimum=0.0),
        "n": parse_int_parameter(parameters, "n", DEFAULT_IMAGE_COUNT, minimum=1, maximum=4),
        "seed": parse_int_parameter(
            parameters,
            "seed",
            int(time.time_ns() % 2147483647),
            minimum=0,
            maximum=2147483647,
        ),
    }

    return {
        "model": model,
        "prompt": prompt.strip(),
        "input_images": input_images,
        "parameters": parameters,
        "generation_config": generation_config,
    }


def decode_image_value(image_value, index):
    if not isinstance(image_value, str) or not image_value.strip():
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} must be a non-empty string.",
            "validation",
        )

    image_value = image_value.strip()

    if image_value.startswith("http://") or image_value.startswith("https://"):
        raise ServiceError(
            400,
            "invalid_request_error",
            "Remote image URLs are not supported by this local deployment. Use a base64 string or data URL.",
            "validation",
        )

    if image_value.startswith("data:"):
        _, separator, encoded_payload = image_value.partition(",")
        if not separator:
            raise ServiceError(
                400,
                "invalid_request_error",
                f"input image #{index} is not a valid data URL.",
                "validation",
            )
    else:
        encoded_payload = image_value

    try:
        image_bytes = base64.b64decode(encoded_payload, validate=True)
    except (binascii.Error, ValueError):
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} is not valid base64 data.",
            "validation",
        )

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} exceeds the {MAX_IMAGE_BYTES} byte limit.",
            "validation",
        )

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} is not a supported image file.",
            "validation",
        )

    if image.width < MIN_IMAGE_DIMENSION or image.height < MIN_IMAGE_DIMENSION:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} must be at least {MIN_IMAGE_DIMENSION}px on each side.",
            "validation",
        )

    if image.width > MAX_IMAGE_DIMENSION or image.height > MAX_IMAGE_DIMENSION:
        raise ServiceError(
            400,
            "invalid_request_error",
            f"input image #{index} must be at most {MAX_IMAGE_DIMENSION}px on each side.",
            "validation",
        )

    return image.convert("RGB"), len(image_bytes)


def decode_input_images(input_images):
    decoded_images = []
    total_bytes = 0

    for index, image_value in enumerate(input_images, start=1):
        decoded_image, image_size = decode_image_value(image_value, index)
        decoded_images.append(decoded_image)
        total_bytes += image_size

    return decoded_images, total_bytes


def build_generator(seed):
    try:
        torch = get_torch()
    except ModuleNotFoundError:
        return None

    device = app.config.get("MODEL_DEVICE", "cpu")
    generator_device = "cuda" if str(device).startswith("cuda") else "cpu"
    return torch.Generator(device=generator_device).manual_seed(seed)


@contextlib.contextmanager
def inference_mode():
    try:
        torch = get_torch()
    except ModuleNotFoundError:
        yield
        return

    with torch.inference_mode():
        yield


def run_inference(prompt, input_images, generation_config):
    ensure_service_ready()

    pipeline_inputs = {
        "image": input_images,
        "prompt": prompt,
        "generator": build_generator(generation_config["seed"]),
        "true_cfg_scale": generation_config["true_cfg_scale"],
        "negative_prompt": generation_config["negative_prompt"],
        "num_inference_steps": generation_config["num_inference_steps"],
        "guidance_scale": generation_config["guidance_scale"],
        "num_images_per_prompt": generation_config["n"],
    }

    with inference_mode():
        output = pipeline(**pipeline_inputs)

    output_images = getattr(output, "images", None)
    if not output_images:
        raise RuntimeError("The model pipeline returned no images.")

    return output_images


def save_output_images(output_images):
    image_urls = []
    output_filenames = []
    image_size = None

    for index, image in enumerate(output_images, start=1):
        if image_size is None:
            image_size = f"{image.width}*{image.height}"

        filename = f"{get_request_id()}_{index}.png"
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        image.save(file_path)

        output_filenames.append(filename)
        image_urls.append(url_for("get_output_file", filename=filename, _external=True))

    return image_urls, output_filenames, image_size


def build_success_response(model, image_urls, image_size):
    content = [{"type": "image", "image": image_url} for image_url in image_urls]
    return {
        "request_id": get_request_id(),
        "output": {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                }
            ],
            "finished": True,
        },
        "usage": {
            "image_count": len(image_urls),
            "size": image_size,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
        "model": model,
    }


def build_health_response():
    configured_model_dir = app.config.get("MODEL_DIR") or os.getenv(MODEL_DIR_ENV, DEFAULT_MODEL_DIR)
    configured_device = app.config.get("MODEL_DEVICE") or os.getenv(DEVICE_ENV) or "auto"

    return {
        "status": "ok" if service_ready and pipeline is not None else "starting",
        "ready": service_ready and pipeline is not None,
        "model": {
            "model_dir": configured_model_dir,
            "device": configured_device,
            "supported_models": sorted(SUPPORTED_MODELS),
        },
    }


def load_pipeline(model_dir, device):
    torch = get_torch()
    from diffusers import QwenImageEditPlusPipeline

    torch_dtype = torch.bfloat16 if str(device).startswith("cuda") else torch.float32

    emit_log("info", "model_loading_started", model_dir=model_dir, device=device)
    loaded_pipeline = QwenImageEditPlusPipeline.from_pretrained(model_dir, torch_dtype=torch_dtype)
    loaded_pipeline.to(device)
    loaded_pipeline.set_progress_bar_config(disable=True)
    emit_log("info", "model_loading_finished", model_dir=model_dir, device=device)
    return loaded_pipeline


def warmup_pipeline():
    emit_log("info", "model_warmup_started", device=app.config.get("MODEL_DEVICE"))

    warmup_image = Image.new("RGB", (512, 512), color="white")
    warmup_prompt = "Warm up the local image editing pipeline."
    warmup_config = {
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "num_inference_steps": 1,
        "guidance_scale": DEFAULT_GUIDANCE_SCALE,
        "true_cfg_scale": DEFAULT_TRUE_CFG_SCALE,
        "n": 1,
        "seed": 0,
    }

    run_inference(warmup_prompt, [warmup_image], warmup_config)
    emit_log("info", "model_warmup_finished", device=app.config.get("MODEL_DEVICE"))


def initialize_service():
    global pipeline, service_ready

    with pipeline_lock:
        if service_ready and pipeline is not None:
            return

        api_key = os.getenv(API_KEY_ENV)
        if not api_key:
            raise RuntimeError(f"{API_KEY_ENV} is required before starting the service.")

        model_dir = os.getenv(MODEL_DIR_ENV, DEFAULT_MODEL_DIR)
        device = resolve_device()

        app.config["API_KEY"] = api_key
        app.config["MODEL_DIR"] = model_dir
        app.config["MODEL_DEVICE"] = device

        emit_log(
            "info",
            "service_initializing",
            model_dir=model_dir,
            device=device,
            supported_models=sorted(SUPPORTED_MODELS),
        )

        try:
            pipeline = load_pipeline(model_dir, device)
            service_ready = True
            warmup_pipeline()
        except Exception:
            service_ready = False
            pipeline = None
            emit_log(
                "error",
                "service_initialization_failed",
                model_dir=model_dir,
                device=device,
                error_type=sys.exc_info()[0].__name__ if sys.exc_info()[0] else "UnknownError",
                error_message=str(sys.exc_info()[1]),
                traceback=traceback.format_exc(),
            )
            raise

        emit_log("info", "service_ready", model_dir=model_dir, device=device)


@app.before_request
def attach_request_context():
    g.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
    g.request_started_at = time.perf_counter()


@app.after_request
def inject_request_id(response):
    if hasattr(g, "request_id"):
        response.headers["X-Request-Id"] = g.request_id
    return response


@app.route("/outputs/<path:filename>", methods=["GET"])
def get_output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/health", methods=["GET"])
def health_check():
    response_payload = build_health_response()
    status_code = 200 if response_payload["ready"] else 503
    return make_json_response(response_payload, status_code)


@app.route("/generation", methods=["POST"])
def generate_image():
    emit_log(
        "info",
        "request_started",
        get_request_id(),
        content_type=request.content_type,
        accept=request.headers.get("Accept"),
    )

    lock_acquired = False
    decoded_images = []

    try:
        authenticate_request()

        lock_acquired = inference_lock.acquire(blocking=False)
        if not lock_acquired:
            return error_response(
                529,
                "overloaded_error",
                OVERLOADED_MESSAGE,
                "concurrency_guard",
                log_event="request_rejected_busy",
                retryable=True,
            )

        payload = require_json_body()
        generation_request = parse_generation_request(payload)

        decode_started_at = time.perf_counter()
        decoded_images, image_bytes = decode_input_images(generation_request["input_images"])
        decode_ms = round((time.perf_counter() - decode_started_at) * 1000, 2)

        emit_log(
            "info",
            "request_validated",
            get_request_id(),
            stage="validation",
            model=generation_request["model"],
            parameter_keys=sorted(generation_request["parameters"].keys()),
            prompt_length=len(generation_request["prompt"]),
            image_count=len(decoded_images),
            image_bytes=image_bytes,
            decode_ms=decode_ms,
        )

        emit_log(
            "info",
            "inference_started",
            get_request_id(),
            model=generation_request["model"],
            prompt_length=len(generation_request["prompt"]),
            image_count=len(decoded_images),
        )

        inference_started_at = time.perf_counter()
        output_images = run_inference(
            generation_request["prompt"],
            decoded_images,
            generation_request["generation_config"],
        )
        inference_ms = round((time.perf_counter() - inference_started_at) * 1000, 2)

        emit_log(
            "info",
            "inference_finished",
            get_request_id(),
            model=generation_request["model"],
            inference_ms=inference_ms,
            output_count=len(output_images),
        )

        save_started_at = time.perf_counter()
        image_urls, output_filenames, image_size = save_output_images(output_images)
        save_output_ms = round((time.perf_counter() - save_started_at) * 1000, 2)

        response_payload = build_success_response(generation_request["model"], image_urls, image_size)

        emit_log(
            "info",
            "request_succeeded",
            get_request_id(),
            status_code=200,
            duration_ms=current_elapsed_ms(),
            model=generation_request["model"],
            parameter_keys=sorted(generation_request["parameters"].keys()),
            prompt_length=len(generation_request["prompt"]),
            image_count=len(decoded_images),
            image_bytes=image_bytes,
            inference_ms=inference_ms,
            save_output_ms=save_output_ms,
            output_filenames=output_filenames,
        )
        return make_json_response(response_payload, 200)

    except ServiceError as exc:
        return error_response(
            exc.status_code,
            exc.code,
            exc.message,
            exc.stage,
            log_event=exc.log_event,
            log_level=exc.log_level,
            **exc.log_fields,
        )
    except Exception as exc:
        return error_response(
            500,
            "api_error",
            "An internal server error occurred. Please try again later.",
            "inference",
            log_level="error",
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            traceback=traceback.format_exc(),
        )
    finally:
        for image in decoded_images:
            with contextlib.suppress(Exception):
                image.close()

        if lock_acquired:
            inference_lock.release()


def auto_initialize_service():
    if os.getenv(SKIP_INIT_ENV, "0").lower() in {"1", "true", "yes"}:
        return
    initialize_service()


if __name__ == "__main__":
    auto_initialize_service()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False, use_reloader=False, threaded=True)
else:
    auto_initialize_service()

