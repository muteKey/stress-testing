from app.db import get_db
import redis
from datetime import datetime, timedelta
import math
import random

class Repository:
    def __init__(self):
        self.cache = redis.Redis(host='redis', port=6379)
    
    def save_request(self, request):
        db = get_db()
        try:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            db.execute("INSERT INTO request (url, body, method, timestamp) VALUES (?, ?, ?, ?)",
                (request.url,request.data, request.method, dt_string)
            )
            db.commit()
        except db.IntegrityError:
            error = f"Cannot save request"

    def get_metrics(self, request):
        key = request.path
        ttl = self.cache.ttl(key)
        (value, delta) = self.cache.get(key)
        now = datetime.now()
        expiry = now + timedelta(seconds=ttl)
        random_expiry = delta * math.log(random(0, 1))
        if not value or now - random_expiry > expiry:
            start = datetime.now()
            metrics = self.fetch_metrics(request)
            delta = datetime.timestamp(datetime.now() - start) 
            self.cache.set(key, (metrics, delta))
        return value


    def fetch_metrics(self, request):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM metric where url_path=?", (request.path,))
        rows = cursor.fetchall()
        if len(rows):
            return rows[0]
        return None
