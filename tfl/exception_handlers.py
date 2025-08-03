from __future__ import annotations
from tfl.domain.exceptions import EntityNotFoundError
from tfl.application_services.dcs import NoChartSupplementError
from typing import TYPE_CHECKING
from fastapi.responses import JSONResponse
from fastapi import HTTPException

if TYPE_CHECKING:
    from fastapi.requests import Request
    from fastapi import FastAPI

def init_exception_handlers(app: FastAPI):
    @app.exception_handler(EntityNotFoundError)
    async def handle_entity_not_found(request: Request, exc: EntityNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "Item not found"},

        )

    @app.exception_handler(NoChartSupplementError)
    async def handle_no_chart_supplement(request: Request, exc: NoChartSupplementError):
        return JSONResponse(
            status_code=404,
            content={"error": "Chart Supplement not found"},

        )