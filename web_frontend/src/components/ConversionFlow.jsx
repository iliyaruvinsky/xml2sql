import { useState } from 'react'
import './ConversionFlow.css'

function ConversionFlow({ stages }) {
  const [viewMode, setViewMode] = useState('summary') // 'summary' or 'detailed'
  const [expandedStage, setExpandedStage] = useState(null)

  if (!stages || stages.length === 0) {
    return null
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓'
      case 'in_progress':
        return '⟳'
      case 'failed':
        return '✗'
      case 'pending':
        return '○'
      default:
        return '○'
    }
  }
  
  const isSkipped = (stage) => {
    return stage.details?.skipped === true || 
           (stage.status === 'pending' && stage.stage_name === 'Auto-Correct SQL')
  }

  const getStatusClass = (status, stage) => {
    // Check if stage is skipped
    if (isSkipped(stage)) {
      return 'status-skipped'
    }
    switch (status) {
      case 'completed':
        return 'status-completed'
      case 'in_progress':
        return 'status-in-progress'
      case 'failed':
        return 'status-failed'
      case 'pending':
        return 'status-pending'
      default:
        return ''
    }
  }

  const formatDuration = (ms) => {
    if (!ms) return ''
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const renderSummaryView = () => {
    return (
      <div className="flow-summary">
        <div className="flowchart-container">
          <div className="flow-stages">
            {stages.map((stage, index) => {
              const skipped = isSkipped(stage)
              return (
              <div key={index} className="flow-stage-wrapper">
                <div className={`flow-stage ${getStatusClass(stage.status, stage)}`}>
                  <div className="stage-number">{index + 1}</div>
                  <div className="stage-icon">{skipped ? '⊘' : getStatusIcon(stage.status)}</div>
                  <div className="stage-content">
                    <div className="stage-name">{stage.stage_name}</div>
                    {stage.duration_ms !== null && stage.duration_ms !== undefined && (
                      <div className="stage-duration">{formatDuration(stage.duration_ms)}</div>
                    )}
                    {stage.details && Object.keys(stage.details).length > 0 && (
                      <div className="stage-stats">
                        {Object.entries(stage.details).slice(0, 3).map(([key, value]) => (
                          <span key={key} className="stat-item">
                            <span className="stat-key">{key.replace(/_/g, ' ')}:</span> {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value).substring(0, 15)}
                          </span>
                        ))}
                        {Object.keys(stage.details).length > 3 && (
                          <span className="stat-item">+{Object.keys(stage.details).length - 3} more</span>
                        )}
                      </div>
                    )}
                    {stage.error && (
                      <div className="stage-error">{stage.error}</div>
                    )}
                    {skipped && (
                      <div className="stage-skipped">Skipped: {stage.details?.reason || 'Not applicable'}</div>
                    )}
                  </div>
                </div>
                {index < stages.length - 1 && (
                  <div className={`flow-connector ${getStatusClass(stage.status, stage)}`}>
                    <div className="connector-line"></div>
                    <div className="connector-arrow">▶</div>
                  </div>
                )}
              </div>
            )
            })}
          </div>
        </div>
      </div>
    )
  }

  const renderDetailedView = () => {
    return (
      <div className="flow-detailed">
        {stages.map((stage, index) => {
          const skipped = isSkipped(stage)
          return (
          <div key={index} className={`flow-stage-detail ${getStatusClass(stage.status, stage)}`}>
            <div
              className="stage-detail-header"
              onClick={() => setExpandedStage(expandedStage === index ? null : index)}
            >
              <div className="stage-icon">{skipped ? '⊘' : getStatusIcon(stage.status)}</div>
              <div className="stage-name">{stage.stage_name}</div>
              {stage.duration_ms !== null && stage.duration_ms !== undefined && (
                <div className="stage-duration">{formatDuration(stage.duration_ms)}</div>
              )}
              <div className="expand-icon">{expandedStage === index ? '▼' : '▶'}</div>
            </div>

            {expandedStage === index && (
              <div className="stage-detail-content">
                {stage.details && Object.keys(stage.details).length > 0 && (
                  <div className="detail-section">
                    <h4>Details</h4>
                    <table className="details-table">
                      <tbody>
                        {Object.entries(stage.details).map(([key, value]) => (
                          <tr key={key}>
                            <td className="detail-key">{key.replace(/_/g, ' ')}</td>
                            <td className="detail-value">
                              {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {stage.xml_snippet && (
                  <div className="detail-section">
                    <h4>XML Input</h4>
                    <pre className="code-snippet">{stage.xml_snippet}</pre>
                  </div>
                )}

                {stage.sql_snippet && (
                  <div className="detail-section">
                    <h4>SQL Output</h4>
                    <pre className="code-snippet">{stage.sql_snippet}</pre>
                  </div>
                )}

                {stage.error && (
                  <div className="detail-section error-section">
                    <h4>Error</h4>
                    <div className="error-message">{stage.error}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
        })}
      </div>
    )
  }

  return (
    <div className="conversion-flow">
      <div className="flow-header">
        <h3>Conversion Flow</h3>
        <div className="view-toggle">
          <button
            className={viewMode === 'summary' ? 'active' : ''}
            onClick={() => setViewMode('summary')}
          >
            Summary
          </button>
          <button
            className={viewMode === 'detailed' ? 'active' : ''}
            onClick={() => setViewMode('detailed')}
          >
            Detailed
          </button>
        </div>
      </div>

      {viewMode === 'summary' ? renderSummaryView() : renderDetailedView()}
    </div>
  )
}

export default ConversionFlow

