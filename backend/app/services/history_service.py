import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


class HistoryService:
    """历史记录服务"""

    def __init__(self):
        self.history_dir = Path("history")
        self.history_dir.mkdir(exist_ok=True)
        self.history_file = self.history_dir / "history.json"
        self._ensure_history_file()

    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            content = self.history_file.read_text(encoding="utf-8")
            return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self, history: List[Dict[str, Any]]):
        """保存历史记录"""
        self.history_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_record(
        self,
        input_type: str,
        title: str,
        summary: str,
        result: Dict[str, Any],
    ) -> str:
        """添加历史记录"""
        history = self._load_history()
        
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "input_type": input_type,
            "title": title,
            "summary": summary,
            "result": result,
            "created_at": datetime.now().isoformat(),
        }
        
        history.insert(0, record)  # 新记录放在最前面
        
        # 限制历史记录数量
        max_records = 100
        if len(history) > max_records:
            history = history[:max_records]
        
        self._save_history(history)
        return record_id

    def get_records(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取历史记录列表"""
        history = self._load_history()
        return history[offset:offset + limit]

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """获取单条历史记录"""
        history = self._load_history()
        for record in history:
            if record["id"] == record_id:
                return record
        return None

    def delete_record(self, record_id: str) -> bool:
        """删除历史记录"""
        history = self._load_history()
        original_len = len(history)
        history = [r for r in history if r["id"] != record_id]
        
        if len(history) < original_len:
            self._save_history(history)
            return True
        return False

    def export_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """导出单条记录"""
        record = self.get_record(record_id)
        if record:
            return {
                "title": record.get("title", ""),
                "input_type": record.get("input_type", ""),
                "created_at": record.get("created_at", ""),
                "summary": record.get("summary", ""),
                "result": record.get("result", {}),
            }
        return None


history_service = HistoryService()
