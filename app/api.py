from fastapi.routing import APIRouter
from fastapi import Response, UploadFile, File, Form, Depends, HTTPException
from uuid import UUID

from app.schemas.file import (
    FileCreate,
    FileRead,
    FileUpdate,
    Filename,
    FileExtension,
    FilePath,
)
from app.core.dependencies import get_file_holder_service
from app.core.file_holder_service import FileHolderService

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok"}


@router.post("/files")
async def post_file(
    filename: Filename = Form(...),
    file_extension: FileExtension = Form(...),
    path: FilePath = Form(...),
    comment: str | None = Form(None),
    file: UploadFile = File(...),
    service: FileHolderService = Depends(get_file_holder_service),
) -> FileRead:
    """
    Загрузка нового файла.
    Принимает метаданные файла и файл.
    """

    file_meta_obj = FileCreate(
        filename=filename,
        file_extension=file_extension,
        path=path,
        size=1,
        comment=comment,
    )

    file_data = await file.read()

    saved_meta = await service.create_file(
        file_data=file_data, file_create=file_meta_obj
    )
    return FileRead(
        id=UUID(saved_meta.uuid),
        filename=saved_meta.filename,
        file_extension=saved_meta.file_extension,
        path=saved_meta.path,
        size=saved_meta.size,
        created_at=saved_meta.created_at.isoformat(),
        updated_at=saved_meta.updated_at.isoformat() if saved_meta.updated_at else None,
        comment=saved_meta.comment,
    )


@router.get("/files")
async def list_files(
    service: FileHolderService = Depends(get_file_holder_service),
) -> list[FileRead]:
    """Получение списка всех файлов"""
    files_meta = await service.list_files()
    return [
        FileRead(
            id=UUID(meta.uuid),
            filename=meta.filename,
            file_extension=meta.file_extension,
            path=meta.path,
            size=meta.size,
            created_at=meta.created_at.isoformat(),
            updated_at=meta.updated_at.isoformat() if meta.updated_at else None,
            comment=meta.comment,
        )
        for meta in files_meta
    ]


@router.get("/files/{file_id}/meta")
async def get_file_meta(
    file_id: UUID,
    service: FileHolderService = Depends(get_file_holder_service),
) -> FileRead:
    """Получение метаданных файла по ID"""
    meta = await service.get_file_meta(file_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="File not found")

    return FileRead(
        id=UUID(meta.uuid),
        filename=meta.filename,
        file_extension=meta.file_extension,
        path=meta.path,
        size=meta.size,
        created_at=meta.created_at.isoformat(),
        updated_at=meta.updated_at.isoformat() if meta.updated_at else None,
        comment=meta.comment,
    )


@router.get("/files/{file_id}")
async def get_file(
    file_id: UUID,
    service: FileHolderService = Depends(get_file_holder_service),
) -> Response:
    """Получение содержимого файла по ID"""
    file_bytes = await service.get_file_by_id(file_id)
    return Response(content=file_bytes, media_type="application/octet-stream")


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: UUID,
    service: FileHolderService = Depends(get_file_holder_service),
):
    """Удаление файла по ID"""
    await service.delete_file(file_id)
    return {"status": "deleted", "file_id": str(file_id)}


@router.put("/files/{file_id}")
async def put_file(
    file_id: UUID,
    update: FileUpdate,
    service: FileHolderService = Depends(get_file_holder_service),
) -> FileRead:
    """
    Полная замена метаданных файла.
    """
    updated = await service.update_file_meta(file_id=file_id, update=update)
    return FileRead(
        id=UUID(updated.uuid),
        filename=updated.filename,
        file_extension=updated.file_extension,
        path=updated.path,
        size=updated.size,
        created_at=updated.created_at.isoformat(),
        updated_at=updated.updated_at.isoformat() if updated.updated_at else None,
        comment=updated.comment,
    )


@router.patch("/files/{file_id}")
async def patch_file(
    file_id: UUID,
    update: FileUpdate,
    service: FileHolderService = Depends(get_file_holder_service),
) -> FileRead:
    """
    Частичное обновление метаданных файла.
    """
    updated = await service.update_file_meta(file_id=file_id, update=update)
    return FileRead(
        id=UUID(updated.uuid),
        filename=updated.filename,
        file_extension=updated.file_extension,
        path=updated.path,
        size=updated.size,
        created_at=updated.created_at.isoformat(),
        updated_at=updated.updated_at.isoformat() if updated.updated_at else None,
        comment=updated.comment,
    )


@router.get("/files/search")
async def search_files(
    file_path: FilePath = Form(...),
    service: FileHolderService = Depends(get_file_holder_service),
) -> list[FileRead]:
    """Поиск файлов по пути"""

    return [
        FileRead(
            id=UUID(meta.uuid),
            filename=meta.filename,
            file_extension=meta.file_extension,
            path=meta.path,
            size=meta.size,
            created_at=meta.created_at.isoformat(),
            updated_at=meta.updated_at.isoformat() if meta.updated_at else None,
            comment=meta.comment,
        )
        for meta in await service.get_by_path_startswith(file_path)
    ]


@router.post("/files/synchronise")
async def synchronise_files():
    print("Synchronising files")
    return {"status": "synchronised"}
