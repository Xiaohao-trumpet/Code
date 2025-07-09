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