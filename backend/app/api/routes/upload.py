from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.common import UploadResponse
from app.services.upload_service import save_item_delivery_upload, save_pull_input_upload

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_input_alias(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")
    return await save_pull_input_upload(file)


@router.post("/upload/pull-input-data", response_model=UploadResponse)
async def upload_pull_input_data(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")
    return await save_pull_input_upload(file)


@router.post("/runs/{run_id}/upload/item-delivery", response_model=UploadResponse)
async def upload_item_delivery_update(run_id: str, file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")
    return await save_item_delivery_upload(run_id, file)
