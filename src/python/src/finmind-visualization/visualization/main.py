from visualization.api import v1
from visualization.backend.application import FastAPI

app = FastAPI()
app.include_router(v1.api_router)
