import os
import json
import logging
from typing import Dict, List, Any, Optional

from app.config import USERS_DIR, CHATS_DIR, PERSONAS_DIR
from app.models.user import User
from app.models.chat import Chat
from app.models.persona import Persona

logger = logging.getLogger("xiaohaochat.storage")

class FileStorage:
    """文件存储实现类，用于处理用户、聊天记录和角色等数据的存储和读取"""

    @staticmethod
    def save_user(user: User) -> bool:
        """保存用户数据到文件
        
        Args:
            user: 用户对象
            
        Returns:
            保存成功返回True，否则返回False
        """
        try:
            user_file = os.path.join(USERS_DIR, f"{user.username}.json")
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user.to_dict(), f, ensure_ascii=False, indent=4)
            logger.info(f"用户保存成功: {user.username}")
            return True
        except Exception as e:
            logger.error(f"保存用户数据失败: {str(e)}")
            return False

    @staticmethod
    def load_user(username: str) -> Optional[User]:
        """通过用户名加载用户数据
        
        Args:
            username: 用户名
            
        Returns:
            如果用户存在，返回用户对象，否则返回None
        """
        user_file = os.path.join(USERS_DIR, f"{username}.json")
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    return User.from_dict(user_data)
            except Exception as e:
                logger.error(f"加载用户数据失败: {str(e)}")
        return None

    @staticmethod
    def user_exists(username: str) -> bool:
        """检查用户是否存在
        
        Args:
            username: 用户名
            
        Returns:
            用户存在返回True，否则返回False
        """
        user_file = os.path.join(USERS_DIR, f"{username}.json")
        return os.path.exists(user_file)

    @staticmethod
    def save_chat(chat: Chat) -> bool:
        """保存聊天记录到文件
        
        Args:
            chat: 聊天对象
            
        Returns:
            保存成功返回True，否则返回False
        """
        try:
            chat_file = os.path.join(CHATS_DIR, f"{chat.chat_id}.json")
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat.to_dict(), f, ensure_ascii=False, indent=4)
            logger.info(f"聊天记录保存成功: {chat.chat_id}")
            return True
        except Exception as e:
            logger.error(f"保存聊天记录失败: {str(e)}")
            return False

    @staticmethod
    def load_chat(chat_id: str) -> Optional[Chat]:
        """加载指定ID的聊天记录
        
        Args:
            chat_id: 聊天ID
            
        Returns:
            如果聊天记录存在，返回Chat对象，否则返回None
        """
        chat_file = os.path.join(CHATS_DIR, f"{chat_id}.json")
        if os.path.exists(chat_file):
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    return Chat.from_dict(chat_data)
            except Exception as e:
                logger.error(f"加载聊天记录失败: {str(e)}")
        return None

    @staticmethod
    def get_user_chats(user_id: str) -> List[Dict]:
        """获取用户的所有聊天记录列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            聊天记录摘要列表
        """
        user_chats = []
        try:
            for filename in os.listdir(CHATS_DIR):
                if not filename.endswith(".json"):
                    continue
                    
                chat_file = os.path.join(CHATS_DIR, filename)
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    metadata = chat_data.get("metadata", {})
                    
                    # 只包含属于该用户的聊天
                    if metadata.get("user_id") == user_id:
                        chat_summary = {
                            "chat_id": chat_data.get("chat_id"),
                            "title": metadata.get("title", "无标题对话"),
                            "updated_at": chat_data.get("updated_at"),
                            "persona": metadata.get("persona", "general")
                        }
                        user_chats.append(chat_summary)
            
            # 按更新时间降序排序
            user_chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        except Exception as e:
            logger.error(f"获取用户聊天记录列表失败: {str(e)}")
        
        return user_chats

    @staticmethod
    def save_persona(persona: Persona) -> bool:
        """保存角色配置到文件
        
        Args:
            persona: 角色对象
            
        Returns:
            保存成功返回True，否则返回False
        """
        try:
            persona_file = os.path.join(PERSONAS_DIR, f"{persona.persona_id}.json")
            with open(persona_file, 'w', encoding='utf-8') as f:
                json.dump(persona.to_dict(), f, ensure_ascii=False, indent=4)
            logger.info(f"角色保存成功: {persona.persona_id}")
            return True
        except Exception as e:
            logger.error(f"保存角色失败: {str(e)}")
            return False

    @staticmethod
    def load_persona(persona_id: str) -> Optional[Persona]:
        """加载指定ID的角色配置
        
        Args:
            persona_id: 角色ID
            
        Returns:
            如果角色存在，返回Persona对象，否则返回None
        """
        persona_file = os.path.join(PERSONAS_DIR, f"{persona_id}.json")
        if os.path.exists(persona_file):
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    return Persona.from_dict(persona_id, persona_data)
            except Exception as e:
                logger.error(f"加载角色配置失败: {str(e)}")
        return None

    @staticmethod
    def load_all_personas() -> Dict[str, Persona]:
        """加载所有可用的角色配置
        
        Returns:
            以角色ID为键，Persona对象为值的字典
        """
        personas = {}
        try:
            for filename in os.listdir(PERSONAS_DIR):
                if not filename.endswith(".json"):
                    continue
                    
                persona_id = filename[:-5]  # 去掉.json后缀
                persona_file = os.path.join(PERSONAS_DIR, filename)
                
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    personas[persona_id] = Persona.from_dict(persona_id, persona_data)
        except Exception as e:
            logger.error(f"加载所有角色配置失败: {str(e)}")
        
        return personas

    @staticmethod
    def persona_exists(persona_id: str) -> bool:
        """检查角色是否存在
        
        Args:
            persona_id: 角色ID
            
        Returns:
            角色存在返回True，否则返回False
        """
        persona_file = os.path.join(PERSONAS_DIR, f"{persona_id}.json")
        return os.path.exists(persona_file) 