import redis
from django.conf import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

DECREMENT_STOCK_LUA = """
local stock_key = KEYS[1]
local current_stock = tonumber(redis.call('get', stock_key))

if current_stock == nil or current_stock <= 0 then
    return 0
end

redis.call('decr', stock_key)
return 1
"""

def reserve_flash_sale_item(sale_id: int) -> bool:
    """
    Attempts to atomically decrement stock in Redis.
    Returns True if stock was secured, False if sold out.
    """
    stock_key = f"flash_sale:{sale_id}:stock"
    result = r.eval(DECREMENT_STOCK_LUA, 1, stock_key)
    return bool(result)