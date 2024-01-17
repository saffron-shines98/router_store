from flask import request
from functools import wraps
from app.common_utils import render_error_response
from app.exceptions import AuthMissing, InvalidAuth, CustomrAlreadyExist, AlreadyExists, InvalidDateFormat
from jsonschema import validate, ValidationError, FormatChecker, SchemaError
from config import Config


def validate_params(param_config=None, token_required=True):

    def deco(func):

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
                stack_trace_params = {'endpoint': str(request.url_rule)}
                validate(params, param_config, format_checker=FormatChecker())
                return func(params=params, headers=headers, *args, **kwargs)
            except (ValidationError, SchemaError) as e:
                return render_error_response('Invalid Input Fields', 400, stack_trace_params, params, headers)
            except AuthMissing as e:
                return render_error_response(e.message, e.http_code, stack_trace_params, params, headers)
            except InvalidAuth as e:
                return render_error_response(e.message, e.http_code, stack_trace_params, params, headers)
            except CustomrAlreadyExist as e:
                return render_error_response(e.message, e.http_code, stack_trace_params, params, headers)
            except AlreadyExists as e:
                return render_error_response(e.message, e.http_code, stack_trace_params, params, headers)
            except InvalidDateFormat as e:
                return render_error_response(e.message, e.http_code, stack_trace_params, params, headers)
            except Exception as e:
                return render_error_response(str(e), 400, stack_trace_params, params, headers)
        return decorated_function

    return deco
