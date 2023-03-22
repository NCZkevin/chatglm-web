import time
from tinydb import TinyDB, Query

class MessageStore:
    def __init__(self, db_path, table_name, max_size=100000):
        self.db = TinyDB(db_path)
        self.table = self.db.table(table_name)
        self.max_size = max_size

    def set(self, key, value):
        if len(self.table) >= self.max_size:
            self._delete_oldest()
        self.table.insert({'key': key, 'value': value, 'timestamp': time.time()})

    def get_from_key(self, key):
        query = Query()
        result = self.table.get(query.key == key)
        if result is None:
            return None
        return result['value']

    def _delete_oldest(self):
        records = self.table.all()
        if len(records) >= self.max_size:
            oldest_record = sorted(records, key=lambda r: r['timestamp'])[0]
            self.table.remove(doc_ids=[oldest_record.doc_id])
