from flask.views import MethodView
from app.decorators import validate_params
from app.common_utils import render_success_response, render_success_response_with_body
from app.retail.v1.catalog.service import CatalogService

class FetchCatalog(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'noderetail_storefront_id':{'type': 'string'}
        },
        'required': ['noderetail_storefront_id']
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response, msg = CatalogService(params, headers).fetch_catalog()
        return render_success_response_with_body(response, msg=msg)
    

class FetchCatalogCount(MethodView):
    param_config = {
        'type': 'object',
        'properties': {
            'noderetail_storefront_id':{'type': 'string'}
        },
        'required': ['noderetail_storefront_id']
    }
    @validate_params(param_config=param_config)
    def post(self, params, headers, *args, **kwargs):
        response, msg = CatalogService(params, headers).fetch_catalog_count()
        return render_success_response_with_body(response, msg=msg)