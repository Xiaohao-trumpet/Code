import datetime
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Persona:
    persona_id: str
    name: str
    description: str
    system_prompt: str
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    @property
    def id(self) -> str:
        """提供id作为persona_id的别名，确保与新接口兼容"""
        return self.persona_id

    @classmethod
    def from_dict(cls, persona_id: str, data: Dict[str, Any]) -> 'Persona':
        return cls(
            persona_id=persona_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            created_at=data.get("created_at", datetime.datetime.now().isoformat())
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at
        } 