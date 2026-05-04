import httpx
from typing import List, Dict, Any, Optional


class ResourceService:
    """资源检索服务"""

    @staticmethod
    async def search_papers(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索论文"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "fields": "title,authors,year,abstract,url,openAccessPdf",
            "limit": limit,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                papers = []
                for paper in data.get("data", []):
                    papers.append({
                        "title": paper.get("title", ""),
                        "authors": [a.get("name", "") for a in paper.get("authors", [])],
                        "year": paper.get("year"),
                        "abstract": paper.get("abstract", ""),
                        "url": paper.get("url", ""),
                        "pdf_url": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
                    })
                return papers
            return []

    @staticmethod
    async def search_github_repos(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索GitHub仓库"""
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                repos = []
                for item in data.get("items", []):
                    repos.append({
                        "name": item.get("full_name", ""),
                        "description": item.get("description", ""),
                        "url": item.get("html_url", ""),
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                    })
                return repos
            return []

    @staticmethod
    async def search_arxiv(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索arXiv论文"""
        import xml.etree.ElementTree as ET
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                papers = []
                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else ""
                    authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)]
                    summary = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
                    arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1] if entry.find("atom:id", ns) is not None else ""
                    pdf_link = entry.find("atom:link[@title='pdf']", ns)
                    pdf_url = pdf_link.get("href") if pdf_link is not None else None
                    
                    papers.append({
                        "title": title,
                        "authors": authors,
                        "abstract": summary,
                        "arxiv_id": arxiv_id,
                        "url": f"https://arxiv.org/abs/{arxiv_id}",
                        "pdf_url": pdf_url,
                    })
                return papers
            return []

    @staticmethod
    def generate_search_urls(resource_name: str, resource_type: str) -> Dict[str, str]:
        """生成搜索链接"""
        urls = {}
        
        if resource_type == "paper":
            urls["google_scholar"] = f"https://scholar.google.com/scholar?q={resource_name.replace(' ', '+')}"
            urls["arxiv"] = f"https://arxiv.org/search/?query={resource_name.replace(' ', '+')}&searchtype=all"
            urls["semantic_scholar"] = f"https://www.semanticscholar.org/search?q={resource_name.replace(' ', '+')}&sort=relevance"
        
        elif resource_type == "repo":
            urls["github"] = f"https://github.com/search?q={resource_name.replace(' ', '+')}&type=repositories"
            urls["papers_with_code"] = f"https://paperswithcode.com/search?q={resource_name.replace(' ', '+')}"
        
        elif resource_type == "dataset":
            urls["huggingface"] = f"https://huggingface.co/datasets?search={resource_name.replace(' ', '+')}"
            urls["google_dataset"] = f"https://datasetsearch.research.google.com/search?q={resource_name.replace(' ', '+')}"
        
        elif resource_type == "model":
            urls["huggingface"] = f"https://huggingface.co/models?search={resource_name.replace(' ', '+')}"
            urls["github"] = f"https://github.com/search?q={resource_name.replace(' ', '+')}&type=repositories"
        
        return urls


resource_service = ResourceService()
