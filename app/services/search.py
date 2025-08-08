from uuid import UUID
from sqlalchemy.orm import Session
from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, FolderPermission, RoleEnum
from sqlalchemy import literal_column


def search_files_and_folders(
    db: Session, user_id: UUID, query: str, folder_id: UUID | None = None
):
    if folder_id:
        # Recursive CTE to find all sub-folders of the given folder_id
        folder_cte = (
            db.query(Folder.id)
            .filter(Folder.id == folder_id)
            .cte(name="folder_cte", recursive=True)
        )

        # Recursive step
        folder_cte = folder_cte.union_all(
            db.query(Folder.id).join(folder_cte, Folder.parent_id == folder_cte.c.id)
        )

        files = (
            db.query(File)
            .join(FilePermission)
            .filter(
                File.name.ilike(f"%{query}%"),
                FilePermission.user_id == user_id,
                FilePermission.role == RoleEnum.owner,
                File.folder_id.in_(
                    db.query(literal_column("id")).select_from(folder_cte)
                ),
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
                Folder.id.in_(db.query(literal_column("id")).select_from(folder_cte)),
            )
            .all()
        )
    else:
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
