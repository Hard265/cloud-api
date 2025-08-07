from uuid import UUID
from sqlalchemy.orm import Session
from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, FolderPermission, RoleEnum


def search_files_and_folders(db: Session, user_id: UUID, query: str):
    files = (
        db.query(File)
        .join(FilePermission)
        .filter(
            File.name.ilike(f"%{query}%"),
            FilePermission.user_id == user_id,
            FilePermission.role == RoleEnum.owner,
        )
        .all()
    )
    folders = (
        db.query(Folder)
        .join(FolderPermission)
        .filter(
            Folder.name.ilike(f"%{query}%"),
            FolderPermission.user_id == user_id,
            FolderPermission.role == RoleEnum.owner,
        )
        .all()
    )
    return files, folders
