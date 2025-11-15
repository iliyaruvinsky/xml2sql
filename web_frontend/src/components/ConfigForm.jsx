import { useState } from 'react'
import './ConfigForm.css'

const fieldHelpContent = {
  client: {
    tooltip:
      "Purpose: Replaces $$client$$ placeholders in the XML with your specified value.\nDefault: PROD\nWhen to change: If your XML has client-specific logic (e.g., WHERE MANDT = '$$client$$').\nExample: If your XML contains WHERE MANDT = '$$client$$' and you set Client to 100, the generated SQL will have WHERE MANDT = '100'.",
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Replaces <code>$$client$$</code> placeholders in the XML with your specified value.
        <br />
        <strong>Default:</strong> PROD
        <br />
        <strong>When to change:</strong> If your XML has client-specific logic (e.g., <code>WHERE MANDT = '$$client$$'</code>).
        <br />
        <strong>Example:</strong> If your XML contains <code>WHERE MANDT = '$$client$$'</code> and you set Client to <code>100</code>, the generated SQL will have <code>WHERE MANDT = '100'</code>.
      </div>
    ),
  },
  language: {
    tooltip:
      "Purpose: Replaces $$language$$ placeholders in the XML with your specified value.\nDefault: EN\nWhen to change: If your XML has language-specific fields or filters.\nExample: If your XML has WHERE SPRAS = '$$language$$' and you set Language to DE, the generated SQL will have WHERE SPRAS = 'DE'.",
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Replaces <code>$$language$$</code> placeholders in the XML with your specified value.
        <br />
        <strong>Default:</strong> EN
        <br />
        <strong>When to change:</strong> If your XML has language-specific fields or filters.
        <br />
        <strong>Example:</strong> If your XML has <code>WHERE SPRAS = '$$language$$'</code> and you set Language to <code>DE</code>, the generated SQL will have <code>WHERE SPRAS = 'DE'</code>.
      </div>
    ),
  },
  schemaOverrides: {
    tooltip:
      'Purpose: Maps schema names from the XML to your Snowflake schema names.\nWhen to use: If your Snowflake schemas have different names than what appears in the XML.\nExample: If your XML references SAPK5D.MARA but your Snowflake schema is PRODUCTION_DATA, add an override SAPK5D → PRODUCTION_DATA. The generated SQL will use PRODUCTION_DATA.MARA.\nNote: Leave empty if your Snowflake schema names match the XML exactly.',
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Maps schema names from the XML to your Snowflake schema names.
        <br />
        <strong>When to use:</strong> If your Snowflake schemas have different names than what's in the XML.
        <br />
        <strong>Example:</strong> If your XML references <code>SAPK5D.MARA</code> but your Snowflake schema is <code>PRODUCTION_DATA</code>, add an override: <code>SAPK5D</code> → <code>PRODUCTION_DATA</code>. The generated SQL will use <code>PRODUCTION_DATA.MARA</code>.
        <br />
        <strong>Note:</strong> Leave empty if your Snowflake schema names match the XML exactly.
      </div>
    ),
  },
  currencyOverview: {
    tooltip:
      'Purpose: Specifies currency conversion UDF and table names if your XML uses currency conversion.\nWhen to use: Only if your calculation views perform currency conversion.\nNote: Leave empty if currency conversion is not part of the XML.',
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Specifies currency conversion UDF and table names if your XML uses currency conversion.
        <br />
        <strong>When to use:</strong> Only if your calculation views perform currency conversion. Leave empty if not applicable.
        <br />
        <strong>Note:</strong> These settings tell the converter what names to use in the generated SQL for currency conversion functions and tables.
      </div>
    ),
  },
  currencyUdf: {
    tooltip:
      'Purpose: Name of your currency conversion function in Snowflake.\nExample: CONVERT_CURRENCY or MY_CURRENCY_CONVERT.\nNote: This should match the actual UDF name in your Snowflake environment.',
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Name of your currency conversion function in Snowflake.
        <br />
        <strong>Example:</strong> <code>CONVERT_CURRENCY</code> or <code>MY_CURRENCY_CONVERT</code>
        <br />
        <strong>Note:</strong> This should match the actual UDF name in your Snowflake environment.
      </div>
    ),
  },
  currencyTable: {
    tooltip:
      'Purpose: Name of your exchange rates table in Snowflake.\nExample: EXCHANGE_RATES or CURRENCY_RATES.\nNote: This table should contain currency exchange rate data used by the UDF.',
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Name of your exchange rates table in Snowflake.
        <br />
        <strong>Example:</strong> <code>EXCHANGE_RATES</code> or <code>CURRENCY_RATES</code>
        <br />
        <strong>Note:</strong> This table should contain currency exchange rate data used by the UDF.
      </div>
    ),
  },
  currencySchema: {
    tooltip:
      'Purpose: Schema where your currency conversion UDF and rates table are located.\nExample: UTILITY or FINANCE.\nNote: The generated SQL will reference currency artifacts as SCHEMA.UDF_NAME and SCHEMA.TABLE_NAME.',
    content: (
      <div className="field-help">
        <strong>Purpose:</strong> Schema where your currency conversion UDF and rates table are located.
        <br />
        <strong>Example:</strong> <code>UTILITY</code> or <code>FINANCE</code>
        <br />
        <strong>Note:</strong> The generated SQL will reference currency artifacts as <code>SCHEMA.UDF_NAME</code> and <code>SCHEMA.TABLE_NAME</code>.
      </div>
    ),
  },
  autoCorrection: {
    tooltip:
      'What it does: Automatically fixes common SQL syntax and semantic issues in the generated SQL.\n\nWhen to apply: Enable this BEFORE converting your XML to SQL if you want the system to automatically correct issues during conversion. This setting affects the conversion process itself.\n\nWhy to apply: Saves time by resolving frequent SQL errors, making the generated SQL more production-ready for Snowflake. Particularly useful for migrating legacy HANA SQL patterns that may have compatibility issues.\n\nExamples of fixes:\n• Reserved keywords: ORDER becomes `ORDER` (quoted)\n• String concatenation: "text1" + "text2" becomes "text1" || "text2"\n• Function translation: IF(condition, val1, val2) becomes IFF(condition, val1, val2)\n\nConfidence levels: The system applies high-confidence fixes automatically. All corrections are shown in the SQL Preview after conversion.',
    content: (
      <div className="field-help">
        <strong>What it does:</strong> Automatically fixes common SQL syntax and semantic issues in the generated SQL.
        <br /><br />
        <strong>When to apply:</strong> Enable this <strong>BEFORE</strong> converting your XML to SQL if you want the system to automatically correct issues during conversion. This setting affects the conversion process itself, so it must be enabled before clicking "Convert to SQL".
        <br /><br />
        <strong>Why to apply:</strong> Saves time by resolving frequent SQL errors, making the generated SQL more production-ready for Snowflake. Particularly useful for migrating legacy HANA SQL patterns that may have compatibility issues.
        <br /><br />
        <strong>Examples of fixes:</strong>
        <ul style={{ marginTop: '0.5rem', marginBottom: '0.5rem', paddingLeft: '1.5rem' }}>
          <li><strong>Reserved keywords:</strong> <code>ORDER</code> becomes <code>`ORDER`</code> (quoted)</li>
          <li><strong>String concatenation:</strong> <code>"text1" + "text2"</code> becomes <code>"text1" || "text2"</code></li>
          <li><strong>Function translation:</strong> <code>IF(condition, val1, val2)</code> becomes <code>IFF(condition, val1, val2)</code></li>
        </ul>
        <strong>Confidence levels:</strong> The system applies <strong>high-confidence fixes</strong> automatically. All corrections are shown in the SQL Preview after conversion with before/after diffs.
      </div>
    ),
  },
}

