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
from tfl.instances import dtpp_service, dcs_path
from tfl.application_services.dcs import NoChartSupplementError, start_polling_dcs
from fastapi.responses import JSONResponse
from tfl.api_v2.metars import router as metars_router
from tfl.api_v2.dcs import router as dcs_router
from tfl.api_v2.tafs import router as tafs_router
from tfl.api_v2.procedures import router as procedures_router
from tfl.exception_handlers import init_exception_handlers

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

SENTRY_DEBUG = "https://9ccd59ca785c29ad20b03b781759c3e1@o391198.ingest.us.sentry.io/4507937915207680"
SENTRY_PROD = "https://06c72edd1f1e4108b6ca0cd2627283dd@o391198.ingest.sentry.io/5892190"
sentry_sdk.init(
    SENTRY_DEBUG,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


app = FastAPI(routes=static_page_routes, middleware=installed_middleware)

app.include_router(weather_router, prefix='/api/v1')
app.include_router(metars_router, prefix='/api/v2')
app.include_router(tafs_router, prefix='/api/v2')
app.include_router(dcs_router, prefix='/api/v2')
app.include_router(procedures_router, prefix='/api/v2')
app.mount("/static", StaticFiles(directory="./tfl/site/static"), name="static")
init_exception_handlers(app)


@app.on_event("startup")
async def startup_event():
    log.info("Starting Metar/TAF Pollers now")
    await metar_service.poller.start()
    await taf_service.poller.start()
    log.info("Starting DTPP Service")
    dtpp_service.register_callback(on_dtpp_change)
    dtpp_service.start()
    start_polling_dcs(dcs_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
    

