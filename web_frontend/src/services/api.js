import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Single file conversion
export const convertSingle = async (file, config) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('config_json', JSON.stringify(config))

  const response = await api.post('/convert/single', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Batch conversion
export const convertBatch = async (files, config) => {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  formData.append('config_json', JSON.stringify(config))

  const response = await api.post('/convert/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Download SQL file
export const downloadSql = async (conversionId) => {
  const response = await api.get(`/download/${conversionId}`, {
    responseType: 'blob',
  })
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  
  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="(.+)"/)
    if (filenameMatch) {
      link.setAttribute('download', filenameMatch[1])
    }
  } else {
    link.setAttribute('download', `conversion_${conversionId}.sql`)
  }
  
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// Download batch ZIP
export const downloadBatchZip = async (batchId) => {
  const response = await api.get(`/download/batch/${batchId}`, {
    responseType: 'blob',
  })
  
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `batch_${batchId}.zip`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// Get history
export const getHistory = async (page = 1, pageSize = 50) => {
  const response = await api.get('/history', {
    params: { page, page_size: pageSize },
  })
  return response.data
}

// Get history detail
export const getHistoryDetail = async (conversionId) => {
  const response = await api.get(`/history/${conversionId}`)
  return response.data
}

// Delete history entry
export const deleteHistory = async (conversionId) => {
  await api.delete(`/history/${conversionId}`)
}

// Delete multiple history entries or all
export const deleteHistoryBulk = async (ids = []) => {
  if (ids.length > 0) {
    await api.delete('/history', {
      params: { ids: ids.join(',') },
    })
  } else {
    await api.delete('/history')
  }
}

// Get default config
export const getDefaultConfig = async () => {
  const response = await api.get('/config/defaults')
  return response.data
}

