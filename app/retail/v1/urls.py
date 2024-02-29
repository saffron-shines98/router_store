from flask import Blueprint
from app.retail.v1.order import views as status_views
from app.retail.v1.product import views as product_view
from app.retail.v1.vendor import views as vendor_view
from app.retail.v1.inventory import views as inventory_view
from app.retail.v1.price import views as price_view
from app.retail.v1.catalog import views as catalog_view
from app.retail.v1.fulfillment import views as fulfillment_view

v1 = Blueprint('v1', __name__)


order_prefix = '/order'
v1.add_url_rule(order_prefix + '/status/update', view_func=status_views.StatusUpdate.as_view('status_update'))
v1.add_url_rule(order_prefix + '/create', view_func=status_views.OrderCreate.as_view('order_create'))
v1.add_url_rule(order_prefix + '/update', view_func=status_views.OrderUpdate.as_view('order_update'))
v1.add_url_rule(order_prefix + '/fetch', view_func=status_views.OrderFetch.as_view('order_fetch'))
v1.add_url_rule(order_prefix + '/status', view_func=status_views.OrderStatus.as_view('order_status'))

fulfillment_prefix = '/fulfillment'
v1.add_url_rule(fulfillment_prefix + '/create', view_func=fulfillment_view.FulfillmentCreate.as_view('fulfillment_create'))
v1.add_url_rule(fulfillment_prefix + '/status', view_func=fulfillment_view.FulfillmentStatus.as_view('fulfillment_status'))


customer_prefix = '/customer'
v1.add_url_rule(customer_prefix + '/create', view_func=status_views.CustomerStatusCreate.as_view('customer_status_create'))

# customer_prefix = '/vendor'
# v1.add_url_rule(customer_prefix + '/status/create', view_func=status_views.CustomerStatusCreate.as_view('customer_status_create'))
vendor_prefix = '/provider'
v1.add_url_rule(vendor_prefix + '/create', view_func=vendor_view.VendorCreate.as_view('vendor_create'))
v1.add_url_rule(vendor_prefix + '/fetch', view_func=vendor_view.VendorFetch.as_view('vendor_fetch'))
v1.add_url_rule(vendor_prefix + '/status', view_func=vendor_view.VendorStatus.as_view('vendor_status'))
v1.add_url_rule(vendor_prefix + '/update', view_func=vendor_view.VendorUpdate.as_view('vendor_update'))

product_prefix = '/product'
v1.add_url_rule(product_prefix + '/create', view_func=product_view.CreateProduct.as_view('create_productr_request_log'))
v1.add_url_rule(product_prefix + '/status', view_func=product_view.ProductStatus.as_view('product_status'))

inventory_prefix = '/inventory'
v1.add_url_rule(inventory_prefix + '/update', view_func=inventory_view.InventoryUpdate.as_view('inventory_updates'))

catalog_prefix = '/catalog'
v1.add_url_rule(catalog_prefix + '/fetch', view_func=catalog_view.FetchCatalogFromEs.as_view('catalog_fetch'))
v1.add_url_rule(catalog_prefix + '/fetchV1', view_func=catalog_view.FetchCatalog.as_view('catalog_fetch_v1'))
v1.add_url_rule(catalog_prefix + '/count', view_func=catalog_view.FetchCatalogCount.as_view('catalog_fetch_count'))

price_prefix = '/price'
v1.add_url_rule(price_prefix + '/update', view_func=price_view.PriceUpdate.as_view('price_updates'))

price_prefix = '/price'
v1.add_url_rule(price_prefix + '/bulkupdate', view_func=price_view.BulkPriceUpdate.as_view('bulk_price_update'))