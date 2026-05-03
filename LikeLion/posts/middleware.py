import logging

logger = logging.getLogger('request_logger')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 서버로 들어오는 모든 http 요청 로깅 (응답 처리 전)
        response = self.get_response(request)

        # 요청 URL과 HTTP 메서드, 응답 상태 코드를 문자열로 치환
        request_url = request.get_full_path()
        method = request.method
        status_code = response.status_code

        log_message = f"Method: {method} | URL: {request_url} | Status: {status_code}"

        # 상태 코드에 따라 로그 레벨 다르게 지정

        if status_code >= 500:
            # 500번대 (서버 내부 에러) -> ERROR 레벨 
            # (file_all, file_errors 핸들러 모두 기록)
            logger.error(log_message)
        elif status_code >= 400:
            # 400번대 (클라이언트 요청 에러) -> WARNING 레벨
            # (file_all, file_errors 핸들러 모두 기록)
            logger.warning(log_message)
        else:
            # 200~300번대 (정상 처리) -> INFO 레벨
            # (file_all 핸들러에만 기록)
            logger.info(log_message)

        return response