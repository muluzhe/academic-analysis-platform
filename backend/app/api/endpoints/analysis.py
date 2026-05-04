import base64
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import uuid
import os
import shutil
import logging

from app.models.schemas import AnalysisRequest, AnalysisResponse, InputType, AnalysisMode
from app.services.ai_service import ai_service
from app.services.paper_service import paper_service
from app.services.wechat_service import wechat_service
from app.services.history_service import history_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """分析请求入口"""
    analysis_id = str(uuid.uuid4())
    
    try:
        if request.input_type == InputType.PAPER:
            result = await _analyze_paper(request)
        elif request.input_type == InputType.WECHAT:
            result = await _analyze_wechat(request)
        elif request.input_type == InputType.LINKAGE:
            result = await _analyze_linkage(request)
        else:
            raise HTTPException(status_code=400, detail="不支持的输入类型")
        
        # 保存历史记录
        history_service.add_record(
            input_type=request.input_type.value,
            title=result.get("title", "未命名分析"),
            summary=result.get("summary", ""),
            result=result,
        )
        
        return AnalysisResponse(
            id=analysis_id,
            input_type=request.input_type,
            mode=request.mode,
            status="completed",
            created_at=datetime.now(),
            completed_at=datetime.now(),
            result=result,
        )
    
    except Exception as e:
        return AnalysisResponse(
            id=analysis_id,
            input_type=request.input_type,
            mode=request.mode,
            status="failed",
            created_at=datetime.now(),
            error=str(e),
        )


