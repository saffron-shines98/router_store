from flask import request
from functools import wraps
from app.common_utils import render_error_response
from app.exceptions import AuthMissing, InvalidAuth, CustomrAlreadyExist, AlreadyExists
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
                validate(params, param_config, format_checker=FormatChecker())
                return func(params=params, headers=headers, *args, **kwargs)
            except (ValidationError, SchemaError) as e:
                return render_error_response('Invalid Input Fields', 400)
            except AuthMissing as e:
                return render_error_response(e.message, e.http_code)
            except InvalidAuth as e:
                return render_error_response(e.message, e.http_code)
            except CustomrAlreadyExist as e:
                return render_error_response(e.message, e.http_code)
            except AlreadyExists as e:
                return render_error_response(e.message, e.http_code)
            except Exception as e:
                return render_error_response('Something went wrong. Please try again later.', 500)
        return decorated_function

    return deco
