from flask import Blueprint
from app.retail.v1.order import views as status_views

v1 = Blueprint('v1', __name__)


order_prefix = '/order'
v1.add_url_rule(order_prefix + '/status/update', view_func=status_views.StatusUpdate.as_view('status_update'))
v1.add_url_rule(order_prefix + '/create', view_func=status_views.OrderCreate.as_view('order_create'))


customer_prefix = '/customer'
v1.add_url_rule(customer_prefix + '/status/create', view_func=status_views.CustomerStatusCreate.as_view('customer_status_create'))