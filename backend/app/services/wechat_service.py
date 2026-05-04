import httpx
import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


class WechatService:
    """公众号文章抓取服务"""

    @staticmethod
    async def fetch_article(url: str) -> Dict[str, Any]:
        """抓取公众号文章内容"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            
            # 处理可能的编码问题
            content = response.text
            
            # 解析HTML
            soup = BeautifulSoup(content, "html.parser")
            
            # 提取标题
            title = ""
            title_tag = soup.find("h1", class_="rich_media_title")
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                title_tag = soup.find("h2", class_="rich_media_title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
            
            # 提取公众号名称
            source = ""
            source_tag = soup.find("a", id="js_name")
            if source_tag:
                source = source_tag.get_text(strip=True)
            
            # 提取作者
            author = ""
            author_tag = soup.find("span", class_="profile_nickname")
            if author_tag:
                author = author_tag.get_text(strip=True)
            
            # 提取发布时间
            publish_time = ""
            time_tag = soup.find("em", id="publish_time")
            if time_tag:
                publish_time = time_tag.get_text(strip=True)
            
            # 提取正文内容
            content_text = ""
            content_div = soup.find("div", id="js_content")
            if content_div:
                # 移除脚本和样式
                for script in content_div.find_all(["script", "style"]):
                    script.decompose()
                content_text = content_div.get_text(separator="\n", strip=True)
            
            # 提取图片
            images = []
            if content_div:
                for img in content_div.find_all("img"):
                    src = img.get("data-src") or img.get("src")
                    if src:
                        images.append(src)
            
            # 提取链接
            links = []
            if content_div:
                for a in content_div.find_all("a"):
                    href = a.get("href")
                    if href:
                        links.append({"text": a.get_text(strip=True), "url": href})
            
            return {
                "title": title,
                "source": source,
                "author": author,
                "publish_time": publish_time,
                "content": content_text,
                "images": images,
                "links": links,
                "url": url,
            }

    @staticmethod
    def extract_paper_links(content: str) -> list:
        """从文章中提取论文链接"""
        # arXiv链接
        arxiv_pattern = r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)"
        arxiv_matches = re.findall(arxiv_pattern, content)
        
        # DOI链接
        doi_pattern = r"doi\.org/(10\.\d{4,}/[^\s]+)"
        doi_matches = re.findall(doi_pattern, content)
        
        papers = []
        for arxiv_id in set(arxiv_matches):
            papers.append({
                "type": "arxiv",
                "id": arxiv_id,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            })
        
        for doi in set(doi_matches):
            papers.append({
                "type": "doi",
                "id": doi,
                "url": f"https://doi.org/{doi}",
            })
        
        return papers

    @staticmethod
    def extract_code_repos(content: str) -> list:
        """从文章中提取代码仓库链接"""
        github_pattern = r"github\.com/([\w-]+/[\w.-]+)"
        matches = re.findall(github_pattern, content)
        
        repos = []
        for repo in set(matches):
            repos.append({
                "platform": "github",
                "name": repo,
                "url": f"https://github.com/{repo}",
            })
        
        return repos


wechat_service = WechatService()
