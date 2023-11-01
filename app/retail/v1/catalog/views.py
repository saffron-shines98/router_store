from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response
from app.retail.v1.catalog.service import CatalogService

class FetchCatalog(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'item_id': {'type': 'string'},
            'provider_id': {'type': 'string'},
            'noderetail_account_user_id': {'type': 'string'},
            'noderetail_catalog_id':{'type': 'string'},
            'noderetail_storefront_id':{'type': 'string'},
            'noderetail_item_id': {'type': 'string'},
            'noderetail_provider_id': {'type': 'string'},
            'noderetail_category': {'type': 'string'},
            'noderetail_category_id': {'type': 'string'},
            'noderetail_agg_id': {'type': 'string'},
            'inventory_info': {'type': 'object'},
            'pricing_info': {'type': 'object'},
            'attributes': {'type': 'object'},
        },
        'required': ['noderetail_storefront_id']
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response = CatalogService(params, headers).fetch_catalog()
        return render_success_response(response, msg='success')
    