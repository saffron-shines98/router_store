from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class ProductCoordinator(BaseCoordinator):
    def __init__(self):
        super(ProductCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()