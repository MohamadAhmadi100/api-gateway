from collections import deque
import copy
from source.helpers.mongo_db import MongoDb


class Saga:
    def __init__(self):
        self.item_id = None
        self.stack = deque()

    @staticmethod
    def startup_action():
        with MongoDb() as client:
            result = client.saga_collection.find()
            return result

    def compensate(self):
        return self.stack

    def add(self, item: dict):
        new_item = copy.deepcopy(item)
        for key, value in new_item.items():
            new_item[key]["action"] = new_item[key]["action"] + "_rollback"
        self.stack.append(new_item)
        with MongoDb() as client:
            if self.item_id:
                result = client.saga_collection.update_one({"_id": self.item_id},
                                                           {"$push": {"actions": new_item}})
            else:
                result = client.saga_collection.insert_one({"actions": [new_item]})
                self.item_id = result.inserted_id

    def remove(self, services: list):
        temp = self.stack.pop()
        item = {key: temp[key] for key in temp if key not in services}
        if item:
            self.stack.append(item)
            with MongoDb() as client:
                client.saga_collection.update_one({"_id": self.item_id},
                                                  {"$set": {"actions." + str(len(self.stack) - 1): item}})

    def finish(self):
        with MongoDb() as client:
            client.saga_collection.delete_one({"_id": self.item_id})
        self.stack.clear()
        self.item_id = None
