import json
from flask import Response
from jsonschema import validate, ValidationError, FormatChecker, SchemaError



def render_error_response(response, msg='', status=1) -> Response:
    body = {
        'api_action_status': 'failed_500'
    }
    return Response(json.dumps(body), status=500, content_type='application/json')


def render_success_response(response,  msg='', status=1) -> Response:
    body = {
        'api_action_status': 'success_200',
        's': status,
        'm': msg,
        'd': response
    }
    return Response(json.dumps(body), status=200, content_type='application/json')



def validate_request_payload(payload, schema):
    try:
        validate(payload, schema, format_checker=FormatChecker())
    except (ValidationError, SchemaError) as e:
        raise Exception('Invalid params')


