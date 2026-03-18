import redis
import json
import time

# Diagnostic script to verify Redis Pub/Sub directly
REDIS_URL = "redis://localhost:6379" # Default, update if needed

def test_listener():
    print(f"Connecting to Redis at {REDIS_URL}...")
    try:
        r = redis.from_url(REDIS_URL)
        pubsub = r.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("market:stream")
        print("Subscribed to market:stream. Waiting for messages (10s)...")
        
        start = time.time()
        count = 0
        while time.time() - start < 10:
            msg = pubsub.get_message()
            if msg and msg['type'] == 'message':
                data = json.loads(msg['data'])
                print(f"Received message: Type={data.get('type')}, Symbols={len(data.get('data', []))}")
                count += 1
            time.sleep(0.1)
        
        if count == 0:
            print("FAILURE: No messages received in 10 seconds.")
        else:
            print(f"SUCCESS: Received {count} messages.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_listener()
