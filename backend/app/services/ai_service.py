import httpx
import json
import logging
from typing import AsyncGenerator, Optional
from app.core.config import get_settings
from app.core.prompts import (
    SYSTEM_PROMPT,
    PAPER_ANALYSIS_PROMPT,
    WECHAT_ANALYSIS_PROMPT,
    RESOURCE_RETRIEVAL_PROMPT,
    LINKAGE_ANALYSIS_PROMPT,
    QUICK_SUMMARY_PROMPT,
)

logger = logging.getLogger(__name__)

settings = get_settings()


class AIService:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.api_base = settings.AI_API_BASE
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE

    async def analyze_paper(
        self, content: str, mode: str = "standard", stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """分析论文内容"""
        if mode == "quick":
            prompt = QUICK_SUMMARY_PROMPT.format(content=content)
        else:
            prompt = PAPER_ANALYSIS_PROMPT.format(content=content)

        if stream:
            async for chunk in self._stream_chat(prompt):
                yield chunk
        else:
            result = await self._chat(prompt)
            yield result

    async def analyze_wechat(
        self, content: str, mode: str = "standard", stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """分析公众号文章"""
        if mode == "quick":
            prompt = QUICK_SUMMARY_PROMPT.format(content=content)
        else:
            prompt = WECHAT_ANALYSIS_PROMPT.format(content=content)

        if stream:
            async for chunk in self._stream_chat(prompt):
                yield chunk
        else:
            result = await self._chat(prompt)
            yield result

    async def analyze_linkage(
        self, paper_content: str, article_content: str, stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """联动分析论文和公众号文章"""
        prompt = LINKAGE_ANALYSIS_PROMPT.format(
            paper_content=paper_content, article_content=article_content
        )

        if stream:
            async for chunk in self._stream_chat(prompt):
                yield chunk
        else:
            result = await self._chat(prompt)
            yield result

    async def retrieve_resources(
        self, resources: list, stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """检索资源"""
        resources_text = "\n".join(
            [f"- {r['name']} ({r['type']})" for r in resources]
        )
        prompt = RESOURCE_RETRIEVAL_PROMPT.format(resources=resources_text)

        if stream:
            async for chunk in self._stream_chat(prompt):
                yield chunk
        else:
            result = await self._chat(prompt)
            yield result

    async def _chat(self, prompt: str) -> str:
        """非流式对话"""
        # 如果没有配置API密钥，返回模拟响应
        if not self.api_key:
            logger.warning("AI_API_KEY 未配置，返回模拟响应")
            return self._mock_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }

        try:
            # 修复双斜杠问题
            base_url = self.api_base.rstrip('/')
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text[:500] if e.response.text else "无详细错误信息"
            logger.error(f"AI API HTTP错误: {e.response.status_code} - {error_detail}")
            logger.error(f"请求URL: {self.api_base}/chat/completions")
            logger.error(f"请求模型: {self.model}")
            return f"AI服务请求失败 (HTTP {e.response.status_code}): {error_detail}\n\n请检查:\n1. API密钥是否正确\n2. 模型名称 '{self.model}' 是否有效\n3. API地址 '{self.api_base}' 是否正确"
        except httpx.RequestError as e:
            logger.error(f"AI API 请求错误: {str(e)}")
            return f"无法连接到AI服务 ({self.api_base}): {str(e)}"
        except Exception as e:
            logger.error(f"AI API 调用失败: {str(e)}")
            return f"AI分析服务异常: {str(e)}"

    async def _stream_chat(self, prompt: str) -> AsyncGenerator[str, None]:
        """流式对话"""
        if not self.api_key:
            logger.warning("AI_API_KEY 未配置，返回模拟响应")
            mock_response = self._mock_response(prompt)
            chunk_size = 50
            for i in range(0, len(mock_response), chunk_size):
                yield mock_response[i:i+chunk_size]
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }

        try:
            # 修复双斜杠问题
            base_url = self.api_base.rstrip('/')
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"] is not None:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPStatusError as e:
            logger.error(f"AI API HTTP错误: {e.response.status_code} - {e.response.text}")
            yield f"AI服务请求失败 (HTTP {e.response.status_code}): {e.response.text[:200]}"
        except httpx.RequestError as e:
            logger.error(f"AI API 请求错误: {str(e)}")
            yield f"无法连接到AI服务 ({self.api_base}): {str(e)}"
        except Exception as e:
            logger.error(f"AI API 调用失败: {str(e)}")
            yield f"AI分析服务异常: {str(e)}"

    def _mock_response(self, prompt: str) -> str:
        """生成模拟响应 - 当未配置API密钥或API调用失败时使用"""
        content_preview = prompt[:100].replace("\n", " ") if len(prompt) > 0 else "无内容"
        
        return f"""# ⚠️ 系统提示：当前处于模拟响应模式

## 🔴 重要说明

**平台尚未正确连接到AI分析服务，因此无法提供基于您输入内容的真实智能分析。**

您看到的以下内容是基于固定模板的占位符回复，**并非针对您提交内容的真实分析结果**。

---

## 诊断信息

| 项目 | 状态 |
|------|------|
| 输入内容长度 | {len(prompt)} 字符 |
| 内容预览 | {content_preview}... |
| AI API 配置 | 未检测到有效配置 |
| 响应类型 | 模拟/占位响应 |

## 解决方案

请按以下步骤配置AI API密钥：

1. **打开后端配置文件**
   ```
   d:\AI\tool\academic-analysis-platform\backend\.env
   ```

2. **填入有效的API密钥**
   ```env
   AI_API_KEY=sk-你的实际API密钥
   AI_API_BASE=https://chat.intern-ai.org.cn/api/v1/
   AI_MODEL=intern-ai-chat
   ```

3. **重启后端服务**
   ```bash
   # 停止当前服务（Ctrl+C），然后重新运行
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **刷新前端页面**，重新提交分析请求

---

## 如何获取API密钥

- **InternLM**: 访问 https://internlm.intern-ai.org.cn/ 注册获取
- **DeepSeek**: 访问 https://platform.deepseek.com/ 注册获取
- **OpenAI**: 访问 https://platform.openai.com/ 注册获取

---

*如果您已经配置了API密钥但仍看到此消息，请检查：*
1. *后端服务是否已重启*
2. *.env 文件是否位于 backend 目录下*
3. *API密钥是否有效且未过期*
"""


ai_service = AIService()
