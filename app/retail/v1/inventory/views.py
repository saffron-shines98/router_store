from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.inventory.service import InventoryService


class InventoryUpdate(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'item_id': {
                'type': 'string'
            },
            'qty': {
                'type': 'number'
            },
            'storefront_instance_id': {
                'type': 'number'
            }
        }
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response = InventoryService(params, headers).update_inventory()
        return render_success_response(response, msg='success')
