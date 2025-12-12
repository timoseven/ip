#!/usr/bin/env python3
# Debug script for ipip-datx library

import os
import sys
from datx import City

# Check if the database file exists and has content
print("Checking database file...")
db_path = './db/ipip/ipipfree.ipdb'
if os.path.exists(db_path):
    file_size = os.path.getsize(db_path)
    print(f"✓ Database file exists: {db_path}")
    print(f"  File size: {file_size:,} bytes")
    if file_size < 1000000:  # Less than 1MB, might be corrupted
        print(f"⚠️  Warning: Database file is very small ({file_size} bytes)")
else:
    print(f"✗ Database file not found: {db_path}")
    sys.exit(1)

try:
    print("\nInitializing database...")
    db = City(db_path)
    print("✓ Database initialized successfully")
    
    # Try to get database information
    print("\nDatabase information:")
    print(f"  Database type: {type(db)}")
    print(f"  Database attributes: {[attr for attr in dir(db) if not attr.startswith('_')]}")
    
    # Test with different IPs
    test_ips = [
        "202.96.209.5",  # Shanghai Telecom
        "8.8.8.8",       # Google DNS
        "114.114.114.114", # China DNS
        "192.168.1.1",   # Private IP
        "::1"             # IPv6 localhost
    ]
    
    for ip in test_ips:
        print(f"\nTesting IP: {ip}")
        try:
            result = db.find(ip)
            print(f"  Result: {result}")
            print(f"  Result type: {type(result)}")
            
            # Try to access data attributes directly if result is an object
            if result and not isinstance(result, dict) and hasattr(result, '__dict__'):
                print(f"  Result attributes: {result.__dict__}")
                
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Try to check the library version and other details
    print("\nLibrary information:")
    print(f"  Python version: {sys.version}")
    print(f"  datx module path: {os.path.dirname(sys.modules['datx'].__file__)}")
    
    # Check if there's a different way to use the library
    print("\nTrying alternative usage...")
    
    # Try to check the database structure
    print("\nChecking database structure...")
    # Look for any methods that might give more information
    for attr in dir(db):
        if not attr.startswith('_') and callable(getattr(db, attr)):
            print(f"  Method: {attr}")
            try:
                if attr != 'find':
                    result = getattr(db, attr)()
                    print(f"    Result: {result}")
            except Exception as e:
                print(f"    Error: {e}")
    
except Exception as e:
    print(f"\n✗ Initialization error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nDebug completed!")
