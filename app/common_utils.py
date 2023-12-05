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
import re
import hashlib
import collections
from time import time
import pysodium as nacl
from hashlib import blake2b
from app.base_coordinator import BaseCoordinator,SSOCoordinator, SSOCoordinatorV1
from jsonschema import validate, ValidationError, FormatChecker, SchemaError
from config import Config
from app.exceptions import InvalidAuth


def render_error_response(msg, status=None) -> Response:
    status = 500 if not status else status
    body = {'error': msg}
    return Response(json.dumps(body), status, content_type='application/json')


def render_success_response(response, msg='', status=1) -> Response:
    body = {
        'api_action_status': 'success'
    }
    return Response(json.dumps(body), status=200, content_type='application/json')

def render_success_response_with_body(response, msg='', status=1) -> Response:
    body = {
        'api_action_status': msg if msg else 'success'
    }
    if response:
        body.update(response)
    return Response(json.dumps(body), status=200, content_type='application/json')

def validate_request_payload(payload, schema):
    try:
        validate(payload, schema, format_checker=FormatChecker())
    except (ValidationError, SchemaError) as e:
        raise Exception('Invalid params')


def get_current_datetime() -> str:
    return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")


def decrypt_jwt(public_pem, jwt_token):
    public_key = serialization.load_pem_public_key(public_pem.encode(), backend=default_backend())
    try:
        decoded_data = jwt.decode(jwt_token, public_key, algorithms='RS256')
        return decoded_data
    except jwt.InvalidTokenError as e:
        # return dict()
        raise Exception(str(e))


def encrypt_jwt(data):
    private_key_start, private_key_end = '-----BEGIN PRIVATE KEY-----', '-----END PRIVATE KEY-----'
    privat_key = Config.PRIVATE_KEY.replace('\n', '').replace('\t', '').replace(private_key_start,private_key_start + '\n').replace(private_key_end,'\n' + private_key_end)
    private_key=serialization.load_pem_private_key(privat_key.encode(), password=None, backend=default_backend())
    if not private_key:
        raise Exception('Private key not found')
    payload={
        "data" : data
    }
    encrypted_data= jwt.encode(payload,private_key, algorithm = "RS256")
    status = 1 if encrypted_data else 0
    return encrypted_data
    

def get_modified_ondc_signing_string(payload, created=None, expires=None):
    h = blake2b()
    h.update(payload.encode('utf-8'))
    data = h.hexdigest()
    base64_hash = base64.b64encode(bytes.fromhex(data)).decode()
    if not created:
        created = int(time())
    if not expires:
        expires = created + 2 * 24 * 3600
    return '''(created): {}\n(expires): {}\ndigest: BLAKE-512={}'''.format(created, expires,  base64_hash), created, expires


def sign_message(signing_message, private_key):
    signed_message = nacl.crypto_sign_detached(signing_message.encode('utf-8'), base64.b64decode(private_key))
    return base64.b64encode(signed_message).decode()


def get_authorization_header(payload, nodesso_details):
    signing_string, created, expires = get_modified_ondc_signing_string(payload)
    signature = sign_message(signing_string, nodesso_details.get('private_key'))
    header_params = {'subscriber_id': nodesso_details.get('subsciber_id'), 'unique_key_id': nodesso_details.get('ukid'),
        'created': created, 'expires': expires, 'signature': signature}
    return '''Signature keyId="{subscriber_id}|{unique_key_id}|ed25519",algorithm="ed25519",created="{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'''.format(**header_params)


def get_filter_dictionary_or_operation(filter_string):
    filter_string_list = re.split(',', filter_string)
    filter_string_list = [x.strip(' ') for x in filter_string_list]  # to remove white spaces from list
    filter_dictionary_or_operation = dict()
    for fs in filter_string_list:
        splits = fs.split('=', maxsplit=1)
        key = splits[0].strip()
        value = splits[1].strip()
        if key == 'keyId':
            value = value.replace("\"", "").strip('\\').split('|')
            filter_dictionary_or_operation['subscriber_id'] = value[0]
            filter_dictionary_or_operation['ukid'] = value[1]
        else:
            filter_dictionary_or_operation[key] = value.replace("\"", "").strip('\\')
    return filter_dictionary_or_operation


def verify_auth_header(payload, signature_string, public_key):
    header_params = get_filter_dictionary_or_operation(signature_string.replace("Signature ", ""))
    request_signing_string, created, expires = get_modified_ondc_signing_string(payload, header_params.get('created'), header_params.get('expires'))
    try:
        nacl.crypto_sign_verify_detached(base64.b64decode(header_params.get('signature')), request_signing_string.encode('utf-8'),
            base64.b64decode(public_key))
        return True
    except Exception as e:
        print(e, 'e')
        return False

def validate_jwt(payload):
    response = SSOCoordinator().post('/verifyHeader', payload=payload, headers={'Authorization': Config.Authorization})
    if response.status_code == 200:
        return response.json().get('d')
    raise InvalidAuth('Invalid auth token.')

def validate_jwt_though_auth1(payload):
    response = SSOCoordinatorV1().post('/verifyHeader', payload=payload, headers={'Authorization': Config.Authorization})
    if response.status_code == 200:
        return response.json().get('d')
    raise InvalidAuth('Invalid auth token.')

def clean_string(string):
    if string is not None:
        trimmed_string = string.strip()
        cleaned_string = re.sub(r'\s+', ' ', trimmed_string)
        cleaned_string = cleaned_string.replace("'", '').replace("\r", ' ').replace("\n", ' ')
        return cleaned_string
    else:
        return None

def get_hash_from_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def get_hash_lookup_key(db_params, key):
    post_params_str = str(collections.OrderedDict(db_params))
    return key + get_hash_from_text(post_params_str)
