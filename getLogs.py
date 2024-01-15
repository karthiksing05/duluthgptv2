import redis
import os

r = redis.Redis(
    host='redis-12355.c325.us-east-1-4.ec2.cloud.redislabs.com',
    port=12355,
    password=os.getenv("REDIS_PASSWD")
)

for xKey in r.scan_iter("userExchange-*"):
    res = dict(r.hgetall(xKey))
    strRes = {}
    for key, val in res.items():
        strRes[str(key.decode('utf-8'))] = str(val.decode('utf-8'))
    with open(f"logs\\{xKey.decode('utf-8')}.txt", "w+") as f:
        f.write(str(strRes))
    r.delete(xKey)