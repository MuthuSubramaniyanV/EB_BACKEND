from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.uploads.service import UploadService
from app.modules.uploads.repository import UploadRepository
from app.modules.uploads.schema import UploadRead, UploadResponse
from app.modules.users.model import User

router = APIRouter(prefix="/uploads")


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    upload = await UploadService.process_meter_upload(session, file, current_user.id)
    return UploadResponse(
        id=upload.id,
        image_url=upload.image_url,
        timestamp=upload.timestamp,
        status=upload.status,
    )


@router.get("", response_model=list[UploadRead])
def list_uploads(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        uploads = UploadRepository.list_all(session)
    else:
        uploads = UploadRepository.list_by_user(session, current_user.id)
    return uploads


@router.get("/{upload_id}", response_model=UploadRead)
def get_upload(
    upload_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    upload = UploadRepository.get(session, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if current_user.role != "admin" and upload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return upload


@router.delete("/{upload_id}")
def delete_upload(
    upload_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    upload = UploadRepository.get(session, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if current_user.role != "admin" and upload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    UploadService.delete_upload(session, upload)
    return {"detail": "Upload deleted"}
