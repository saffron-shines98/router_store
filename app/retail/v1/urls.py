from flask import Blueprint
from app.retail.v1.order import views as status_views

v1 = Blueprint('v1', __name__)


order_prefix = '/order'
v1.add_url_rule(order_prefix + '/status/update', view_func=status_views.StatusUpdate.as_view('status_update'))