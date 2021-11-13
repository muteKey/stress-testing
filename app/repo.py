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
        delta_key = key + '_delta'

        if not self.cache.exists(key):
            self.__cache(request)
        ttl = self.cache.ttl(key)
        value = int(self.cache.get(key)) if self.cache.get(key) else 0
        delta = float(self.cache.get(delta_key)) if self.cache.get(delta_key) else 0

        now = datetime.now()
        expiry = now + timedelta(seconds=ttl)
        random_expiry = datetime.fromtimestamp(delta * math.log(random.random()))

        new_delta = (now - random_expiry).total_seconds()
        new_delta = datetime.fromtimestamp(new_delta)

        if not value or new_delta > expiry:
            self.__cache(request)
        return value

    def __cache(self, request):
        key = request.path
        delta_key = key + '_delta'

        start = datetime.now()
        metrics = self.fetch_metrics(request)
        delta = (datetime.now() - start).total_seconds()
        
        self.cache.set(key, metrics['metric'])
        self.cache.set(delta_key, delta)

    def fetch_metrics(self, request):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM metric where url_path=?", (request.path,))
        rows = cursor.fetchall()
        if len(rows):
            return rows[0]
        return None
