import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


DATA_FILE = Path(__file__).resolve().parent / 'instance' / 'mongodb_canteen.json'
COLLECTIONS = ('users', 'menu_items', 'orders')


def parse_datetime(value):
    if not isinstance(value, str):
        return value
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value


def prepare_documents(data):
    data = deepcopy(data)

    users_by_id = {user['_id']: user for user in data.get('users', [])}

    for collection in COLLECTIONS:
        for doc in data.get(collection, []):
            if 'created_at' in doc:
                doc['created_at'] = parse_datetime(doc['created_at'])

    for order in data.get('orders', []):
        user = users_by_id.get(order.get('user_id'))
        if user and 'user_name' not in order:
            order['user_name'] = user.get('name', '')
        for item in order.get('items', []):
            if 'name' not in item and 'menu_item_name' in item:
                item['name'] = item['menu_item_name']

    return data


def main():
    load_dotenv()
    mongo_uri = os.environ['MONGO_URI']

    with DATA_FILE.open(encoding='utf-8') as f:
        data = prepare_documents(json.load(f))

    client = MongoClient(mongo_uri)
    db = client.get_default_database()

    for collection in COLLECTIONS:
        db[collection].delete_many({})
        docs = data.get(collection, [])
        if docs:
            db[collection].insert_many(docs)
        print(f'{collection}: imported {len(docs)} documents')


if __name__ == '__main__':
    main()
