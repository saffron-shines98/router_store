from config import Config
from app.base_coordinator import BaseCoordinator,SSOCoordinator


class PriceCoordinator(BaseCoordinator):

    def __init__(self):
        super(PriceCoordinator, self).__init__()
        self.sso_coordinator =SSOCoordinator()