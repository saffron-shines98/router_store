from config import Config
from app.app_config import register_versions, app


register_versions(Config.VERSIONS_ALLOWED)
