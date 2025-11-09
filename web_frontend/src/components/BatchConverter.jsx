import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import ConfigForm from './ConfigForm'
import { convertBatch, downloadBatchZip } from '../services/api'
import './BatchConverter.css'

function BatchConverter({ files, onFilesChange, config, onConfigChange }) {
  const [loading, setLoading] = useState(false)
  const [batchResult, setBatchResult] = useState(null)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      onFilesChange([...files, ...acceptedFiles])
    },
    accept: {
      'application/xml': ['.xml', '.XML'],
      'text/xml': ['.xml', '.XML'],
    },
    multiple: true,
  })

  const removeFile = (index) => {
    const newFiles = files.filter((_, i) => i !== index)
    onFilesChange(newFiles)
  }

  const handleConvert = async () => {
    if (files.length === 0) return

    setLoading(true)
    setBatchResult(null)
    try {
      const result = await convertBatch(files, config)
      setBatchResult(result)
    } catch (error) {
      alert(`Batch conversion failed: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadZip = async () => {
    if (!batchResult) return
    try {
      await downloadBatchZip(batchResult.batch_id)
    } catch (error) {
      alert(`Download failed: ${error.message}`)
    }
  }

  return (
    <div className="batch-converter-container">
      <div className="card">
        <h2>Batch Conversion</h2>

        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop XML files here...</p>
          ) : (
            <div>
              <p>Drag & drop XML files here, or click to select</p>
              <p className="hint">Supports multiple .xml and .XML files</p>
            </div>
          )}
        </div>

        {files.length > 0 && (
          <div className="file-list">
            <h3>Selected Files ({files.length}):</h3>
            <div className="files-grid">
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">
                    {(file.size / 1024).toFixed(2)} KB
                  </span>
                  <button
                    className="remove-btn"
                    onClick={() => removeFile(index)}
                    disabled={loading}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          className="convert-btn"
          onClick={handleConvert}
          disabled={files.length === 0 || loading}
        >
          {loading ? 'Converting...' : `Convert ${files.length} File${files.length !== 1 ? 's' : ''}`}
        </button>

        {batchResult && (
          <div className="batch-results">
            <div className="results-header">
              <h3>Conversion Results</h3>
              <div className="results-stats">
                <span className="stat success">
                  ✓ {batchResult.successful} successful
                </span>
                {batchResult.failed > 0 && (
                  <span className="stat error">
                    ✗ {batchResult.failed} failed
                  </span>
                )}
              </div>
            </div>

            {batchResult.successful > 0 && (
              <button className="download-zip-btn" onClick={handleDownloadZip}>
                Download All as ZIP
              </button>
            )}

            <div className="results-list">
              {batchResult.results.map((result, index) => (
                <div
                  key={index}
                  className={`result-item ${result.status}`}
                >
                  <span className="result-filename">{result.filename}</span>
                  <span className={`result-status ${result.status}`}>
                    {result.status === 'success' ? '✓' : '✗'}
                  </span>
                  {result.error_message && (
                    <div className="result-error">{result.error_message}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BatchConverter

