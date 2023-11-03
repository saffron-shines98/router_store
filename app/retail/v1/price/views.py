from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.price.service import PriceService
class PriceUpdate(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'item_id': {
                'type': 'string'
            },
            'noderetail_storefront_id': {
                'type': 'string'
            }
        }
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response = PriceService(params, headers).update_price()
        return render_success_response(response, msg='success')
