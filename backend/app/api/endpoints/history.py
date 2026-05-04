from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.schemas import HistoryItem, HistoryListResponse
from app.services.history_service import history_service

router = APIRouter()


@router.get("", response_model=HistoryListResponse)
async def get_history(limit: int = 50, offset: int = 0):
    """获取历史记录列表"""
    records = history_service.get_records(limit=limit, offset=offset)
    items = []
    for record in records:
        items.append(HistoryItem(
            id=record["id"],
            title=record.get("title", "未命名"),
            input_type=record.get("input_type", "unknown"),
            created_at=record.get("created_at", ""),
            summary=record.get("summary", ""),
        ))
    
    return HistoryListResponse(
        items=items,
        total=len(items),
    )


@router.get("/{record_id}")
async def get_history_record(record_id: str):
    """获取单条历史记录"""
    record = history_service.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")
    return record


@router.delete("/{record_id}")
async def delete_history_record(record_id: str):
    """删除历史记录"""
    success = history_service.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录未找到")
    return {"message": "删除成功"}


@router.get("/{record_id}/export")
async def export_history_record(record_id: str):
    """导出历史记录"""
    record = history_service.export_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")
    return record
