from visualization.backend import clients, finmind, router, application
from visualization.backend.database import DB
from visualization.backend.finmind import FinMindApi
from visualization.backend.router import Router

finmind_api = FinMindApi()
db = DB()
router = Router()
