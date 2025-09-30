import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.main import api as fastapi_api

api_version = fastapi_api