function ConfigForm({ config, onConfigChange }) {
  const [schemaOverrides, setSchemaOverrides] = useState(
    Object.entries(config.schema_overrides || {}).map(([key, value]) => ({ key, value }))
  )
  const [showHelp, setShowHelp] = useState(false)

  const updateConfig = (updates) => {
    onConfigChange({ ...config, ...updates })
  }

  const addSchemaOverride = () => {
    const newOverrides = [...schemaOverrides, { key: '', value: '' }]
    setSchemaOverrides(newOverrides)
    updateSchemaOverrides(newOverrides)
  }

  const removeSchemaOverride = (index) => {
    const newOverrides = schemaOverrides.filter((_, i) => i !== index)
    setSchemaOverrides(newOverrides)
    updateSchemaOverrides(newOverrides)
  }

  const updateSchemaOverride = (index, field, value) => {
    const newOverrides = [...schemaOverrides]
    newOverrides[index][field] = value
    setSchemaOverrides(newOverrides)
    updateSchemaOverrides(newOverrides)
  }

  const updateSchemaOverrides = (overrides) => {
    const overridesObj = {}
    overrides.forEach(({ key, value }) => {
      if (key && value) {
        overridesObj[key] = value
      }
    })
    updateConfig({ schema_overrides: overridesObj })
  }

  return (
    <div className="config-form-container">
      <div className="card">
        <div className="config-header">
          <h2>Configuration</h2>
          <button 
            className="help-toggle-btn"
            onClick={() => setShowHelp(!showHelp)}
            title="Toggle help"
          >
            {showHelp ? '−' : '?'}
          </button>
        </div>

        {showHelp && (
          <div className="config-help-overview">
            <h3>About Configuration</h3>
            <p>
              This tool generates SQL files that you execute in Snowflake. The configuration below 
              controls how the SQL is generated to match your Snowflake environment. You don't need 
              to connect to Snowflake here—just configure the settings, generate SQL, then execute 
              it in Snowflake using Snowflake's web UI, SnowSQL, or your preferred tool.
            </p>
            <p>
              <strong>Note:</strong> Most fields have default values and can be left unchanged unless 
              your XML files use specific placeholders or your Snowflake schemas differ from the XML.
            </p>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="client">
            Client
            <span 
              className="help-icon" 
              title={fieldHelpContent.client.tooltip}
            >
              ℹ️
            </span>
          </label>
          {showHelp && fieldHelpContent.client.content}
          <input
            id="client"
            type="text"
            value={config.client || 'PROD'}
            onChange={(e) => updateConfig({ client: e.target.value })}
            placeholder="PROD"
          />
        </div>

        <div className="form-group">
          <label htmlFor="language">
            Language
            <span 
              className="help-icon" 
              title={fieldHelpContent.language.tooltip}
            >
              ℹ️
            </span>
          </label>
          {showHelp && fieldHelpContent.language.content}
          <input
            id="language"
            type="text"
            value={config.language || 'EN'}
            onChange={(e) => updateConfig({ language: e.target.value })}
            placeholder="EN"
          />
        </div>

        <div className="form-section">
          <h3>Target Database</h3>
          
          <div className="form-group">
            <label htmlFor="database_mode">
              Database Mode
            </label>
            <select
              id="database_mode"
              value={config.database_mode || 'snowflake'}
              onChange={(e) => updateConfig({ database_mode: e.target.value })}
            >
              <option value="snowflake">Snowflake</option>
              <option value="hana">SAP HANA</option>
            </select>
            <p className="field-hint">
              Select the target database system for SQL generation. This determines syntax, functions, and data types used in the generated SQL.
            </p>
          </div>

          {config.database_mode === 'hana' && (
            <div className="form-group">
              <label htmlFor="hana_version">
                HANA Version
              </label>
              <select
                id="hana_version"
                value={config.hana_version || '2.0'}
                onChange={(e) => updateConfig({ hana_version: e.target.value })}
              >
                <option value="1.0">HANA 1.0</option>
                <option value="2.0">HANA 2.0</option>
                <option value="2.0_SPS01">HANA 2.0 SPS01</option>
                <option value="2.0_SPS03">HANA 2.0 SPS03</option>
                <option value="2.0_SPS04">HANA 2.0 SPS04</option>
              </select>
              <p className="field-hint">
                Select HANA version for version-specific SQL syntax and features. Older versions may not support all features.
              </p>
            </div>
          )}
        </div>

        <div className="form-section">
          <h3>
            Auto-Correction
            <span 
              className="help-icon" 
              title={fieldHelpContent.autoCorrection.tooltip}
            >
              ℹ️
            </span>
          </h3>
          {showHelp && fieldHelpContent.autoCorrection.content}
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={config.auto_fix || false}
                onChange={(e) => updateConfig({ auto_fix: e.target.checked })}
              />
              <span>Enable auto-correction of SQL issues</span>
            </label>
            <p className="field-hint">
              Automatically fix common SQL issues such as reserved keywords, string concatenation, and function translations.
            </p>
          </div>
        </div>

        <div className="form-group">
          <label>
            Schema Overrides
            <span 
              className="help-icon" 
              title={fieldHelpContent.schemaOverrides.tooltip}
            >
              ℹ️
            </span>
          </label>
          {showHelp && fieldHelpContent.schemaOverrides.content}
          {schemaOverrides.map((override, index) => (
            <div key={index} className="schema-override-row">
              <input
                type="text"
                placeholder="Original schema (e.g., SAPK5D)"
                value={override.key}
                onChange={(e) => updateSchemaOverride(index, 'key', e.target.value)}
              />
              <span>→</span>
              <input
                type="text"
                placeholder="Snowflake schema (e.g., PRODUCTION_DATA)"
                value={override.value}
                onChange={(e) => updateSchemaOverride(index, 'value', e.target.value)}
              />
              <button
                className="remove-override-btn"
                onClick={() => removeSchemaOverride(index)}
                title="Remove this override"
              >
                ×
              </button>
            </div>
          ))}
          <button className="add-override-btn" onClick={addSchemaOverride}>
            + Add Schema Override
          </button>
        </div>

        <div className="form-section">
          <h3>
            Currency Settings
            <span 
              className="help-icon" 
              title={fieldHelpContent.currencyOverview.tooltip}
            >
              ℹ️
            </span>
          </h3>
          {showHelp && fieldHelpContent.currencyOverview.content}
          
          <div className="form-group">
            <label htmlFor="currency_udf">
              UDF Name
              <span 
                className="help-icon" 
                title={fieldHelpContent.currencyUdf.tooltip}
              >
                ℹ️
            </span>
            </label>
            {showHelp && fieldHelpContent.currencyUdf.content}
            <input
              id="currency_udf"
              type="text"
              value={config.currency_udf_name || ''}
              onChange={(e) => updateConfig({ currency_udf_name: e.target.value || null })}
              placeholder="CONVERT_CURRENCY"
            />
          </div>

          <div className="form-group">
            <label htmlFor="currency_table">
              Rates Table
              <span 
                className="help-icon" 
                title={fieldHelpContent.currencyTable.tooltip}
              >
                ℹ️
            </span>
            </label>
            {showHelp && fieldHelpContent.currencyTable.content}
            <input
              id="currency_table"
              type="text"
              value={config.currency_rates_table || ''}
              onChange={(e) => updateConfig({ currency_rates_table: e.target.value || null })}
              placeholder="EXCHANGE_RATES"
            />
          </div>

          <div className="form-group">
            <label htmlFor="currency_schema">
              Schema
              <span 
                className="help-icon" 
                title={fieldHelpContent.currencySchema.tooltip}
              >
                ℹ️
            </span>
            </label>
            {showHelp && fieldHelpContent.currencySchema.content}
            <input
              id="currency_schema"
              type="text"
              value={config.currency_schema || ''}
              onChange={(e) => updateConfig({ currency_schema: e.target.value || null })}
              placeholder="UTILITY"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConfigForm

