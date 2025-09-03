from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.responses import UJSONResponse


class FastAPI(FastAPI):
    """Core application to test."""

    def __init__(self):
        # 模板無法更改，需要到 fastapi 修改底層 code
        super(FastAPI, self).__init__()
        descritption = '<h1><a target="_blank" href="https://finmindtrade.com/"><h1>FinMind 提供金融開源 data，以台股為主，超過 50 種金融數據。</h1></a></h1>'
        self.description = descritption
        origins = [
            "http://localhost",
            "http://localhost:80",
            "http://localhost:443",
            "http://localhost:8080",
            "http://localhost:5000",
            "http://127.0.0.1:3001",
            "http://localhost:3001",
            "http://finminddev.servehttp.com/",
            "https://finminddev.servehttp.com/",
            "http://finmindtrade.com/",
            "https://finmindtrade.com/",
        ]
        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
        self.get("/")(self.main)
        self.on_event("shutdown")(self.close)
        self.title = "FinMind Visualization Api"
        self.version = "0.1"

    async def main(self):
        return UJSONResponse(
            {"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"}
        )

    async def close(self):
        """Gracefull shutdown."""
        logger.info("Shutting down the app.")
