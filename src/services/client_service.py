"""
Client Management Service for BananAI
Handles CRUD operations for clients using JSON storage.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClientService:
    """Manages client data with JSON storage."""
    
    def __init__(self, clients_file: Path = None):
        if clients_file is None:
            clients_file = Path("data/clients.json")
        self.clients_file = clients_file
        self.clients_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_clients(self) -> List[Dict[str, Any]]:
        """Load clients from JSON file."""
        if not self.clients_file.exists():
            return []
        try:
            with open(self.clients_file, "r") as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_clients(self, clients: List[Dict[str, Any]]):
        """Save clients to JSON file."""
        with open(self.clients_file, "w") as f:
            json.dump(clients, f, indent=2)
    
    def _generate_client_id(self) -> str:
        """Generate a unique client ID."""
        clients = self._load_clients()
        existing_ids = {c.get("client_id", "") for c in clients}
        counter = 1
        while f"CLI-{counter:06d}" in existing_ids:
            counter += 1
        return f"CLI-{counter:06d}"
    
    def create_client(self, name: str, email: str = "", phone: str = "", 
                     address: str = "", notes: str = "") -> Dict[str, Any]:
        """Create a new client."""
        clients = self._load_clients()
        
        client = {
            "client_id": self._generate_client_id(),
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        clients.append(client)
        self._save_clients(clients)
        return client
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients."""
        return self._load_clients()
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific client by ID."""
        clients = self._load_clients()
        for client in clients:
            if client.get("client_id") == client_id:
                return client
        return None
    
    def update_client(self, client_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a client. Pass fields to update as keyword arguments."""
        clients = self._load_clients()
        
        for client in clients:
            if client.get("client_id") == client_id:
                for key, value in kwargs.items():
                    if key in client:
                        client[key] = value
                client["updated_at"] = datetime.now().isoformat()
                self._save_clients(clients)
                return client
        return None
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client."""
        clients = self._load_clients()
        original_count = len(clients)
        clients = [c for c in clients if c.get("client_id") != client_id]
        
        if len(clients) < original_count:
            self._save_clients(clients)
            return True
        return False
    
    def search_clients(self, query: str) -> List[Dict[str, Any]]:
        """Search clients by name, email, or phone."""
        clients = self._load_clients()
        query_lower = query.lower()
        
        results = []
        for client in clients:
            if (query_lower in client.get("name", "").lower() or
                query_lower in client.get("email", "").lower() or
                query_lower in client.get("phone", "").lower()):
                results.append(client)
        
        return results
