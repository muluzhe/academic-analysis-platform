import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
})

// 分析API
export const analysisApi = {
  // 分析论文
  analyzePaper: (data) => api.post('/analysis/analyze', {
    input_type: 'paper',
    mode: data.mode || 'standard',
    paper_url: data.url,
    content: data.content,
  }),

  // 分析公众号文章
  analyzeWechat: (data) => api.post('/analysis/analyze', {
    input_type: 'wechat',
    mode: data.mode || 'standard',
    wechat_url: data.url,
    content: data.content,
  }),

  // 联动分析
  analyzeLinkage: (data) => api.post('/analysis/analyze', {
    input_type: 'linkage',
    mode: data.mode || 'standard',
    paper_url: data.paperUrl,
    wechat_url: data.wechatUrl,
    content: data.content,
  }),

  // 上传PDF分析
  analyzePDF: (file, mode = 'standard') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('mode', mode)
    return api.post('/analysis/analyze/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 流式分析
  analyzeStream: (data) => {
    return fetch(`${API_BASE_URL}/analysis/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input_type: data.inputType,
        mode: data.mode || 'standard',
        paper_url: data.paperUrl,
        wechat_url: data.wechatUrl,
        content: data.content,
      }),
    })
  },
}

// 历史记录API
export const historyApi = {
  getHistory: (limit = 50, offset = 0) => 
    api.get(`/history?limit=${limit}&offset=${offset}`),
  
  getRecord: (id) => api.get(`/history/${id}`),
  
  deleteRecord: (id) => api.delete(`/history/${id}`),
  
  exportRecord: (id) => api.get(`/history/${id}/export`),
}

// 资源检索API
export const resourceApi = {
  searchPapers: (q, limit = 5) => 
    api.get(`/resource/search/papers?q=${encodeURIComponent(q)}&limit=${limit}`),
  
  searchRepos: (q, limit = 5) => 
    api.get(`/resource/search/repos?q=${encodeURIComponent(q)}&limit=${limit}`),
  
  searchArxiv: (q, limit = 5) => 
    api.get(`/resource/search/arxiv?q=${encodeURIComponent(q)}&limit=${limit}`),
  
  generateSearchUrls: (name, type) => 
    api.get(`/resource/search-urls?name=${encodeURIComponent(name)}&type=${type}`),
}

export default api
