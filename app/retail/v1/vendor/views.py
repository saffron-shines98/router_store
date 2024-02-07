from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response, render_success_response_with_body
from app.retail.v1.vendor.service import VendorService


class VendorCreate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = VendorService(params, headers).create_vendor()
        return render_success_response(response, msg='success')

class VendorFetch(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = VendorService(params, headers).fetch_vendor()
        return render_success_response_with_body(response, msg='success')

class VendorStatus(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = VendorService(params, headers).vendor_status()
        return render_success_response_with_body(response, msg='success')

class VendorUpdate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = VendorService(params, headers).update_vendor()
        return render_success_response(response, msg='success')
