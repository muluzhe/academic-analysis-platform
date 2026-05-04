import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import PaperAnalysis from './components/PaperAnalysis'
import WechatAnalysis from './components/WechatAnalysis'
import HistoryList from './components/HistoryList'

function App() {
  const [activeTab, setActiveTab] = useState('paper')
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    // 检查系统偏好
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setDarkMode(prefersDark)
  }, [])

  useEffect(() => {
    // 应用深色模式
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'paper':
        return <PaperAnalysis />
      case 'wechat':
        return <WechatAnalysis />
      case 'history':
        return <HistoryList />
      default:
        return <PaperAnalysis />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
      />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500 dark:text-gray-400">
            <p>学术内容智能分析平台 - 专为研究生设计的学术助理</p>
            <p className="mt-1">支持论文分析、公众号文章解析和资源检索</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
