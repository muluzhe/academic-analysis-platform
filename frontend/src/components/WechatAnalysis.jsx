import React, { useState } from 'react'
import { Link, MessageSquare, Loader2, Send, Globe } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { analysisApi } from '../services/api'

function WechatAnalysis() {
  const [url, setUrl] = useState('')
  const [content, setContent] = useState('')
  const [mode, setMode] = useState('standard')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [streamText, setStreamText] = useState('')

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    setStreamText('')

    try {
      if (url || content) {
        // 流式分析
        const response = await analysisApi.analyzeStream({
          inputType: 'wechat',
          mode,
          wechatUrl: url,
          content,
        })

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let fullText = ''
        let doneReceived = false

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const parsed = JSON.parse(data)
                if (parsed.type === 'done') {
                  doneReceived = true
                  setResult({ result: { analysis: fullText } })
                  return
                }
                if (parsed.type === 'error') {
                  setError(parsed.data)
                  return
                }
                if (parsed.type === 'content') {
                  fullText += parsed.data
                  setStreamText(fullText)
                }
              } catch (e) {
                // 兼容旧格式
                if (data === '[DONE]') {
                  doneReceived = true
                  setResult({ result: { analysis: fullText } })
                  return
                }
                if (data.startsWith('[ERROR]')) {
                  setError(data.slice(7))
                  return
                }
                fullText += data
                setStreamText(fullText)
              }
            }
          }
        }
        
        // 如果流结束但没有收到 [DONE]，仍然显示结果
        if (!doneReceived && fullText.length > 0) {
          setResult({ result: { analysis: fullText } })
        }
      } else {
        setError('请输入公众号文章链接或粘贴内容')
      }
    } catch (err) {
      setError(err.message || '分析失败，请稍后重试')
    } finally {
      // 确保 loading 状态总是被重置
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <MessageSquare className="h-6 w-6 mr-2 text-primary-600" />
          公众号文章分析
        </h2>

        {/* Mode Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">分析模式</label>
          <div className="flex space-x-2">
            {[
              { value: 'quick', label: '快速摘要' },
              { value: 'standard', label: '标准分析' },
              { value: 'full', label: '完整分析' },
            ].map((m) => (
              <button
                key={m.value}
                onClick={() => setMode(m.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mode === m.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        {/* URL Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            <Link className="h-4 w-4 inline mr-1" />
            文章链接
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="输入微信公众号文章链接 (mp.weixin.qq.com)"
            className="input-field"
          />
        </div>

        {/* Content Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            <Globe className="h-4 w-4 inline mr-1" />
            或粘贴文章内容
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="粘贴公众号文章内容"
            rows={8}
            className="input-field resize-none"
          />
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading || (!url && !content)}
          className="btn-primary w-full flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>分析中...</span>
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              <span>开始分析</span>
            </>
          )}
        </button>

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800">
            {error}
          </div>
        )}
      </div>

      {/* Result Section */}
      {(streamText || result) && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">分析结果</h3>
          <div className="markdown-body">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {streamText || result?.result?.analysis || result?.data?.result?.analysis || ''}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

export default WechatAnalysis
