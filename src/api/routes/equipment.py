import logging

from fastapi import APIRouter, Depends, HTTPException, Path

from src.api.dependencies import get_equipment_repo
from src.api.schemas.equipment import EquipmentResponse
from src.db.equipment_repo import EquipmentRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["equipment"])


@router.get(
    "/equipment/{equipment_id:path}",
    response_model=EquipmentResponse,
    summary="Данные единицы оборудования по идентификатору",
)
def get_equipment(
    equipment_id: str = Path(..., min_length=1, max_length=50),
    repo: EquipmentRepository = Depends(get_equipment_repo),
) -> EquipmentResponse:
    try:
        rec = repo.get_by_id(equipment_id.strip())
    except Exception as exc:
        logger.exception("Ошибка обращения к БД оборудования")
        raise HTTPException(status_code=503, detail="База оборудования недоступна") from exc

    if rec is None:
        raise HTTPException(status_code=404, detail=f"Оборудование '{equipment_id}' не найдено")

    return EquipmentResponse(**rec.to_dict())
