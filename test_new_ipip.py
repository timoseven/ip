#!/usr/bin/env python3
# Test script for ipip-ipdb library

import os
import sys
from ipdb import City

# Check if the database file exists
db_path = './db/ipip/ipipfree.ipdb'
print(f"Checking database file: {db_path}")
if os.path.exists(db_path):
    file_size = os.path.getsize(db_path)
    print(f"✓ Database file exists")
    print(f"  File size: {file_size:,} bytes")
else:
    print(f"✗ Database file not found")
    sys.exit(1)

try:
    print("\nInitializing database...")
    db = City(db_path)
    print(f"✓ Database initialized successfully")
    print(f"  Database type: {type(db)}")
    print(f"  Available methods: {[m for m in dir(db) if not m.startswith('_')]}")
    
    # Test with different IPs
    test_ips = ["202.96.209.5", "8.8.8.8", "114.114.114.114"]
    for ip in test_ips:
        print(f"\nTesting IP: {ip}")
        try:
            # Try find with language parameter
            result = db.find(ip, "CN")
            print(f"  find(ip, 'CN') result: {result}")
            print(f"  Result type: {type(result)}")
            
            # Check if result is a tuple or list
            if isinstance(result, (list, tuple)):
                print(f"  Result items: {[item for item in result]}")
            
            # Try find_map method
            result_map = db.find_map(ip, "CN")
            print(f"  find_map(ip, 'CN') result: {result_map}")
            print(f"  Result map type: {type(result_map)}")
            
            # Try find_info method
            result_info = db.find_info(ip, "CN")
            print(f"  find_info(ip, 'CN') result: {result_info}")
            print(f"  Result info type: {type(result_info)}")
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ Test completed")
