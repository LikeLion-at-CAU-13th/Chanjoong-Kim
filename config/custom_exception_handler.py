from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail, ValidationError
from .custom_api_exceptions import PostValidationException, DailyPostLimitException

def custom_exception_handler(exc, context):
    print(f"Exception occurred: {type(exc).__name__}: {exc}")  # 디버깅용
    response = exception_handler(exc, context)

    if response is not None:
        print(f"Response status: {response.status_code}")  # 디버깅용
        print(f"Response data: {response.data}")  # 디버깅용
        
        # DailyPostLimitException 특별 처리
        if isinstance(exc, DailyPostLimitException):
            print("Handling DailyPostLimitException")  # 디버깅용
            response.data = _create_daily_limit_error_response(exc, response)
        # ValidationError인 경우 특별 처리
        elif isinstance(exc, ValidationError):
            print("Handling ValidationError")  # 디버깅용
            response.data = _create_validation_error_response(exc, response)
        else:
            print("Handling other error")  # 디버깅용
            response.data = _create_unified_response(response)

    return response

def _create_validation_error_response(exc, response):
    """ValidationError에 대한 상세한 응답을 생성합니다."""
    field_errors = {}
    error_messages = []
    
    if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
        for field, errors in exc.detail.items():
            field_errors[field] = []
            if isinstance(errors, list):
                for error in errors:
                    error_msg = str(error)
                    field_errors[field].append(error_msg)
                    error_messages.append(f"{field}: {error_msg}")
            else:
                error_msg = str(errors)
                field_errors[field].append(error_msg)
                error_messages.append(f"{field}: {error_msg}")
    
    # 한국어 필드명 매핑
    field_name_mapping = {
        'title': '제목',
        'content': '내용',
        'status': '상태',
        'user': '사용자',
        'image': '이미지',
        'category': '카테고리',
        'author': '작성자',
        'body': '댓글 내용',
        'post': '게시글',
        'c_id': '댓글 ID'
    }
    
    # 필드명을 한국어로 변환
    korean_error_messages = []
    korean_field_errors = {}
    
    for field, errors in field_errors.items():
        korean_field = field_name_mapping.get(field, field)
        korean_field_errors[korean_field] = errors
        for error in errors:
            korean_error_messages.append(f"{korean_field}: {error}")
    
    return {
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': f"입력값 검증에 실패했습니다. ({len(korean_error_messages)}개의 오류)",
            'status_code': response.status_code,
            'details': {
                'field_errors': korean_field_errors,
                'error_summary': korean_error_messages,
                'total_errors': len(korean_error_messages)
            }
        }
    }

def _create_unified_response(response):
    error_detail = _extract_error_detail(response.data)

    return {
        'success': False,
        'error': {
            'code': error_detail.get('code', 'DRF-API-ERROR'),
            'message': error_detail.get('message', 'An error occurred.'),
            'status_code': response.status_code,
        }
    }

def _extract_error_detail(error_data):
    print(f"Extracting error detail from: {error_data}")
    if isinstance(error_data, str):
        return {
            'message': error_data,
            'code': 'api_error'
        }
    
    if isinstance(error_data, list) and error_data:
        first_error = error_data[0]
        if isinstance(first_error, str):
            return {
                'message': first_error, 
                'code': 'validation_error'
            }
        elif isinstance(first_error, dict):
            return _extract_error_detail(first_error)
        
    if isinstance(error_data, ErrorDetail):
        return {
            'message': str(error_data),
            'code': getattr(error_data, 'code', 'unknown_error')
        }
    
    if isinstance(error_data, dict):
        if 'message' in error_data and 'code' in error_data:
            return error_data
        
        if 'detail' in error_data:
            return {
                'message': str(error_data['detail']),
                'code': getattr(error_data['detail'], 'code', 'unknown_error')
            }
        
        field_errors = []
        for field, messages in error_data.items():
            if isinstance(messages, list) and messages:
                field_errors.append(f"{field}: {messages[0]}")
            else:
                field_errors.append(f"{field}: {str(messages)}")
        
        if field_errors:
            return {
                'message': f"{len(field_errors)} validation errors occurred",
                'code': 'validation_error',
                'errors': field_errors,
                'field_details': error_data
            }
    
    return {
        'message': str(error_data),
        'code': 'unknown_error'
    }

def _create_daily_limit_error_response(exc, response):
    """DailyPostLimitException에 대한 상세한 응답을 생성합니다."""
    return {
        'success': False,
        'error': {
            'code': 'DAILY_POST_LIMIT_EXCEEDED',
            'message': str(exc.detail),
            'status_code': response.status_code,
            'details': {
                'limit_type': '일일 게시글 작성 제한',
                'max_posts_per_day': 1,
                'user': getattr(exc, 'user', None),
                'reset_time': '내일 00:00 (자정)',
                'suggestion': '내일 다시 시도해주세요!'
            }
        }
    }
# This code is a custom exception handler for Django REST Framework (DRF).
# It overrides the default exception handling to provide a unified error response format.