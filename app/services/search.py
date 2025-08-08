from uuid import UUID
from sqlalchemy.orm import Session, aliased
from app.models.file import File
from app.models.folder import Folder
from app.models.permission import FilePermission, FolderPermission, RoleEnum
from sqlalchemy import literal_column, or_
from app.graphql.types import FilterInput, ContentType


def search_files_and_folders(
    db: Session,
    user_id: UUID,
    query: str,
    folder_id: UUID | None = None,
    filter: FilterInput | None = None,
):
    # Base queries
    files_query = db.query(File).join(FilePermission)
    folders_query = db.query(Folder).join(FolderPermission)

    # Initial filters
    files_query = files_query.filter(
        File.name.ilike(f"%{query}%"),
        FilePermission.user_id == user_id,
    )
    folders_query = folders_query.filter(
        Folder.name.ilike(f"%{query}%"),
        FolderPermission.user_id == user_id,
    )

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

        files_query = files_query.filter(
            File.folder_id.in_(db.query(literal_column("id")).select_from(folder_cte))
        )
        folders_query = folders_query.filter(
            Folder.id.in_(db.query(literal_column("id")).select_from(folder_cte))
        )

    if filter:
        if filter.type:
            if filter.type == ContentType.FILE:
                folders_query = folders_query.filter(literal_column("1") == "2")
            elif filter.type == ContentType.FOLDER:
                files_query = files_query.filter(literal_column("1") == "2")
        if filter.mime_type:
            files_query = files_query.filter(File.mime_type == filter.mime_type)
        if filter.created_at_after:
            files_query = files_query.filter(File.created_at > filter.created_at_after)
            folders_query = folders_query.filter(
                Folder.created_at > filter.created_at_after
            )
        if filter.created_at_before:
            files_query = files_query.filter(File.created_at < filter.created_at_before)
            folders_query = folders_query.filter(
                Folder.created_at < filter.created_at_before
            )
        if filter.updated_at_after:
            files_query = files_query.filter(File.updated_at > filter.updated_at_after)
            folders_query = folders_query.filter(
                Folder.updated_at > filter.updated_at_after
            )
        if filter.updated_at_before:
            files_query = files_query.filter(File.updated_at < filter.updated_at_before)
            folders_query = folders_query.filter(
                Folder.updated_at < filter.updated_at_before
            )
        if filter.size_greater_than:
            files_query = files_query.filter(File.size > filter.size_greater_than)
        if filter.size_less_than:
            files_query = files_query.filter(File.size < filter.size_less_than)
        if filter.owner_id:
            files_query = files_query.filter(
                FilePermission.role == RoleEnum.owner,
                FilePermission.user_id == filter.owner_id,
            )
            folders_query = folders_query.filter(
                FolderPermission.role == RoleEnum.owner,
                FolderPermission.user_id == filter.owner_id,
            )
        if filter.shared_with_me:
            files_query = files_query.filter(FilePermission.role != RoleEnum.owner)
            folders_query = folders_query.filter(
                FolderPermission.role != RoleEnum.owner
            )
        if filter.shared_by_me:
            owner_permission_file = aliased(FilePermission)
            shared_permission_file = aliased(FilePermission)
            files_query = files_query.join(
                owner_permission_file,
                (owner_permission_file.file_id == File.id)
                & (owner_permission_file.user_id == user_id)
                & (owner_permission_file.role == RoleEnum.owner),
            ).join(
                shared_permission_file,
                (shared_permission_file.file_id == File.id)
                & (shared_permission_file.user_id != user_id),
            )

            owner_permission_folder = aliased(FolderPermission)
            shared_permission_folder = aliased(FolderPermission)
            folders_query = folders_query.join(
                owner_permission_folder,
                (owner_permission_folder.folder_id == Folder.id)
                & (owner_permission_folder.user_id == user_id)
                & (owner_permission_folder.role == RoleEnum.owner),
            ).join(
                shared_permission_folder,
                (shared_permission_folder.folder_id == Folder.id)
                & (shared_permission_folder.user_id != user_id),
            )

        if filter.starred:
            files_query = files_query.filter(File.starred == True)
            folders_query = folders_query.filter(Folder.starred == True)

    return files_query.all(), folders_query.all()
