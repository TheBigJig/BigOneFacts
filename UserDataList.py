import os
import json
class UserDataList:
    def __init__(self, filename):
        self.filename = filename
        self.data = {"users": []}
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as file:
                loaded_data = json.load(file)
                if "users" in loaded_data:
                    self.data["users"] = loaded_data["users"]
        except json.JSONDecodeError:
            self.data = {"users": []}

    def save(self):
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                data["users"] = self.data["users"]
        except json.JSONDecodeError:
            data = {"users": self.data["users"]}
        
        with open(self.filename, 'w') as file:
            json.dump(data, file)
            
    def add_user(self, user_id):
        user = {"id": user_id, "wins": 0, "coins": 0, "plays": 0}
        self.data["users"].append(user)
        self.save()

    def find_user(self, user_id):
        for user in self.data["users"]:
            if user["id"] == user_id:
                return user
        return None

    def update_user(self, user_id, wins=None, coins=None, plays=None):
        user = self.find_user(user_id)
        if user is not None:
            if wins is not None:
                user["wins"] = wins
            if coins is not None:
                user["coins"] = coins
            if plays is not None:
                user["plays"] = plays
            self.save()

    def __repr__(self):
        return str(self.data["users"])