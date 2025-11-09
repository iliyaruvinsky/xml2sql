import { useState } from 'react'
import Layout from './components/Layout'
import FileUpload from './components/FileUpload'
import ConfigForm from './components/ConfigForm'
import SqlPreview from './components/SqlPreview'
import HistoryPanel from './components/HistoryPanel'
import BatchConverter from './components/BatchConverter'
import './App.css'

function App() {
  const [mode, setMode] = useState('single') // 'single' or 'batch'
  const [singleFiles, setSingleFiles] = useState([])
  const [singleResult, setSingleResult] = useState(null)
  const [singleLoading, setSingleLoading] = useState(false)
  const [batchFiles, setBatchFiles] = useState([])
  const [config, setConfig] = useState({
    client: 'PROD',
    language: 'EN',
    schema_overrides: {},
    currency_udf_name: null,
    currency_rates_table: null,
    currency_schema: null,
  })
  const [showHistory, setShowHistory] = useState(false)

  const handleConfigChange = (newConfig) => {
    setConfig(newConfig)
  }

  return (
    <Layout>
      <div className="app-container">
        <div className="app-header">
          <h1>XML to SQL Converter</h1>
          <p>Convert SAP HANA calculation view XML to Snowflake SQL</p>
        </div>

        <div className="mode-selector">
          <button
            className={mode === 'single' ? 'active' : ''}
            onClick={() => setMode('single')}
          >
            Single File
          </button>
          <button
            className={mode === 'batch' ? 'active' : ''}
            onClick={() => setMode('batch')}
          >
            Batch Conversion
          </button>
          <button
            className={showHistory ? 'active' : ''}
            onClick={() => setShowHistory(!showHistory)}
          >
            History
          </button>
        </div>

        {showHistory ? (
          <HistoryPanel onClose={() => setShowHistory(false)} />
        ) : (
          <>
            <div className="main-content">
              <div className="left-panel">
                {mode === 'single' ? (
                  <>
                    <FileUpload
                      multiple={false}
                      files={singleFiles}
                      onFilesChange={(newFiles) => {
                        setSingleFiles(newFiles)
                        setSingleResult(null)
                      }}
                      config={config}
                      onConfigChange={handleConfigChange}
                      onConversionComplete={setSingleResult}
                      loading={singleLoading}
                      setLoading={setSingleLoading}
                    />
                    <ConfigForm
                      config={config}
                      onConfigChange={handleConfigChange}
                    />
                  </>
                ) : (
                  <BatchConverter
                    files={batchFiles}
                    onFilesChange={setBatchFiles}
                    config={config}
                    onConfigChange={handleConfigChange}
                  />
                )}
              </div>

              <div className="right-panel">
                {singleResult && mode === 'single' && (
                  <SqlPreview result={singleResult} />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}

export default App

