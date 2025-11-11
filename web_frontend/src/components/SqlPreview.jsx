import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { downloadSql } from '../services/api'
import XmlViewer from './XmlViewer'
import ValidationResults from './ValidationResults'
import ConversionFlow from './ConversionFlow'
import './SqlPreview.css'

function SqlPreview({ result }) {
  const [viewMode, setViewMode] = useState('split') // 'split', 'tabs'
  const [activeTab, setActiveTab] = useState('xml') // 'xml' or 'sql' for tabs view
  const handleDownload = async () => {
    try {
      await downloadSql(result.id)
    } catch (error) {
      alert(`Download failed: ${error.message}`)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(result.sql_content)
    alert('SQL copied to clipboard!')
  }

  const hasXml = result.xml_content && result.xml_content.trim().length > 0

  // Debug: log to console
  if (process.env.NODE_ENV === 'development') {
    console.log('SqlPreview result:', {
      hasXml,
      xml_content_length: result.xml_content?.length,
      xml_content_preview: result.xml_content?.substring(0, 100),
    })
  }

  return (
    <div className="sql-preview-container">
      <div className="card">
        <div className="sql-preview-header">
          <h2>Conversion Result</h2>
          {hasXml && (
            <div className="view-mode-selector">
              <button
                className={viewMode === 'split' ? 'active' : ''}
                onClick={() => setViewMode('split')}
                title="Side-by-side view"
              >
                Split
              </button>
              <button
                className={viewMode === 'tabs' ? 'active' : ''}
                onClick={() => setViewMode('tabs')}
                title="Tabbed view"
              >
                Tabs
              </button>
            </div>
          )}
        </div>

        {/* Conversion Flow - Always show at top if available */}
        {result.stages && result.stages.length > 0 && (
          <ConversionFlow stages={result.stages} />
        )}

        {result.metadata && (
          <div className="metadata">
            <div className="metadata-item">
              <span className="label">Scenario ID:</span>
              <span className="value">{result.metadata.scenario_id || 'N/A'}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Nodes:</span>
              <span className="value">{result.metadata.nodes_count}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Filters:</span>
              <span className="value">{result.metadata.filters_count}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Calculated Attributes:</span>
              <span className="value">{result.metadata.calculated_attributes_count}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Logical Model:</span>
              <span className="value">{result.metadata.logical_model_present ? 'Yes' : 'No'}</span>
            </div>
          </div>
        )}

        <ValidationResults validation={result.validation} logs={result.validation_logs || []} />

        {result.corrections && result.corrections.corrections_applied && result.corrections.corrections_applied.length > 0 && (
          <div className="corrections">
            <h3>Auto-Corrections Applied ({result.corrections.corrections_applied.length})</h3>
            <div className="corrections-list">
              {result.corrections.corrections_applied.map((correction, index) => (
                <div key={index} className={`correction-item correction-${correction.confidence}`}>
                  <div className="correction-header">
                    <span className="correction-confidence">{correction.confidence.toUpperCase()}</span>
                    <span className="correction-code">{correction.issue_code}</span>
                    {correction.line_number && (
                      <span className="correction-line">Line {correction.line_number}</span>
                    )}
                  </div>
                  <div className="correction-description">{correction.description}</div>
                  <div className="correction-diff">
                    <span className="correction-original">- {correction.original_text}</span>
                    <span className="correction-corrected">+ {correction.corrected_text}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.warnings && result.warnings.length > 0 && !result.validation && (
          <div className="warnings">
            <h3>Warnings</h3>
            <ul>
              {result.warnings.map((warning, index) => (
                <li key={index}>{warning.message}</li>
              ))}
            </ul>
          </div>
        )}

        {hasXml && viewMode === 'split' && (
          <div className="split-view">
            <div className="split-panel xml-panel">
              <XmlViewer xmlContent={result.xml_content} filename={result.filename} embedded={true} />
            </div>
            <div className="split-panel sql-panel">
              <div className="sql-panel-header">
                <div className="sql-actions">
                  <button className="copy-btn" onClick={handleCopy}>
                    Copy SQL
                  </button>
                  <button className="download-btn" onClick={handleDownload}>
                    Download SQL
                  </button>
                </div>
              </div>
              <div className="sql-content">
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    borderRadius: '8px',
                    padding: '1rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    overflowWrap: 'break-word',
                  }}
                  wrapLines={true}
                  wrapLongLines={true}
                >
                  {result.sql_content}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        )}

        {hasXml && viewMode === 'tabs' && (
          <div className="tabs-view">
            <div className="tabs-header">
              <button
                className={activeTab === 'xml' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('xml')}
              >
                XML
              </button>
              <button
                className={activeTab === 'sql' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('sql')}
              >
                SQL
              </button>
            </div>
            <div className="tabs-content">
              {activeTab === 'xml' && (
                <XmlViewer xmlContent={result.xml_content} filename={result.filename} />
              )}
              {activeTab === 'sql' && (
                <div className="sql-tab-content">
                  <div className="sql-tab-header">
                    <div className="sql-actions">
                      <button className="copy-btn" onClick={handleCopy}>
                        Copy SQL
                      </button>
                      <button className="download-btn" onClick={handleDownload}>
                        Download SQL
                      </button>
                    </div>
                  </div>
                  <div className="sql-content">
                    <SyntaxHighlighter
                      language="sql"
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        borderRadius: '8px',
                        padding: '1rem',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                      }}
                      wrapLines={true}
                      wrapLongLines={true}
                    >
                      {result.sql_content}
                    </SyntaxHighlighter>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {!hasXml && (
          <div className="sql-only-view">
            <div className="sql-panel-header">
              <div className="sql-actions">
                <button className="copy-btn" onClick={handleCopy}>
                  Copy SQL
                </button>
                <button className="download-btn" onClick={handleDownload}>
                  Download SQL
                </button>
              </div>
            </div>
            <div className="sql-content">
              <SyntaxHighlighter
                language="sql"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  borderRadius: '8px',
                  padding: '1rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  overflowWrap: 'break-word',
                }}
                wrapLines={true}
                wrapLongLines={true}
              >
                {result.sql_content}
              </SyntaxHighlighter>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SqlPreview

