import os
import logging
import datetime
from typing import Dict, List

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directories exist
CHATS_DIR = os.path.join(DATA_DIR, "chats")
USERS_DIR = os.path.join(DATA_DIR, "users")
PERSONAS_DIR = os.path.join(DATA_DIR, "personas")

for directory in [CHATS_DIR, USERS_DIR, PERSONAS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Ollama configuration
OLLAMA_CONFIG = {
    "default_model": "deepseek-r1:7b",
    "available_models": ["deepseek-r1:7b"],  # Can be expanded later
    "ollama_host": "http://localhost:11434",  # For local development
    # "ollama_host": "SERVER_URL_PLACEHOLDER",  # For production deployment
}

# UI Configuration
UI_CONFIG = {
    "page_title": "晓昊助手",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Default personas dictionary
PERSONAS_DATA = {
    "default": {
        "name": "通用助手",
        "description": "一个通用的AI助手，可以回答各种问题。",
        "system_prompt": "你是一个乐于助人的AI助手。",
    },
    "medical": {
        "name": "医疗助手",
        "description": "专注于医疗健康领域的AI助手。",
        "system_prompt": "你是一个医疗领域的AI助手，提供健康相关的信息。注意：你不应该提供医疗诊断或治疗建议，仅提供一般性的医疗信息。",
    },
    "legal": {
        "name": "法律助手",
        "description": "专注于法律领域的AI助手。",
        "system_prompt": "你是一个法律领域的AI助手，提供法律相关的信息。注意：你不应该提供具体的法律建议，仅提供一般性的法律信息。",
    }
}

def get_default_personas():
    """返回默认角色列表，避免循环导入"""
    from app.models.persona import Persona
    
    return [
        Persona(
            persona_id=persona_id,
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            created_at=datetime.datetime.now().isoformat()
        )
        for persona_id, data in PERSONAS_DATA.items()
    ]

# LLM options
THINKING_MODE_OPTIONS = {
    "normal": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "num_predict": 1024,
    },
    "deep": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "num_predict": 2048,  # Generate longer responses
    }
}

# Logging configuration
def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(BASE_DIR, "app.log"))
        ]
    )
    return logging.getLogger("xiaohaochat") 