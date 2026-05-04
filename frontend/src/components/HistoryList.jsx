import React, { useState, useEffect } from 'react'
import { Clock, Trash2, Download, FileText, MessageSquare, GitCompare } from 'lucide-react'
import { historyApi } from '../services/api'

function HistoryList() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const response = await historyApi.getHistory()
      setHistory(response.data.items || [])
    } catch (err) {
      setError('加载历史记录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await historyApi.deleteRecord(id)
      setHistory(history.filter((item) => item.id !== id))
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleExport = async (id) => {
    try {
      const response = await historyApi.exportRecord(id)
      const data = response.data
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis_${id}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('导出失败')
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'paper':
        return <FileText className="h-5 w-5 text-blue-500" />
      case 'wechat':
        return <MessageSquare className="h-5 w-5 text-green-500" />
      case 'linkage':
        return <GitCompare className="h-5 w-5 text-purple-500" />
      default:
        return <FileText className="h-5 w-5 text-gray-500" />
    }
  }

  const getTypeLabel = (type) => {
    switch (type) {
      case 'paper':
        return '论文分析'
      case 'wechat':
        return '公众号分析'
      case 'linkage':
        return '联动分析'
      default:
        return '未知类型'
    }
  }

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Clock className="h-6 w-6 mr-2 text-primary-600" />
          历史记录
        </h2>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20">
            {error}
          </div>
        )}

        {history.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>暂无历史记录</p>
            <p className="text-sm mt-2">开始分析论文或公众号文章，记录将显示在这里</p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div
                key={item.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getTypeIcon(item.input_type)}
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {item.title}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1 text-sm text-gray-500 dark:text-gray-400">
                        <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                          {getTypeLabel(item.input_type)}
                        </span>
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                      {item.summary && (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                          {item.summary}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleExport(item.id)}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                      title="导出"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="删除"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryList
