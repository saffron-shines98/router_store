from flask import Flask, request
from app.retail.v1.urls import v1
from config import Config
from app.common_utils import render_error_response
import json


app = Flask(__name__)

VERSION_OBJECT_MAPPING = {
    '1': v1
}

def get_url_prefix(version):
    return '/api/v{version_number}'.format(version_number=str(version))

def register_versions(allowed_versions):
    for version in allowed_versions:
        app.register_blueprint(
            VERSION_OBJECT_MAPPING[version], url_prefix=get_url_prefix(version)
        )


