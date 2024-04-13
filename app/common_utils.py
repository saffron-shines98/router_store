import json
from config import Config
import pytz
from copy import deepcopy
from flask import Response
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt
import base64
import traceback
import re
from time import time
# import pysodium as nacl
from hashlib import blake2b
# from app.base_coordinator import BaseCoordinator,SSOCoordinator, SSOCoordinatorV1
from jsonschema import validate, ValidationError, FormatChecker, SchemaError
from config import Config
from app.exceptions import InvalidAuth, AuthMissing




def render_error_response(response, msg='', status=1) -> Response:
    body = {
        'api_action_status': 'failed_500'
    }
    return Response(json.dumps(body), status=500, content_type='application/json')


def render_success_response(response, msg='', status=1) -> Response:
    body = {
        'api_action_status': 'success_200'
    }
    return Response(json.dumps(body), status=200, content_type='application/json')



def validate_request_payload(payload, schema):
    try:
        validate(payload, schema, format_checker=FormatChecker())
    except (ValidationError, SchemaError) as e:
        raise Exception('Invalid params')


def get_current_datetime() -> str:
    return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")



def clean_string(string):
    if string is not None:
        trimmed_string = string.strip()
        cleaned_string = re.sub(r'\s+', ' ', trimmed_string)
        cleaned_string = cleaned_string.replace("'", '').replace("\r", ' ').replace("\n", ' ')
        return cleaned_string
    else:
        return None