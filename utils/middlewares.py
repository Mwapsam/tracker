import json
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_body_length = 1024 * 1024
        self.filter_func = None

    def __call__(self, request):
        if self.filter_func is None:
            return self._log_request(request)
        else:
            return (
                self._log_request(request)
                if self.filter_func(request)
                else self.get_response(request)
            )

    def _log_request(self, request):
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Request Headers: {request.META}")

        if not request.body:
            logger.info(f"Request Body: None")
        else:
            content_type = request.META.get("CONTENT_TYPE", "")
            if content_type.startswith("application/json"):
                try:
                    json_body = json.loads(request.body.decode("utf-8"))
                    if "query" in json_body:
                        logger.info(f"GraphQL Request: {json_body['query']}")
                    else:
                        logger.info(f"Request Body (JSON): {json_body}")
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON request body")

        response = self.get_response(request)

        logger.info(f"Response: {response.status_code}")

        return response
