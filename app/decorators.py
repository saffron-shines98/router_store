from flask import request
from functools import wraps
from app.common_utils import render_error_response
from jsonschema import validate, ValidationError, FormatChecker, SchemaError
from config import Config


def validate_params(param_config=None, token_required=True):

    def deco(func):

        def is_token_verified():
            if not request.headers.get('Authorization'):
                return False
            elif request.headers.get('Authorization') == Config.API_ACCESS_KEY:
                return True
            elif not request.headers.get('user_id'):
                return False
            else:
                redis_conn = Config.REDIS_CONN
                return redis_conn.get(request.headers.get('Authorization')) == request.headers.get('user_id')

        def extract_params(request):
            if request.method == 'POST':
                if request.content_type == 'application/x-www-form-urlencoded':
                    params = request.form
                elif 'multipart/form-data' in request.content_type:
                    params = request
                else:
                    params = request.get_json()
                return params
            else:
                params = request.args
                parsed_params = dict()
                for key, val in dict(params).items():
                    if isinstance(val, list) and val:
                        parsed_params.update({key: val[0]})
                    else:
                        parsed_params.update({key: val})
                return parsed_params

        def extract_headers(request):
            return dict(request.headers)

        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                params = extract_params(request)
                headers = extract_headers(request)
                validate(params, param_config, format_checker=FormatChecker())
                if (not token_required) or is_token_verified():
                    return func(params=params, headers=headers, *args, **kwargs)
                else:
                    return render_error_response('Invalid Token', 401)
            except Exception as e:
                return render_error_response(str(e), 500)
        return decorated_function

    return deco
