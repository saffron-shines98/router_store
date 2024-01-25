from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response, render_success_response_with_body
from app.retail.v1.order.service import OrderService

class StatusUpdate(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'node_instance_id': {
                'type': 'number'
            }
        }
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).update_order_status()
        return render_success_response(response, msg='success')


class CustomerStatusCreate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).customer_status_create()
        return render_success_response(response, msg='success')
    

class OrderCreate(MethodView):
    
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).order_create()
        return render_success_response(response, msg='success')

class OrderFetch(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).order_fetch()
        return render_success_response_with_body(response, msg='success')
