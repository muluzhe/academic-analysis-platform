import React, { useState, useRef, useCallback } from 'react'
import { Upload, Link, FileText, Loader2, Send, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { analysisApi } from '../services/api'

function PaperAnalysis() {
  const [url, setUrl] = useState('')
  const [content, setContent] = useState('')
  const [mode, setMode] = useState('standard')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [streamText, setStreamText] = useState('')
  const fileInputRef = useRef(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    setStreamText('')

    try {
      if (uploadedFile) {
        // PDF文件分析
        const response = await analysisApi.analyzePDF(uploadedFile, mode)
        setResult(response.data)
      } else if (url || content) {
        // 流式分析
        const response = await analysisApi.analyzeStream({
          inputType: 'paper',
          mode,
          paperUrl: url,
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
        setError('请输入论文链接、上传PDF或粘贴内容')
      }
    } catch (err) {
      setError(err.message || '分析失败，请稍后重试')
    } finally {
      // 确保 loading 状态总是被重置
      setLoading(false)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file)
      setUrl('')
      setContent('')
    } else {
      setError('请上传PDF文件')
    }
  }

  const clearFile = () => {
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <FileText className="h-6 w-6 mr-2 text-primary-600" />
          论文分析
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
            论文链接
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              setUploadedFile(null)
            }}
            placeholder="输入arXiv、DOI或Semantic Scholar链接"
            className="input-field"
            disabled={!!uploadedFile}
          />
        </div>

        {/* File Upload */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            <Upload className="h-4 w-4 inline mr-1" />
            上传PDF
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={!!url}
              className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
            >
              <Upload className="h-4 w-4" />
              <span>选择PDF文件</span>
            </button>
            {uploadedFile && (
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-600 dark:text-gray-300">
                  {uploadedFile.name}
                </span>
                <button onClick={clearFile} className="text-red-500 hover:text-red-700">
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Content Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">或粘贴论文内容</label>
          <textarea
            value={content}
            onChange={(e) => {
              setContent(e.target.value)
              setUploadedFile(null)
            }}
            placeholder="粘贴论文摘要或全文内容"
            rows={6}
            className="input-field resize-none"
            disabled={!!uploadedFile}
          />
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading || (!url && !content && !uploadedFile)}
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

export default PaperAnalysis
