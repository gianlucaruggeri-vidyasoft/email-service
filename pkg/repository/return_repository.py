from typing import Optional
from pkg.config.database import get_database

class Return:
    def __init__(self, return_id: str) -> None:
        self.id = return_id

class ReturnRepository:
    def __init__(self) -> None:
        self.db = get_database()
        self.collection = self.db.returns

    async def add(self, ret: Return) -> None:
        await self.collection.update_one(
            {"return_id": ret.id},
            {"$set": {"return_id": ret.id}},
            upsert=True
        )

    async def get_by_id(self, return_id: str) -> Optional[Return]:
        try:
            data = await self.collection.find_one({"return_id": return_id})
            if data:
                return Return(return_id=data["return_id"])
            return None
        except Exception:
            return None

    async def exists(self, return_id: str) -> bool:
        try:
            doc = await self.collection.find_one({"return_id": return_id})
            return doc is not None
        except Exception:
            return False