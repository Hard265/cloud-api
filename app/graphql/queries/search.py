from typing import List
from uuid import UUID
import strawberry
from strawberry.types import Info

from app.graphql.types import ContentsType, FileType, FolderType
from app.services.search import search_files_and_folders


@strawberry.type
class SearchQueries:
    @strawberry.field
    def search(self, info: Info, query: str) -> List[ContentsType]:
        user = info.context.get("user")
        db = info.context.get("db")
        files, folders = search_files_and_folders(
            db, user_id=UUID(user.sub), query=query
        )
        return [FileType.from_model(f) for f in files] + [
            FolderType.from_model(f) for f in folders
        ]
