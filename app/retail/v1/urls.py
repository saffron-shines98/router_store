from flask import Blueprint
from app import views as route_view

v1 = Blueprint('v1', __name__)


order_prefix = 'order'
v1.add_url_rule(order_prefix + '/status/update', view_func=route_view.StatusUpdate.as_view('status_update'))