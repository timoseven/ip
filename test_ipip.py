#!/usr/bin/env python3
# Test script for ipip-datx library

from datx import City
import sys

# Test the ipip-datx library
print("Testing ipip-datx library...")

try:
    # Initialize the database
    db = City('./db/ipip/ipipfree.ipdb')
    print("✓ Database initialized successfully")
    
    # Test IP: 202.96.209.5 (Shanghai Telecom)
    ip = "202.96.209.5"
    print(f"\nTesting IP: {ip}")
    
    # Try different methods to get data
    print("\n1. Testing find() method:")
    try:
        result = db.find(ip)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error with find(): {e}")
    
    print("\n2. Testing __getitem__ method:")
    try:
        result = db[ip]
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error with __getitem__: {e}")
    
    print("\n3. Testing available attributes:")
    print(f"Available attributes: {dir(db)}")
    
    # Check if there's a different method name
    print("\n4. Testing other possible methods:")
    for attr in dir(db):
        if not attr.startswith('_') and callable(getattr(db, attr)):
            print(f"  - {attr}")
    
    # Try to get all available methods
    print("\n5. Testing get() method if exists:")
    if hasattr(db, 'get'):
        try:
            result = db.get(ip)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error with get(): {e}")
            
    print("\n6. Testing raw data access:")
    # Check if we can access the database directly
    print(f"Database path: {db._database}")
    print(f"Database type: {type(db)}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ Test completed successfully")
