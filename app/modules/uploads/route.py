from fastapi import APIRouter, UploadFile, File
from .service import MeterService
from .schema import MeterReadingResponse

router = APIRouter()

@router.post("/upload", response_model=MeterReadingResponse)
async def upload_image(file: UploadFile = File(...)):
    return await MeterService.process_meter_upload(file)
