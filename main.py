import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tfl.api_v1.weather import router as weather_router
from tfl.events import on_dtpp_change
from tfl.instances import metar_service, taf_service
from tfl.middleware import installed_middleware
from tfl.site_routing import static_page_routes
import os
import sys
from logging import StreamHandler, FileHandler
import logging
from tfl.instances import dtpp_service

BASE_DIR = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))

handler_console = StreamHandler(stream=sys.stdout)
handler_filestream = FileHandler(filename=f"{BASE_DIR}/tfl.log", encoding='utf-8')
handler_filestream.setLevel(logging.INFO)
handler_console.setLevel(logging.DEBUG)


logging_handlers = [
        handler_console,
        handler_filestream
    ]

logging.basicConfig(
    format="%(asctime)s | %(name)25s | %(funcName)25s | %(levelname)6s | %(message)s",
    datefmt="%b %d %H:%M:%S",
    level=logging.DEBUG,
    handlers=logging_handlers
)
logging.getLogger('asyncio').setLevel(logging.ERROR)
log = logging.getLogger(__name__)


sentry_sdk.init(
    "https://06c72edd1f1e4108b6ca0cd2627283dd@o391198.ingest.sentry.io/5892190",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


app = FastAPI(routes=static_page_routes, middleware=installed_middleware)

app.include_router(weather_router, prefix='/api/v1')
app.mount("/static", StaticFiles(directory="./tfl/site/static"), name="static")


@app.on_event("startup")
async def startup_event():
    log.info("Starting Metar/TAF Pollers")
    await metar_service.poller.start()
    await taf_service.poller.start()
    log.info("Starting DTPP Service")
    dtpp_service.register_callback(on_dtpp_change)
    dtpp_service.start()



