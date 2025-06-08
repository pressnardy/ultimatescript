import datetime
from core import apirequests, settings, util

last_candle = apirequests.get_candles('30m', 2, 'BTCUSDT')[-1]
# print(last_candle)
candle_time = last_candle['time']
current_time = datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000
print(current_time)
uptime_duration = 30
is_active = util.is_active_signal(candle_time, uptime_duration)
print(is_active)

