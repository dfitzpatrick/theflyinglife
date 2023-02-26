from __future__ import annotations
from typing import TYPE_CHECKING
from .instances import airport_repository
if TYPE_CHECKING:
    from tfl.application_services.dtpp import DTPPVersionFile
    from tfl.domain.facilities import DTPPHeader


async def on_dtpp_change(header: DTPPHeader, version: DTPPVersionFile):
    airport_repository.load_dtpp(version.file_path)
