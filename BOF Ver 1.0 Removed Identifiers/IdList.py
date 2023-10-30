import os
import json
#class that helps detirmine the first correct answer
class IdList:
    def __init__(self, filename):
        self.filename = filename
        self.data = {"ids": []}
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as file:
                loaded_data = json.load(file)
                if "ids" in loaded_data:
                    self.data["ids"] = loaded_data["ids"]
        except json.JSONDecodeError:
            self.data = {"ids": []}

    def save(self):
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                data["ids"] = self.data["ids"]
        except json.JSONDecodeError:
            data = {"ids": self.data["ids"]}

        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def add_id(self, id):
        if id not in self.data["ids"]:
            self.data["ids"].append(id)
            self.save()

    def remove_id(self, id):
        if id in self.data["ids"]:
            self.data["ids"].remove(id)
            self.save()

    def get_first(self):
        return self.data["ids"][0] if self.data["ids"] else None
    
    def get_size(self):
        return len(self.data["ids"])

    def __repr__(self):
        return str(self.data["ids"])