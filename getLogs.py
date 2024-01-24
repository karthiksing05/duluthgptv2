import redis
import os
import datetime

r = redis.Redis(
    host='redis-12355.c325.us-east-1-4.ec2.cloud.redislabs.com',
    port=12355,
    password=os.getenv("REDIS_PASSWD")
)

for xKey in r.scan_iter("userExchange-*"):
    try:
        with open(f"logs\\logAt{datetime.datetime.now().strftime('%Y-%m-%d')}.txt", "w+") as f:
            res = dict(r.hgetall(xKey))
            strRes = {}
            for key, val in res.items():
                strRes[str(key.decode('utf-8'))] = str(val.decode('utf-8'))
                f.write(xKey.decode('utf-8') + ": " + str(strRes))
            r.delete(xKey)
    except UnicodeEncodeError:
        r.delete(xKey)
