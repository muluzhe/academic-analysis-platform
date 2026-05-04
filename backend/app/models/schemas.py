from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class InputType(str, Enum):
    PAPER = "paper"
    WECHAT = "wechat"
    LINKAGE = "linkage"


class AnalysisMode(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    FULL = "full"


class AnalysisRequest(BaseModel):
    input_type: InputType
    mode: AnalysisMode = AnalysisMode.STANDARD
    paper_url: Optional[str] = None
    wechat_url: Optional[str] = None
    content: Optional[str] = None
    ai_model: Optional[str] = None


class AnalysisResponse(BaseModel):
    id: str
    input_type: InputType
    mode: AnalysisMode
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class PaperInfo(BaseModel):
    title: str
    authors: List[str]
    venue: Optional[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    code_url: Optional[str] = None
    dataset_url: Optional[str] = None


class WechatArticle(BaseModel):
    title: str
    author: Optional[str] = None
    source: Optional[str] = None
    publish_time: Optional[datetime] = None
    content: Optional[str] = None
    url: str


class ResourceItem(BaseModel):
    name: str
    resource_type: Literal["paper", "repo", "dataset", "model", "tool"]
    status: Literal["found", "searching", "not_found"]
    url: Optional[str] = None
    search_suggestion: Optional[str] = None
    priority: Literal["high", "medium", "low"]


class AnalysisResult(BaseModel):
    overview: dict
    key_points: List[str]
    important_data: List[dict]
    resources: List[ResourceItem]
    action_suggestions: dict
    reproduction_roadmap: Optional[dict] = None
    raw_analysis: str


class HistoryItem(BaseModel):
    id: str
    title: str
    input_type: InputType
    created_at: datetime
    summary: str


class HistoryListResponse(BaseModel):
    items: List[HistoryItem]
    total: int
