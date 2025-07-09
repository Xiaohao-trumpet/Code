import logging
from typing import Optional

from app.models.user import User
from app.storage.file_storage import FileStorage

logger = logging.getLogger("xiaohaochat.auth")

class UserManager:
    """用户管理类，处理用户认证、注册等功能"""
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """认证用户并返回用户ID
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            如果认证成功，返回用户ID，否则返回None
        """
        user = self.storage.load_user(username)
        if not user:
            logger.info(f"认证失败: 用户 {username} 不存在")
            return None
        
        # TODO: 生产环境应使用加密哈希比较密码
        if user.password == password:
            logger.info(f"用户 {username} 认证成功")
            return user.user_id
        
        logger.info(f"认证失败: 用户 {username} 密码不正确")
        return None
    
    def register_user(self, username: str, password: str) -> Optional[str]:
        """注册新用户并返回用户ID
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            如果注册成功，返回用户ID，否则返回None
        """
        # 检查用户是否已存在
        if self.storage.user_exists(username):
            logger.info(f"注册失败: 用户名 {username} 已存在")
            return None
        
        # TODO: 生产环境应该对密码进行哈希处理
        user = User(username=username, password=password)
        if self.storage.save_user(user):
            logger.info(f"用户注册成功: {username}")
            return user.user_id
        
        logger.error(f"用户注册失败: {username}")
        return None 