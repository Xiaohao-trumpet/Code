import streamlit as st
import logging
from typing import Tuple, Optional

from app.auth.user_manager import UserManager

logger = logging.getLogger("xiaohaochat.ui.auth")

class AuthView:
    """认证界面组件，处理登录和注册UI"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
    
    def render(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """渲染认证界面
        
        Returns:
            元组 (认证成功标志, 用户ID, 用户名)
        """
        auth_container = st.container()
        authenticated = False
        user_id = None
        username = None
        
        with auth_container:
            st.title("晓昊助手 - 登录")
            
            col1, col2 = st.columns(2)
            
            # 登录表单
            with col1:
                st.subheader("登录")
                login_username = st.text_input("用户名", key="login_username")
                login_password = st.text_input("密码", type="password", key="login_password")
                login_button = st.button("登录")
                
                if login_button:
                    if not login_username or not login_password:
                        st.error("用户名和密码不能为空")
                    else:
                        user_id = self.user_manager.authenticate_user(login_username, login_password)
                        if user_id:
                            authenticated = True
                            username = login_username
                            logger.info(f"用户 {login_username} 登录成功")
                        else:
                            st.error("用户名或密码错误")
            
            # 注册表单
            with col2:
                st.subheader("注册")
                reg_username = st.text_input("用户名", key="reg_username")
                reg_password = st.text_input("密码", type="password", key="reg_password")
                reg_password_confirm = st.text_input("确认密码", type="password", key="reg_password_confirm")
                reg_button = st.button("注册")
                
                if reg_button:
                    if reg_password != reg_password_confirm:
                        st.error("两次密码输入不一致")
                    elif not reg_username or not reg_password:
                        st.error("用户名和密码不能为空")
                    else:
                        user_id = self.user_manager.register_user(reg_username, reg_password)
                        if user_id:
                            st.success("注册成功，请登录")
                        else:
                            st.error("用户名已存在")
        
        return authenticated, user_id, username 