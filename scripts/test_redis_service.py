from app.services.redis.redis_client import redis_client

redis_client.set("test_key", "hello_redis")

value = redis_client.get("test_key")

print("Redis Value:", value)