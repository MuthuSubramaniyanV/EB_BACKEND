from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_user
from app.modules.meter.schema import MeterCaptureResponse
from app.modules.meter.service import MeterCaptureService
from app.modules.users.model import User

router = APIRouter(prefix="/meter")


@router.post("/capture", response_model=MeterCaptureResponse)
def capture_meter_image(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    upload = MeterCaptureService.capture_remote_image(session, current_user.id)
    return MeterCaptureResponse(
        upload_id=upload.id,
        image_url=upload.image_url,
        timestamp=upload.timestamp,
        status=upload.status,
    )
