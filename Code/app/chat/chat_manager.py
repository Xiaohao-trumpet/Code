import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional

from app.models.chat import Chat
from app.storage.file_storage import FileStorage

logger = logging.getLogger("xiaohaochat.chat")

class ChatManager:
    """聊天管理类，处理聊天历史的创建、加载和保存"""
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
    
    def create_chat(self, user_id: str, persona_id: str = "general") -> Chat:
        """创建新的聊天会话
        
        Args:
            user_id: 用户ID
            persona_id: 角色ID，默认为"general"
            
        Returns:
            新创建的Chat对象
        """
        chat_id = str(uuid.uuid4())
        title = f"新对话 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 创建聊天元数据
        metadata = {
            "user_id": user_id,
            "title": title,
            "persona": persona_id
        }
        
        # 创建聊天对象
        chat = Chat(
            chat_id=chat_id,
            user_id=user_id,
            messages=[],
            metadata=metadata,
            updated_at=datetime.datetime.now().isoformat()
        )
        
        # 保存到存储
        if self.storage.save_chat(chat):
            logger.info(f"创建聊天成功: {chat_id}")
        else:
            logger.error(f"创建聊天失败: {chat_id}")
        
        return chat
    
    def load_chat(self, chat_id: str) -> Optional[Chat]:
        """加载指定ID的聊天记录
        
        Args:
            chat_id: 聊天ID
            
        Returns:
            如果聊天记录存在，返回Chat对象，否则返回None
        """
        return self.storage.load_chat(chat_id)
    
    def get_user_chats(self, user_id: str) -> List[Dict]:
        """获取用户的所有聊天记录列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            聊天记录摘要列表
        """
        return self.storage.get_user_chats(user_id)
    
    def save_message(self, chat_id: str, role: str, content: str) -> bool:
        """向聊天中添加新消息并保存
        
        Args:
            chat_id: 聊天ID
            role: 消息发送者角色 ("user"或"assistant")
            content: 消息内容
            
        Returns:
            保存成功返回True，否则返回False
        """
        chat = self.storage.load_chat(chat_id)
        if not chat:
            logger.error(f"添加消息失败: 聊天 {chat_id} 不存在")
            return False
        
        # 添加新消息
        chat.messages.append({
            "role": role,
            "content": content
        })
        
        # 更新时间戳
        chat.updated_at = datetime.datetime.now().isoformat()
        
        # 保存到存储
        return self.storage.save_chat(chat)
    
    def update_chat_metadata(self, chat_id: str, metadata: Dict[str, Any]) -> bool:
        """更新聊天元数据
        
        Args:
            chat_id: 聊天ID
            metadata: 要更新的元数据字典
            
        Returns:
            更新成功返回True，否则返回False
        """
        chat = self.storage.load_chat(chat_id)
        if not chat:
            logger.error(f"更新元数据失败: 聊天 {chat_id} 不存在")
            return False
        
        # 更新元数据
        chat.metadata.update(metadata)
        
        # 更新时间戳
        chat.updated_at = datetime.datetime.now().isoformat()
        
        # 保存到存储
        return self.storage.save_chat(chat) 