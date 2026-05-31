from datetime import date

from pydantic import BaseModel


class EquipmentResponse(BaseModel):
    equipment_id: str
    type: str
    commissioned_date: date
    last_inspection_date: date
    status: str
    location: str | None = None
