import uuid
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class User:
    """User model representing a registered user."""
    
    username: str
    password: str  # In production, store password hash instead
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            username=data.get("username", ""),
            password=data.get("password", ""),
            user_id=data.get("user_id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.datetime.now().isoformat())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to a dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "created_at": self.created_at
        } 