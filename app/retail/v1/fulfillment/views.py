from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response, render_success_response_with_body
from app.retail.v1.fulfillment.service import FulfillmentService


class FulfillmentCreate(MethodView):

    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = FulfillmentService(params, headers).fulfillment_create()
        return render_success_response(response, msg='success')

class FulfillmentStatus(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = FulfillmentService(params, headers).fulfillment_status()
        return render_success_response_with_body(response, msg='success')