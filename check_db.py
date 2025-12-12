#!/usr/bin/env python3
# Check ipip database file structure

import os

def bytes2long(a, b, c, d):
    """Convert 4 bytes to a long integer"""
    return (a << 24) | (b << 16) | (c << 8) | d

def convert(b):
    """Convert byte to integer"""
    return b if isinstance(b, int) else ord(b)

db_path = './db/ipip/ipipfree.ipdb'

# Read the first 4 bytes to get indexSize
with open(db_path, 'rb') as f:
    header = f.read(4)
    data = f.read()

indexSize = bytes2long(header[0], header[1], header[2], header[3])
file_size = os.path.getsize(db_path)

print(f"Database file size: {file_size:,} bytes")
print(f"Index size: {indexSize:,} bytes")
print(f"Data size: {len(data):,} bytes")

# Calculate high value for binary search
high = int((indexSize - 262144 - 262148) / 9) - 1
print(f"\nBisection search parameters:")
print(f"  High value: {high}")
print(f"  Calculation: (indexSize - 262144 - 262148) / 9 - 1")
print(f"              = ({indexSize:,} - 262,144 - 262,148) / 9 - 1")
print(f"              = ({indexSize - 262144 - 262148:,}) / 9 - 1")
print(f"              = {int((indexSize - 262144 - 262148) / 9):,} - 1")

# Check if high is negative (invalid)
if high < 0:
    print(f"\n❌ ERROR: High value is negative ({high}), binary search will not execute!")
    print("This means the database file format is incompatible with the library.")
    
    # Check if the file is a gzip archive
    print(f"\nChecking if file is a gzip archive...")
    with open(db_path, 'rb') as f:
        magic = f.read(2)
    if magic == b'\x1f\x8b':
        print("❌ The file is a gzip archive, but the library expects an uncompressed file!")
    else:
        print(f"File magic bytes: {magic.hex()} (not gzip)")

# Try to extract more information
print(f"\nDatabase header analysis:")
print(f"  First 10 bytes: {header.hex()}")

# Check if the file might be corrupted
if file_size < 1000000:
    print(f"\n⚠️  Warning: Database file is very small ({file_size} bytes)")
    print("It might be corrupted or in an incompatible format.")
