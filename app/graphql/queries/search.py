from typing import List, Optional
from uuid import UUID
import strawberry
from strawberry.types import Info

from app.graphql.types import ContentsType, FileType, FolderType, FilterInput
from app.services.search import search_files_and_folders


@strawberry.type
class SearchQueries:
    @strawberry.field
    def search(
        self,
        info: Info,
        query: str,
        folder_id: Optional[UUID] = None,
        filter: Optional[FilterInput] = None,
    ) -> List[ContentsType]:
        user = info.context.get("user")
        db = info.context.get("db")
        files, folders = search_files_and_folders(
            db, user_id=UUID(user.sub), query=query, folder_id=folder_id, filter=filter
        )
        return [FileType.from_model(f) for f in files] + [
            FolderType.from_model(f) for f in folders
        ]
