from typing import Optional
from pkg.config.database import get_database

class Reservation:
    def __init__(self, reservation_id: str) -> None:
        self.id = reservation_id

class ReservationRepository:
    def __init__(self) -> None:
        self.db = get_database()
        self.collection = self.db.reservations

    async def add(self, reservation: Reservation) -> None:
        await self.collection.update_one(
            {"reservation_id": reservation.id},
            {"$set": {"reservation_id": reservation.id}},
            upsert=True
        )

    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        try:
            data = await self.collection.find_one({"reservation_id": reservation_id})
            if data:
                return Reservation(reservation_id=data["reservation_id"])
            return None
        except Exception:
            return None

    async def exists(self, reservation_id: str) -> bool:
        try:
            doc = await self.collection.find_one({"reservation_id": reservation_id})
            return doc is not None
        except Exception:
            return False