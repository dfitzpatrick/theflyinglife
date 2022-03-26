from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from tfl.api_v1.weather import router as weather_router
from tfl.instances import metar_service, taf_service
from tfl.site_routing import static_page_routes
from tfl.configuration import SECRET_KEY
from tfl.middleware import installed_middleware
import sentry_sdk

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
    await metar_service.poller.start()
    await taf_service.poller.start()
    #pass

