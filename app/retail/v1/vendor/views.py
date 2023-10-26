from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.vendor.service import VendorService


class VendorCreate(MethodView):
    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response = VendorService(params, headers).create_vendor()
        return render_success_response(response, msg='success')

