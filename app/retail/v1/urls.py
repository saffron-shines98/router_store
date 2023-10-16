from flask import Blueprint
from app import views as route_view

v1 = Blueprint('v1', __name__)


v1.add_url_rule('/sso-login', view_func=route_view.Login.as_view('login'))
v1.add_url_rule('/sso-sign', view_func=route_view.EncryptRequest.as_view('sign_encrypt_request'))
v1.add_url_rule('/create-client', view_func=route_view.CreateClient.as_view('create_client'))
v1.add_url_rule('/create-service', view_func=route_view.CreateService.as_view('create_service'))
v1.add_url_rule('/list-clients', view_func=route_view.ListClients.as_view('list_clients'))
v1.add_url_rule('/list-services', view_func=route_view.ListServices.as_view('list_services'))

v1.add_url_rule('/generate-header', view_func=route_view.GenerateHeader.as_view('generate_header'))
v1.add_url_rule('/verify-header', view_func=route_view.VerifyHeader.as_view('verify_header'))