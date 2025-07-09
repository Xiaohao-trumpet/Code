import uuid
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Chat:
    chat_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        return cls(
            chat_id=data.get("chat_id", str(uuid.uuid4())),
            user_id=data.get("metadata", {}).get("user_id", ""),
            messages=data.get("messages", []),
            metadata=data.get("metadata", {}),
            updated_at=data.get("updated_at", datetime.datetime.now().isoformat())
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chat_id": self.chat_id,
            "messages": self.messages,
            "metadata": self.metadata,
            "updated_at": self.updated_at
        } 