from flask import Flask, request
from app.retail.v1.urls import v1
from config import Config
from app.common_utils import render_error_response
import json
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

def register_versions():
    app.register_blueprint(v1)


