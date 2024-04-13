from flask import Blueprint
from app.retail.v1.cart import views as router_views

v1 = Blueprint('v1', __name__)


router_prefix ='/router'
v1.add_url_rule(router_prefix + '/config', view_func=router_views.RouterConfig.as_view('router_config'))

