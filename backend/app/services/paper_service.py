import httpx
import fitz  # PyMuPDF
import re
from typing import Optional, Dict, Any
from app.models.schemas import PaperInfo


class PaperService:
    """论文解析服务"""

    @staticmethod
    async def fetch_arxiv(arxiv_id: str) -> Dict[str, Any]:
        """获取arXiv论文信息"""
        url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            # 解析XML响应
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find(".//atom:entry", ns)
            if entry is None:
                raise ValueError("论文未找到")
            
            title = entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else ""
            authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)]
            summary = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
            pdf_link = entry.find("atom:link[@title='pdf']", ns)
            pdf_url = pdf_link.get("href") if pdf_link is not None else None
            
            return {
                "title": title,
                "authors": authors,
                "abstract": summary,
                "pdf_url": pdf_url,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            }

    @staticmethod
    async def fetch_semantic_scholar(paper_id: str) -> Dict[str, Any]:
        """获取Semantic Scholar论文信息"""
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        params = {
            "fields": "title,authors,year,abstract,url,pdf,openAccessPdf,fieldsOfStudy",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return {
                "title": data.get("title", ""),
                "authors": [a.get("name", "") for a in data.get("authors", [])],
                "year": data.get("year"),
                "abstract": data.get("abstract", ""),
                "url": data.get("url", ""),
                "pdf_url": data.get("openAccessPdf", {}).get("url") if data.get("openAccessPdf") else None,
            }

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF文件内容"""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise ValueError(f"PDF解析失败: {str(e)}")
        return text

    @staticmethod
    async def download_pdf(url: str, save_path: str) -> str:
        """下载PDF文件"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60.0, follow_redirects=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
        return save_path

    @staticmethod
    def extract_arxiv_id(url: str) -> Optional[str]:
        """从URL中提取arXiv ID"""
        patterns = [
            r"arxiv\.org/abs/(\d+\.\d+)",
            r"arxiv\.org/pdf/(\d+\.\d+)",
            r"arXiv:(\d+\.\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_doi(url: str) -> Optional[str]:
        """从URL中提取DOI"""
        pattern = r"(?:doi\.org/|doi:)(10\.\d{4,}/[^\s]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None


paper_service = PaperService()
