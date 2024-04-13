from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.cart.service import RouterService


class RouterConfig(MethodView):

    @validate_params(param_config=dict())
    def post(self, params, headers, *args, **kwargs):
        response_data = RouterService(params, headers).main()
        return render_success_response(response_data, msg='success')