from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response, render_success_response_with_body
from app.retail.v1.cart.service import CartService


class Cartcreate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response_data = CartService(params, headers).cart_create()
        return render_success_response_with_body(response_data, msg='success')

class Cartupdate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response_data = CartService(params, headers).cart_update()
        return render_success_response_with_body(response_data, msg='success')