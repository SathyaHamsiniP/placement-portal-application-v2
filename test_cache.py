"""
test_cache.py
------------
Verifies connection to Redis DB 3 and that keys can be read, written, and deleted.
Run:
    python test_cache.py
"""

import redis

try:
    client = redis.Redis(host='localhost', port=6379, db=3, decode_responses=True)
    
    # Test set/get
    client.set("test_key", "caching_works")
    val = client.get("test_key")
    print(f"Redis write/read value: {val}")
    assert val == "caching_works", "Value does not match!"
    
    # Test delete
    client.delete("test_key")
    val_after = client.get("test_key")
    print(f"Value after deletion: {val_after}")
    assert val_after is None, "Deletion failed!"
    
    print("\nRedis Cache DB connection and test operations: OK! ✅")
except Exception as e:
    print(f"Redis caching test failed: {e}")
