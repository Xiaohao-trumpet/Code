import logging
from typing import Optional
import json
import os

from app.models.user import User
from app.storage.file_storage import FileStorage
from app.config import USERS_DIR

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
        # 直接检查文件内容以排除可能的问题
        user_file = os.path.join(USERS_DIR, f"{username}.json")
        if not os.path.exists(user_file):
            logger.info(f"认证失败: 用户 {username} 不存在")
            return None
            
        try:
            # 直接读取用户文件
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                logger.info(f"成功读取用户数据: {username}")
                logger.info(f"用户数据: {json.dumps(user_data, ensure_ascii=False)}")
                
            stored_password = user_data.get("password", "")
            
            # 对比密码
            if stored_password == password:
                logger.info(f"用户 {username} 认证成功")
                return user_data.get("user_id", "")
            else:
                logger.info(f"认证失败: 用户 {username} 密码不匹配, 输入: {password}, 存储: {stored_password}")
                return None
                
        except Exception as e:
            logger.error(f"认证过程中出错: {str(e)}")
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