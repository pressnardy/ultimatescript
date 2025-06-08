import time
from datetime import datetime, timezone

system_time = time.time()
utc_time = datetime.utcnow().timestamp()

# print(f"System time: {system_time}")
print(f"UTC time: {utc_time}")
current_time = datetime.now(timezone.utc).timestamp()
# print(f"Difference: {system_time - utc_time} seconds")
print(f".now: {current_time}")


