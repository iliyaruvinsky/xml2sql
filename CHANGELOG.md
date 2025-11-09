# Changelog

All notable changes to the XML to SQL Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-09

### Added
- **XML Validation**: Early detection of non-HANA XML files with clear error messages
- **Auto-Correction Engine**: Automatic fixing of common SQL issues (reserved keywords, string concatenation, function translation)
- **Error Log Display**: View detailed error messages for failed conversions in History tab
- **Improved Error Messages**: All error messages now specify expected XML type (SAP HANA calculation view)
- **Version Display**: Application version now shown in footer (v0.2.0)
- **Installation Guide**: Complete installation instructions for client deployment
- **Distribution Package**: Ready-to-use zip package for client installation

### Changed
- **UI Improvements**: 
  - Reorganized button placement in History tab for better alignment
  - Auto-Correction moved to appear before conversion (more visible)
  - Improved text placement and layout consistency
- **Error Handling**: Enhanced error messages with detailed guidance
- **Configuration UI**: Added comprehensive help tooltips and explanations

### Fixed
- Fixed bug in expression validation (Predicate attribute access)
- Fixed text placement issues in configuration form
- Improved button alignment in History tab

## [0.1.0] - Initial Release

### Added
- Core XML to SQL conversion functionality
- Web GUI with single file and batch conversion
- Conversion history with SQLite database
- SQL validation system (Phases 1, 2, 3)
- Validation logs display
- History management (multi-select, bulk deletion)
- Configuration UI with schema overrides and currency settings

