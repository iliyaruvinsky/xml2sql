#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project Consistency Validation Script

Validates:
1. Documentation consistency and redundancy
2. Code references and implementations
3. File references exist
4. Method/function calls are implemented
5. Definitions alignment
6. Test artifacts and temporary files
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class ProjectValidator:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.errors = []
        self.warnings = []
        self.info = []

    def log_error(self, category: str, message: str):
        self.errors.append(f"[ERROR] {category}: {message}")

    def log_warning(self, category: str, message: str):
        self.warnings.append(f"[WARN] {category}: {message}")

    def log_info(self, category: str, message: str):
        self.info.append(f"[INFO] {category}: {message}")

    # ========================================================================
    # PART 1: DOCUMENTATION VALIDATION
    # ========================================================================

    def validate_documentation(self):
        """Validate all documentation files for consistency."""
        print("\n" + "="*70)
        print("PART 1: DOCUMENTATION VALIDATION")
        print("="*70)

        # Get all markdown files
        root_docs = list(self.root.glob("*.md"))
        docs_folder = list((self.root / "docs").glob("*.md")) if (self.root / "docs").exists() else []
        all_docs = root_docs + docs_folder

        print(f"\nFound {len(all_docs)} documentation files:")
        print(f"  - Root level: {len(root_docs)}")
        print(f"  - docs/ folder: {len(docs_folder)}")

        # 1. Check for duplicate content
        self._check_duplicate_docs(all_docs)

        # 2. Check for redundant/obsolete files
        self._check_obsolete_docs(root_docs)

        # 3. Check file references
        self._check_file_references(all_docs)

        # 4. Check for circular references
        self._check_circular_references(all_docs)

        # 5. Check for inconsistent information
        self._check_version_consistency(all_docs)

    def _check_duplicate_docs(self, docs: List[Path]):
        """Check for duplicate or highly similar documentation."""
        print("\n--- Checking for duplicate documentation ---")

        # Group by similar names
        name_groups = defaultdict(list)
        for doc in docs:
            base_name = doc.stem.lower()
            # Remove common suffixes
            base_name = re.sub(r'_(summary|report|guide|notes|log)$', '', base_name)
            name_groups[base_name].append(doc)

        for base_name, files in name_groups.items():
            if len(files) > 1:
                self.log_warning("DUPLICATE_NAMES",
                    f"Similar documentation names: {[str(f.name) for f in files]}")

    def _check_obsolete_docs(self, docs: List[Path]):
        """Check for potentially obsolete documentation."""
        print("\n--- Checking for obsolete documentation ---")

        # Files that suggest temporary/testing nature
        temp_patterns = [
            r'test.*\.md$',
            r'.*_test\.md$',
            r'debug.*\.md$',
            r'temp.*\.md$',
            r'tmp.*\.md$',
            r'scratch.*\.md$',
            r'notes.*\.md$',
            r'iteration.*\.md$',
            r'cycle.*\.md$',
        ]

        for doc in docs:
            name_lower = doc.name.lower()
            for pattern in temp_patterns:
                if re.match(pattern, name_lower):
                    self.log_warning("TEMP_DOC",
                        f"Potentially temporary doc: {doc.name}")
                    break

    def _check_file_references(self, docs: List[Path]):
        """Check that all referenced files actually exist."""
        print("\n--- Checking file references ---")

        # Pattern to match file references in markdown
        patterns = [
            r'`([^`]+\.(py|yaml|yml|sql|md|txt))`',  # Inline code
            r'\[.*?\]\(([^)]+\.(py|yaml|yml|sql|md|txt))\)',  # Links
            r'see `?([A-Z_]+\.md)`?',  # "see FILENAME.md"
            r'in `?([a-z_/]+\.py)`?',  # "in path/to/file.py"
        ]

        ref_count = 0
        for doc in docs:
            try:
                content = doc.read_text(encoding='utf-8', errors='ignore')
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        ref_file = match.group(1)
                        ref_count += 1

                        # Try to find the file
                        possible_paths = [
                            self.root / ref_file,
                            self.root / "src" / ref_file,
                            self.root / "docs" / ref_file,
                        ]

                        exists = any(p.exists() for p in possible_paths)
                        if not exists and not ref_file.startswith('http'):
                            self.log_error("MISSING_FILE",
                                f"{doc.name} references missing file: {ref_file}")
            except Exception as e:
                self.log_warning("READ_ERROR", f"Cannot read {doc.name}: {e}")

        print(f"Checked {ref_count} file references")

    def _check_circular_references(self, docs: List[Path]):
        """Check for circular documentation references."""
        print("\n--- Checking for circular references ---")

        # Build reference graph
        refs = defaultdict(set)
        for doc in docs:
            try:
                content = doc.read_text(encoding='utf-8', errors='ignore')
                # Find references to other .md files
                matches = re.finditer(r'(?:see|read|check)\s+`?([A-Z_a-z]+\.md)`?', content, re.IGNORECASE)
                for match in matches:
                    ref_name = match.group(1)
                    refs[doc.name].add(ref_name)
            except:
                pass

        # Check for cycles (simple 2-node cycles for now)
        for doc_name, referenced in refs.items():
            for ref_name in referenced:
                if doc_name in refs.get(ref_name, set()):
                    self.log_warning("CIRCULAR_REF",
                        f"Circular reference: {doc_name} <-> {ref_name}")

    def _check_version_consistency(self, docs: List[Path]):
        """Check for version number consistency."""
        print("\n--- Checking version consistency ---")

        versions = defaultdict(list)
        for doc in docs:
            try:
                content = doc.read_text(encoding='utf-8', errors='ignore')
                # Find version references
                matches = re.finditer(r'v?(\d+\.\d+\.\d+)', content)
                for match in matches:
                    version = match.group(1)
                    versions[version].append(doc.name)
            except:
                pass

        if len(versions) > 1:
            print(f"Found {len(versions)} different version numbers:")
            for version, files in sorted(versions.items()):
                print(f"  v{version}: {len(files)} files")
                if len(files) <= 3:
                    for f in files:
                        print(f"    - {f}")

    # ========================================================================
    # PART 2: CODE VALIDATION
    # ========================================================================

    def validate_code(self):
        """Validate code consistency and implementation."""
        print("\n" + "="*70)
        print("PART 2: CODE VALIDATION")
        print("="*70)

        # 1. Find all Python files
        py_files = list(self.root.glob("src/**/*.py"))
        test_files = list(self.root.glob("tests/**/*.py"))

        print(f"\nFound {len(py_files)} source files, {len(test_files)} test files")

        # 2. Check function/method implementations
        self._check_function_implementations(py_files)

        # 3. Check import statements
        self._check_imports(py_files)

        # 4. Check for duplicate definitions
        self._check_duplicate_definitions(py_files)

        # 5. Validate catalog references
        self._validate_catalog_references()

    def _check_function_implementations(self, py_files: List[Path]):
        """Check that called functions are actually implemented."""
        print("\n--- Checking function implementations ---")

        # Build index of defined functions
        defined_funcs = defaultdict(list)
        called_funcs = defaultdict(list)

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Find function definitions
                for match in re.finditer(r'^def\s+([a-z_][a-z0-9_]*)\s*\(', content, re.MULTILINE):
                    func_name = match.group(1)
                    defined_funcs[func_name].append(str(py_file))

                # Find function calls
                for match in re.finditer(r'([a-z_][a-z0-9_]*)\s*\(', content):
                    func_name = match.group(1)
                    if func_name not in ['if', 'for', 'while', 'def', 'class', 'return', 'print']:
                        called_funcs[func_name].append(str(py_file))

            except Exception as e:
                self.log_warning("READ_ERROR", f"Cannot read {py_file}: {e}")

        # Check for calls to undefined functions (excluding builtins and imports)
        builtins = {'len', 'str', 'int', 'float', 'dict', 'list', 'set', 'tuple',
                    'open', 'range', 'enumerate', 'zip', 'map', 'filter', 'any', 'all',
                    'getattr', 'setattr', 'hasattr', 'isinstance', 'issubclass', 'type'}

        undefined = set(called_funcs.keys()) - set(defined_funcs.keys()) - builtins
        if undefined:
            print(f"Found {len(undefined)} potentially undefined functions (may be imports):")
            for func in sorted(list(undefined)[:10]):  # Show first 10
                print(f"  - {func}")

    def _check_imports(self, py_files: List[Path]):
        """Check for broken import statements."""
        print("\n--- Checking imports ---")

        import_errors = []
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Find local imports (from . or from src)
                local_imports = re.finditer(
                    r'from\s+(\.+[a-z_][a-z0-9_.]*|src\.[a-z_][a-z0-9_.]*)\s+import',
                    content
                )

                for match in local_imports:
                    module_path = match.group(1)
                    # Convert to file path
                    if module_path.startswith('.'):
                        # Relative import - harder to validate
                        pass
                    elif module_path.startswith('src.'):
                        file_path = module_path.replace('.', '/') + '.py'
                        if not (self.root / file_path).exists():
                            # Check if it's a package (__init__.py)
                            pkg_path = module_path.replace('.', '/') + '/__init__.py'
                            if not (self.root / pkg_path).exists():
                                import_errors.append((py_file.name, module_path))

            except Exception as e:
                pass

        if import_errors:
            for file, module in import_errors[:5]:  # Show first 5
                self.log_error("BROKEN_IMPORT", f"{file} imports missing module: {module}")

    def _check_duplicate_definitions(self, py_files: List[Path]):
        """Check for duplicate class/function definitions."""
        print("\n--- Checking for duplicate definitions ---")

        definitions = defaultdict(list)

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Find class definitions
                for match in re.finditer(r'^class\s+([A-Z][a-zA-Z0-9_]*)', content, re.MULTILINE):
                    class_name = match.group(1)
                    definitions[f"class:{class_name}"].append(str(py_file))

                # Find function definitions (top-level only)
                for match in re.finditer(r'^def\s+([a-z_][a-z0-9_]*)\s*\(', content, re.MULTILINE):
                    func_name = match.group(1)
                    if not func_name.startswith('_'):  # Ignore private
                        definitions[f"func:{func_name}"].append(str(py_file))

            except:
                pass

        # Report duplicates
        duplicates = {name: files for name, files in definitions.items() if len(files) > 1}
        if duplicates:
            print(f"Found {len(duplicates)} duplicate definitions:")
            for name, files in list(duplicates.items())[:10]:  # Show first 10
                print(f"  - {name} defined in {len(files)} files")

    def _validate_catalog_references(self):
        """Validate catalog YAML files are referenced correctly."""
        print("\n--- Validating catalog references ---")

        # Check functions.yaml
        functions_yaml = self.root / "src/xml_to_sql/catalog/data/functions.yaml"
        if functions_yaml.exists():
            self.log_info("CATALOG", "functions.yaml exists")
        else:
            self.log_error("MISSING_CATALOG", "functions.yaml not found")

        # Check patterns.yaml
        patterns_yaml = self.root / "src/xml_to_sql/catalog/data/patterns.yaml"
        if patterns_yaml.exists():
            self.log_info("CATALOG", "patterns.yaml exists")
        else:
            self.log_error("MISSING_CATALOG", "patterns.yaml not found")

        # Check if loaders reference these files correctly
        loader_py = self.root / "src/xml_to_sql/catalog/loader.py"
        pattern_loader_py = self.root / "src/xml_to_sql/catalog/pattern_loader.py"

        if loader_py.exists():
            content = loader_py.read_text(encoding='utf-8', errors='ignore')
            if 'functions.yaml' in content:
                self.log_info("CATALOG", "loader.py references functions.yaml")
            else:
                self.log_error("CATALOG_REF", "loader.py doesn't reference functions.yaml")

        if pattern_loader_py.exists():
            content = pattern_loader_py.read_text(encoding='utf-8', errors='ignore')
            if 'patterns.yaml' in content:
                self.log_info("CATALOG", "pattern_loader.py references patterns.yaml")
            else:
                self.log_error("CATALOG_REF", "pattern_loader.py doesn't reference patterns.yaml")

    # ========================================================================
    # PART 3: TEST ARTIFACTS VALIDATION
    # ========================================================================

    def validate_test_artifacts(self):
        """Find and validate test/temporary artifacts."""
        print("\n" + "="*70)
        print("PART 3: TEST ARTIFACTS VALIDATION")
        print("="*70)

        # Find test files in root (should be in tests/ folder)
        root_test_files = list(self.root.glob("test_*.py")) + list(self.root.glob("*_test.py"))

        if root_test_files:
            print(f"\nFound {len(root_test_files)} test files in root directory:")
            for f in root_test_files:
                print(f"  - {f.name}")
                self.log_warning("MISPLACED_TEST", f"Test file in root: {f.name}")
        else:
            print("\nNo test files found in root (good!)")

        # Find temporary SQL files
        temp_sql = list(self.root.glob("test*.sql")) + list(self.root.glob("temp*.sql"))
        if temp_sql:
            print(f"\nFound {len(temp_sql)} temporary SQL files:")
            for f in temp_sql:
                print(f"  - {f.name}")
                self.log_warning("TEMP_FILE", f"Temporary SQL file: {f.name}")

        # Find .pyc and __pycache__
        pycache = list(self.root.glob("**/__pycache__"))
        if pycache:
            self.log_info("CACHE", f"Found {len(pycache)} __pycache__ directories")

    # ========================================================================
    # PART 4: CONFIGURATION VALIDATION
    # ========================================================================

    def validate_configuration(self):
        """Validate configuration files."""
        print("\n" + "="*70)
        print("PART 4: CONFIGURATION VALIDATION")
        print("="*70)

        # Check config files
        config_yaml = self.root / "config.yaml"
        config_example = self.root / "config.example.yaml"

        if config_yaml.exists():
            self.log_info("CONFIG", "config.yaml exists")
        else:
            self.log_warning("CONFIG", "config.yaml not found")

        if config_example.exists():
            self.log_info("CONFIG", "config.example.yaml exists")
        else:
            self.log_error("CONFIG", "config.example.yaml missing (needed for documentation)")

        # Check if they have similar structure
        if config_yaml.exists() and config_example.exists():
            try:
                import yaml
                with open(config_yaml, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                with open(config_example, 'r', encoding='utf-8') as f:
                    example_data = yaml.safe_load(f)

                if config_data and example_data:
                    config_keys = set(config_data.keys())
                    example_keys = set(example_data.keys())

                    missing_in_example = config_keys - example_keys
                    if missing_in_example:
                        self.log_warning("CONFIG_SYNC",
                            f"config.example.yaml missing keys: {missing_in_example}")

                    extra_in_example = example_keys - config_keys
                    if extra_in_example:
                        self.log_info("CONFIG_SYNC",
                            f"config.example.yaml has extra keys: {extra_in_example}")
            except ImportError:
                self.log_warning("VALIDATION", "yaml module not available, skipping config comparison")
            except Exception as e:
                self.log_warning("CONFIG_PARSE", f"Error comparing configs: {e}")

    # ========================================================================
    # MAIN REPORT
    # ========================================================================

    def generate_report(self):
        """Generate final validation report."""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)

        print(f"\nERRORS: {len(self.errors)}")
        for error in self.errors:
            print(f"  {error}")

        print(f"\nWARNINGS: {len(self.warnings)}")
        for warning in self.warnings[:20]:  # Show first 20
            print(f"  {warning}")
        if len(self.warnings) > 20:
            print(f"  ... and {len(self.warnings) - 20} more warnings")

        print(f"\nINFO: {len(self.info)}")
        for info in self.info[:10]:  # Show first 10
            print(f"  {info}")

        # Summary
        print("\n" + "="*70)
        if len(self.errors) == 0:
            print("✅ NO CRITICAL ERRORS FOUND")
        else:
            print(f"❌ {len(self.errors)} CRITICAL ERRORS NEED ATTENTION")

        if len(self.warnings) == 0:
            print("✅ NO WARNINGS")
        else:
            print(f"⚠️  {len(self.warnings)} WARNINGS TO REVIEW")

        print("="*70)

        # Save to file
        report_file = self.root / "VALIDATION_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PROJECT CONSISTENCY VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"ERRORS: {len(self.errors)}\n")
            for error in self.errors:
                f.write(f"  {error}\n")
            f.write(f"\nWARNINGS: {len(self.warnings)}\n")
            for warning in self.warnings:
                f.write(f"  {warning}\n")
            f.write(f"\nINFO: {len(self.info)}\n")
            for info in self.info:
                f.write(f"  {info}\n")

        print(f"\nFull report saved to: {report_file}")

        return len(self.errors) == 0

def main():
    print("="*70)
    print("PROJECT CONSISTENCY VALIDATOR")
    print("="*70)
    print("\nThis script validates:")
    print("  1. Documentation consistency and redundancy")
    print("  2. Code references and implementations")
    print("  3. File references exist")
    print("  4. Method/function calls are implemented")
    print("  5. Configuration alignment")
    print("  6. Test artifacts cleanup")

    validator = ProjectValidator()

    # Run all validations
    validator.validate_documentation()
    validator.validate_code()
    validator.validate_test_artifacts()
    validator.validate_configuration()

    # Generate report
    success = validator.generate_report()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
