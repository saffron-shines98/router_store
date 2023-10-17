from config import Config
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
            'token': jwt_token,
            'nodessoId': nodesso_id,
        }
        api_response = self.coordinator.validate_jwt(payload)
        challenging_string = api_response.get('challenge_string')
        order_payload = {
            "order_id": self.params.get('order_id'),
            "order_status": self.params.get('order_status'),
            "fulfilment_status": self.params.get('fulfillment_status'),
            "refund_status": self.params.get('refund_status'),
            "status_created_time": self.params.get('status_created_time'),
            "remark": self.params.get('remark'),
            "challenge_string":challenging_string
        }
        self.coordinator.save_data_in_db(order_payload, 'plotch_order_status_request')
        return order_payload