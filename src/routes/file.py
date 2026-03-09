from fastapi import UploadFile, File, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db

router = APIRouter()


@router.post("/file", response_model=bool)
async def file(attachments: list[UploadFile] = File(...), db: AsyncSession = Depends(get_db)):
    pass