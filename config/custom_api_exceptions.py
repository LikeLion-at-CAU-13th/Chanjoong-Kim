from rest_framework.exceptions import APIException

class BaseCustomAPIException(APIException):
    status_code = 500
    default_detail = "An unexpected error occurred."
    default_code = "UNEXPECTED-ERROR"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        
        if code is None:
            code = self.default_code
        
        super().__init__(detail=detail, code=code)

class ConflictException(BaseCustomAPIException):
    status_code = 409
    default_detail = "A conflict occurred."
    default_code = "CONFLICT"

class PostConflictException(ConflictException):
    default_detail = "A conflict occurred with the post."
    default_code = "POST-CONFLICT"

class ValidationErrorException(BaseCustomAPIException):
    status_code = 400
    default_detail = "Validation failed."
    default_code = "VALIDATION_ERROR"

class PostValidationException(ValidationErrorException):
    default_detail = "Post validation failed."
    default_code = "POST_VALIDATION_ERROR"
    
    def __init__(self, field_errors=None, detail=None, code=None):
        if field_errors:
            # 필드별 에러 메시지를 생성
            error_messages = []
            for field, errors in field_errors.items():
                if isinstance(errors, list):
                    error_messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
                else:
                    error_messages.append(f"{field}: {str(errors)}")
            
            detail = f"다음 필드에 오류가 있습니다: {'; '.join(error_messages)}"
        
        super().__init__(detail=detail, code=code)
        self.field_errors = field_errors or {}

class RequiredFieldException(ValidationErrorException):
    default_detail = "Required field is missing."
    default_code = "REQUIRED_FIELD_ERROR"
    
    def __init__(self, field_name=None, detail=None, code=None):
        if field_name and detail is None:
            detail = f"'{field_name}' 필드는 필수입니다."
        
        super().__init__(detail=detail, code=code)
        self.field_name = field_name

class CommentValidationException(ValidationErrorException):
    default_detail = "Comment validation failed."
    default_code = "COMMENT_VALIDATION_ERROR"
    
    def __init__(self, field_errors=None, detail=None, code=None):
        if field_errors:
            # 필드별 에러 메시지를 생성
            error_messages = []
            for field, errors in field_errors.items():
                if isinstance(errors, list):
                    error_messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
                else:
                    error_messages.append(f"{field}: {str(errors)}")
            
            detail = f"댓글 작성 중 오류가 발생했습니다: {'; '.join(error_messages)}"
        
        super().__init__(detail=detail, code=code)
        self.field_errors = field_errors or {}

class DailyPostLimitException(BaseCustomAPIException):
    status_code = 429  # Too Many Requests
    default_detail = "일일 게시글 작성 제한에 도달했습니다."
    default_code = "DAILY_POST_LIMIT_EXCEEDED"
    
    def __init__(self, user=None, detail=None, code=None):
        if user and detail is None:
            detail = f"'{user}'님은 오늘 이미 게시글을 작성하셨습니다. 하루에 하나의 게시글만 작성할 수 있습니다."
        
        super().__init__(detail=detail, code=code)
        self.user = user