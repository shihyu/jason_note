from fastapi import APIRouter
from visualization.api.v1.endpoints import (
    update_data,
    create_mysql_table,
    sync_history_data,
)

prefix = "/api/v1"
api_router = APIRouter()

api_router.include_router(update_data.router, prefix=prefix)
api_router.include_router(create_mysql_table.router, prefix=prefix)
api_router.include_router(sync_history_data.router, prefix=prefix)
