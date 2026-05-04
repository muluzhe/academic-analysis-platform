from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.resource_service import resource_service

router = APIRouter()


@router.get("/search/papers")
async def search_papers(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20),
):
    """搜索论文"""
    papers = await resource_service.search_papers(q, limit)
    return {"papers": papers}


@router.get("/search/repos")
async def search_repos(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20),
):
    """搜索代码仓库"""
    repos = await resource_service.search_github_repos(q, limit)
    return {"repositories": repos}


@router.get("/search/arxiv")
async def search_arxiv(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20),
):
    """搜索arXiv论文"""
    papers = await resource_service.search_arxiv(q, limit)
    return {"papers": papers}


@router.get("/search-urls")
async def generate_search_urls(
    name: str = Query(..., description="资源名称"),
    type: str = Query(..., description="资源类型: paper/repo/dataset/model"),
):
    """生成搜索链接"""
    urls = resource_service.generate_search_urls(name, type)
    return {"urls": urls}
