"""Test validation in the actual application."""

import json
import requests
from pathlib import Path

# Test file - try a more complex one
xml_file = Path("Source (XML Files)") / "Sold_Materials_PROD.XML"

if not xml_file.exists():
    print(f"File not found: {xml_file}")
    print(f"Trying absolute path...")
    xml_file = xml_file.resolve()
    if not xml_file.exists():
        print(f"Still not found. Available files:")
        source_dir = Path("Source (XML Files)")
        if source_dir.exists():
            for f in source_dir.glob("*.XML"):
                print(f"  - {f}")
        exit(1)

print(f"Testing validation with file: {xml_file.name}")
print("=" * 60)

# Prepare request
files = {"file": (xml_file.name, open(str(xml_file), "rb"), "application/xml")}
data = {"config_json": "{}"}

try:
    # Make API call
    response = requests.post("http://localhost:8000/api/convert/single", files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        exit(1)
    
    result = response.json()
    
    # Check validation results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    if "validation" in result:
        validation = result["validation"]
        print(f"✓ Validation present: Yes")
        print(f"✓ Validation valid: {validation.get('is_valid', 'N/A')}")
        print(f"✓ Errors: {len(validation.get('errors', []))}")
        print(f"✓ Warnings: {len(validation.get('warnings', []))}")
        print(f"✓ Info messages: {len(validation.get('info', []))}")
        
        # Show errors
        if validation.get("errors"):
            print("\n" + "-" * 60)
            print("ERRORS:")
            print("-" * 60)
            for i, error in enumerate(validation["errors"][:5], 1):
                print(f"{i}. [{error['code']}] {error['message']}")
                if error.get("line_number"):
                    print(f"   Line: {error['line_number']}")
        
        # Show warnings
        if validation.get("warnings"):
            print("\n" + "-" * 60)
            print("WARNINGS (first 10):")
            print("-" * 60)
            for i, warning in enumerate(validation["warnings"][:10], 1):
                print(f"{i}. [{warning['code']}] {warning['message']}")
                if warning.get("line_number"):
                    print(f"   Line: {warning['line_number']}")
        
        # Show info
        if validation.get("info"):
            print("\n" + "-" * 60)
            print("INFO MESSAGES (first 5):")
            print("-" * 60)
            for i, info in enumerate(validation["info"][:5], 1):
                print(f"{i}. [{info['code']}] {info['message']}")
    else:
        print("✗ Validation not present in response")
        print("Response keys:", list(result.keys()))
    
    # Show conversion status
    print("\n" + "=" * 60)
    print("CONVERSION STATUS")
    print("=" * 60)
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Scenario ID: {result.get('scenario_id', 'N/A')}")
    print(f"Warnings (legacy): {len(result.get('warnings', []))}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server at http://localhost:8000")
    print("Make sure the server is running with: python run_server.py")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