@router.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """流式分析"""
    async def event_generator():
        try:
            if request.input_type == InputType.PAPER:
                content = request.content or ""
                if request.paper_url:
                    # 获取论文内容
                    arxiv_id = paper_service.extract_arxiv_id(request.paper_url)
                    if arxiv_id:
                        paper_info = await paper_service.fetch_arxiv(arxiv_id)
                        content = f"标题: {paper_info['title']}\n\n作者: {', '.join(paper_info['authors'])}\n\n摘要: {paper_info['abstract']}"
                
                async for chunk in ai_service.analyze_paper(content, request.mode.value, stream=True):
                    # 使用 JSON 编码避免换行符问题
                    data = json.dumps({"type": "content", "data": chunk})
                    yield f"data: {data}\n\n"
            
            elif request.input_type == InputType.WECHAT:
                content = request.content or ""
                if request.wechat_url:
                    article = await wechat_service.fetch_article(request.wechat_url)
                    content = article["content"]
                
                async for chunk in ai_service.analyze_wechat(content, request.mode.value, stream=True):
                    # 使用 JSON 编码避免换行符问题
                    data = json.dumps({"type": "content", "data": chunk})
                    yield f"data: {data}\n\n"
            
            elif request.input_type == InputType.LINKAGE:
                paper_content = request.content or ""
                article_content = ""
                
                if request.paper_url:
                    arxiv_id = paper_service.extract_arxiv_id(request.paper_url)
                    if arxiv_id:
                        paper_info = await paper_service.fetch_arxiv(arxiv_id)
                        paper_content = f"标题: {paper_info['title']}\n\n作者: {', '.join(paper_info['authors'])}\n\n摘要: {paper_info['abstract']}"
                
                if request.wechat_url:
                    article = await wechat_service.fetch_article(request.wechat_url)
                    article_content = article["content"]
                
                async for chunk in ai_service.analyze_linkage(paper_content, article_content, stream=True):
                    # 使用 JSON 编码避免换行符问题
                    data = json.dumps({"type": "content", "data": chunk})
                    yield f"data: {data}\n\n"
            
            # 发送完成信号
            done_data = json.dumps({"type": "done"})
            yield f"data: {done_data}\n\n"
        
        except Exception as e:
            error_data = json.dumps({"type": "error", "data": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/analyze/pdf")
async def analyze_pdf(
    file: UploadFile = File(...),
    mode: str = Form("standard"),
):
    """上传PDF分析"""
    analysis_id = str(uuid.uuid4())
    
    try:
        # 保存上传的文件
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{analysis_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 解析PDF
        content = paper_service.parse_pdf(file_path)
        
        # 分析内容
        result_text = ""
        async for chunk in ai_service.analyze_paper(content, mode, stream=False):
            result_text += chunk
        
        # 保存历史记录
        history_service.add_record(
            input_type="paper",
            title=f"PDF: {file.filename}",
            summary=result_text[:200] + "...",
            result={"analysis": result_text},
        )
        
        # 清理临时文件
        os.remove(file_path)
        
        return AnalysisResponse(
            id=analysis_id,
            input_type=InputType.PAPER,
            mode=AnalysisMode(mode),
            status="completed",
            created_at=datetime.now(),
            completed_at=datetime.now(),
            result={"analysis": result_text},
        )
    
    except Exception as e:
        return AnalysisResponse(
            id=analysis_id,
            input_type=InputType.PAPER,
            mode=AnalysisMode(mode),
            status="failed",
            created_at=datetime.now(),
            error=str(e),
        )


async def _analyze_paper(request: AnalysisRequest) -> dict:
    """分析论文"""
    content = request.content or ""
    title = "论文分析"
    
    if request.paper_url:
        arxiv_id = paper_service.extract_arxiv_id(request.paper_url)
        if arxiv_id:
            paper_info = await paper_service.fetch_arxiv(arxiv_id)
            title = paper_info["title"]
            
            # 尝试获取PDF全文内容
            full_text = ""
            if paper_info.get("pdf_url"):
                try:
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp_path = tmp.name
                    await paper_service.download_pdf(paper_info["pdf_url"], tmp_path)
                    full_text = paper_service.parse_pdf(tmp_path)
                    os.remove(tmp_path)
                except Exception as e:
                    logger.warning(f"无法获取PDF全文: {str(e)}")
            
            # 构建分析内容：优先使用全文，否则使用摘要
            if full_text and len(full_text) > 100:
                # 限制内容长度，避免超出token限制
                max_length = 15000  # 约4000-5000 tokens
                if len(full_text) > max_length:
                    full_text = full_text[:max_length] + "\n\n[内容已截断，仅分析前部内容]"
                content = f"标题: {paper_info['title']}\n\n作者: {', '.join(paper_info['authors'])}\n\n全文内容:\n{full_text}"
            else:
                content = f"标题: {paper_info['title']}\n\n作者: {', '.join(paper_info['authors'])}\n\n摘要: {paper_info['abstract']}"
        else:
            # 尝试Semantic Scholar
            content = f"论文链接: {request.paper_url}\n\n请分析此论文。"
    
    result_text = ""
    async for chunk in ai_service.analyze_paper(content, request.mode.value, stream=False):
        result_text += chunk
    
    return {
        "title": title,
        "summary": result_text[:200] + "...",
        "analysis": result_text,
        "input_url": request.paper_url,
    }


async def _analyze_wechat(request: AnalysisRequest) -> dict:
    """分析公众号文章"""
    content = request.content or ""
    title = "公众号文章分析"
    
    if request.wechat_url:
        article = await wechat_service.fetch_article(request.wechat_url)
        title = article["title"]
        content = article["content"]
    
    result_text = ""
    async for chunk in ai_service.analyze_wechat(content, request.mode.value, stream=False):
        result_text += chunk
    
    return {
        "title": title,
        "summary": result_text[:200] + "...",
        "analysis": result_text,
        "input_url": request.wechat_url,
    }


async def _analyze_linkage(request: AnalysisRequest) -> dict:
    """联动分析"""
    paper_content = request.content or ""
    article_content = ""
    title = "联动分析"
    
    if request.paper_url:
        arxiv_id = paper_service.extract_arxiv_id(request.paper_url)
        if arxiv_id:
            paper_info = await paper_service.fetch_arxiv(arxiv_id)
            paper_content = f"标题: {paper_info['title']}\n\n作者: {', '.join(paper_info['authors'])}\n\n摘要: {paper_info['abstract']}"
            title = f"联动: {paper_info['title']}"
    
    if request.wechat_url:
        article = await wechat_service.fetch_article(request.wechat_url)
        article_content = article["content"]
        if title == "联动分析":
            title = f"联动: {article['title']}"
    
    result_text = ""
    async for chunk in ai_service.analyze_linkage(paper_content, article_content, stream=False):
        result_text += chunk
    
    return {
        "title": title,
        "summary": result_text[:200] + "...",
        "analysis": result_text,
        "paper_url": request.paper_url,
        "article_url": request.wechat_url,
    }
