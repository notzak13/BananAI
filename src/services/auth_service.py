"""
Authentication Service for BananAI
Handles user registration, login, and password hashing with Hardcoded Admin Bypass.
"""
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class AuthService:
    """Manages user authentication with hashed passwords stored in JSON."""
    
    def __init__(self, users_file: Path = None):
        if users_file is None:
            users_file = Path("data/users.json")
        self.users_file = users_file
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        # Ensure file exists at startup
        if not self.users_file.exists():
            self._save_users({})
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from JSON with Google-grade structural validation."""
        if not self.users_file.exists():
            return {}
        try:
            with open(self.users_file, "r") as f:
                data = json.load(f)
                
                # DATA INTEGRITY GUARD: Convert list-style legacy data to dict
                if isinstance(data, list):
                    new_dict = {}
                    for item in data:
                        if isinstance(item, dict) and "username" in item:
                            u_name = item.pop("username")
                            new_dict[u_name] = item
                    return new_dict
                
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, Exception):
            return {}
    
    def _save_users(self, users: Dict[str, Dict[str, Any]]):
        """Save users to JSON file."""
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against salt:hash string."""
        try:
            if ":" not in hashed:
                return False
            salt, stored_hash = hashed.split(":", 1)
            hash_obj = hashlib.sha256()
            hash_obj.update((password + salt).encode('utf-8'))
            return hash_obj.hexdigest() == stored_hash
        except Exception:
            return False
    
    def register(self, username: str, password: str, email: str = "", full_name: str = ""):
        """Register a new user in the persistent database."""
        users = self._load_users()
        
        if username in users or username.lower() == "camel123":
            return False, "Username already exists or is reserved"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        users[username] = {
            "password_hash": self._hash_password(password),
            "email": email,
            "full_name": full_name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_users(users)
        return True, "Registration successful"
    
    def login(self, username: str, password: str):
        """
        Authenticate a user with a Hardcoded Admin Bypass.
        Returns (success, message)
        """
        # --- 👑 THE SOVEREIGN BYPASS (HARDCODED ADMIN) ---
        # This allows you into the system regardless of what is in users.json
        ADMIN_USER = "Camel123"
        ADMIN_PASS = "BananaKing2026" # Change this as needed!

        if username == ADMIN_USER and password == ADMIN_PASS:
            return True, f"Welcome back, Commander {username}."

        # --- REGULAR DATABASE AUTHENTICATION ---
        users = self._load_users()
        
        if not isinstance(users, dict):
            return False, "Internal System Error: User Database Corrupted"
            
        if username not in users:
            return False, "Invalid username or password"
        
        user_data = users[username]
        
        if not isinstance(user_data, dict) or "password_hash" not in user_data:
            return False, "User data corrupted"
            
        if not self._verify_password(password, user_data["password_hash"]):
            return False, "Invalid username or password"
        
        return True, "Login successful"
    
    def user_exists(self, username: str) -> bool:
        """Check if a username exists."""
        if username.lower() == "camel123": return True
        users = self._load_users()
        return username in users if isinstance(users, dict) else False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve profile data without exposing sensitive hashes."""
        if username == "Camel123":
            return {
                "full_name": "ISAAK YAKOVSON (ADMIN)",
                "email": "admin@bananai.com",
                "role": "Superuser"
            }
            
        users = self._load_users()
        if not isinstance(users, dict) or username not in users:
            return None
            
        user_info = users[username].copy()
        user_info.pop("password_hash", None)
        return user_info