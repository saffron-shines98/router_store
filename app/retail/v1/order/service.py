from config import Config
from datetime import datetime
from app.common_utils import get_current_datetime
from app.retail.v1.order.order_coordinator import OrderCoordinator

class OrderService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator =OrderCoordinator()

    def update_order_status(self):
        jwt_token = self.headers.get('Jwt')
        nodesso_id = self.headers.get('Nodesso-Id')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        api_response = self.coordinator.validate_jwt(payload)
        created_time = self.params.get('status_created_time')
        input_format = "%d:%m:%Y %H:%M:%S"
        output_format = "%Y:%m:%d %H:%M:%S"
        parsed_date = datetime.strptime(created_time, input_format)
        converted_date_time = parsed_date.strftime(output_format)
        current_date_time= get_c
        order_payload = {
            "order_id": self.params.get('order_id'),
            "order_status": self.params.get('order_status'),
            "fulfilment_status": self.params.get('fulfilment_status'),
            "refund_status": self.params.get('refund_status'),
            "status_created_time": converted_date_time,
            "remark": self.params.get('remark'),
            "created_at":get_current_datetime()
        }
        self.coordinator.save_data_in_db(order_payload, 'plotch_order_status_request')
        return order_payload