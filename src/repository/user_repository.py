import json
import hashlib
import os
from datetime import datetime

class UserRepository:
    def __init__(self, file_path="data/users.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            # Standardizing Admin credentials
            admin_pw = self._hash_password("zak123!")
            initial_users = {
                "admin": {
                    "password": admin_pw,
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }
            }
            with open(self.file_path, "w") as f:
                json.dump(initial_users, f, indent=4)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """Returns the user data dict if success, else None."""
        if not os.path.exists(self.file_path): return None
        
        with open(self.file_path, "r") as f:
            users = json.load(f)
        
        user_data = users.get(username)
        if user_data and user_data["password"] == self._hash_password(password):
            return user_data # Now returns the whole object (role, etc.)
        return None

    def register(self, username, password, role="buyer"):
        """Registers a new operator or client with a specific role."""
        with open(self.file_path, "r") as f:
            users = json.load(f)
            
        if username in users: 
            return False
            
        users[username] = {
            "password": self._hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.file_path, "w") as f:
            json.dump(users, f, indent=4)
        return True

    def get_all_users(self):
        """Useful for the Admin Dashboard Client Registry."""
        with open(self.file_path, "r") as f:
            return json.load(f)