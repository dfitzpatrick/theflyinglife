from fastapi.routing import APIRouter
from tfl.instances import dcs_service
from fastapi.responses import FileResponse, Response, StreamingResponse
import io

router = APIRouter()

@router.get('/dcs/{icao}', response_class=StreamingResponse)
async def dcs_get(icao: str) -> list[io.BytesIO]:    
    def iter():
        zip = dcs_service.get_as_zip(icao)
        yield from zip
    
    return StreamingResponse(
        iter(), 
        media_type='application/x-zip-compressed',
        headers={
             "Content-Disposition": "attachment; filename=pages.zip"
        }
    )
    # return Response(
    #     zip.getvalue(),
    #     media_type='application/x-zip-compressed',
    #     headers={
    #         "Content-Disposition": "attachment; filename=pages.zip"
    #     }
    # )