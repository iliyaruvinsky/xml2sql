import { useState } from 'react'
import Layout from './components/Layout'
import FileUpload from './components/FileUpload'
import ConfigForm from './components/ConfigForm'
import SqlPreview from './components/SqlPreview'
import HistoryPanel from './components/HistoryPanel'
import BatchConverter from './components/BatchConverter'
import BatchResults from './components/BatchResults'
import './App.css'

function App() {
  const [mode, setMode] = useState('single') // 'single' or 'batch'
  const [singleFiles, setSingleFiles] = useState([])
  const [singleResult, setSingleResult] = useState(null)
  const [singleLoading, setSingleLoading] = useState(false)
  const [singleProgressStages, setSingleProgressStages] = useState([])
  const [batchFiles, setBatchFiles] = useState([])
  const [batchResult, setBatchResult] = useState(null)
  const [batchLoading, setBatchLoading] = useState(false)
  const [config, setConfig] = useState({
    database_mode: 'hana',
    hana_version: '2.0',
    hana_package: null,
    client: 'PROD',
    language: 'EN',
    schema_overrides: { 'ABAP': 'SAPABAP1' },
    view_schema: '_SYS_BIC',
    currency_udf_name: null,
    currency_rates_table: null,
    currency_schema: null,
    auto_fix: false,
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
          <p>Convert SAP HANA calculation view XML to SQL</p>
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
                        setSingleProgressStages([])
                      }}
                      config={config}
                      onConfigChange={handleConfigChange}
                      onConversionComplete={(result) => {
                        setSingleResult(result)
                        setSingleProgressStages([])
                      }}
                      onProgressUpdate={setSingleProgressStages}
                      loading={singleLoading}
                      setLoading={setSingleLoading}
                    />
                    <ConfigForm
                      config={config}
                      onConfigChange={handleConfigChange}
                    />
                  </>
                ) : (
                  <>
                    <BatchConverter
                      files={batchFiles}
                      onFilesChange={(newFiles) => {
                        setBatchFiles(newFiles)
                        setBatchResult(null)
                      }}
                      config={config}
                      onConfigChange={handleConfigChange}
                      onConversionComplete={setBatchResult}
                      loading={batchLoading}
                      setLoading={setBatchLoading}
                    />
                    <ConfigForm
                      config={config}
                      onConfigChange={handleConfigChange}
                    />
                  </>
                )}
              </div>

              <div className="right-panel">
                {mode === 'single' && (
                  <SqlPreview
                    result={singleResult}
                    loading={singleLoading}
                    progressStages={singleProgressStages}
                    progressFilename={singleFiles[0]?.name}
                  />
                )}
                {mode === 'batch' && batchResult && (
                  <BatchResults batchResult={batchResult} />
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

