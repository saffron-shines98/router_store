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
    param_config = {
        'type': 'object',
        'properties': {
            'order_id': {
                'type': 'string'
            },
            'noderetail_storefront_id': {
                'type': 'string'
            },
            'order_status': {
                'type': 'string'
            },
            'created_at_start': {
                'type': 'string'
            },
            'created_at_end': {
                'type': 'string'
            },
            'page_number': {
                'type': 'number'
            },
            'page_size': {
                'type': 'number'
            },
            'required': ['order_id', 'noderetail_storefront_id', 'order_status', 'created_at_start', 'created_at_end', 'created_at_end', 'page_number', 'page_size']
        }
    }
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).order_fetch()
        return render_success_response_with_body(response, msg='success')

class OrderStatus(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = OrderService(params, headers).order_status()
        return render_success_response_with_body(response, msg='success')
