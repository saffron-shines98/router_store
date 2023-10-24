from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.product.service import ProductService


class CreateProduct(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'attributes': {'type': 'object'},
            'item_id': {'type': 'string'},
            'category': {'type': 'string'},
            'provider_id': {'type': 'string'},
        },
        'required': ['item_id', 'category', 'provider_id', 'attributes']
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response = ProductService(params, headers).create_product_request_log()
        return render_success_response(response, msg='Successfully Log save')