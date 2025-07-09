import streamlit as st
import logging
from typing import Tuple, Optional

from app.auth.user_manager import UserManager

logger = logging.getLogger("xiaohaochat.ui.auth")

class AuthView:
    """认证界面组件，处理登录和注册UI"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        # 确保session_state中有auth_view
        if 'auth_view' not in st.session_state:
            st.session_state.auth_view = 'login'
    
    def render(self) -> None:
        """渲染认证界面并处理登录/注册流程
        
        如果登录/注册成功，会更新session_state中的logged_in和current_user
        """
        auth_container = st.container()
        
        with auth_container:
            st.title("晓昊助手")
            
            if st.session_state.auth_view == 'login':
                self._render_login_view()
            else:  # 注册页面
                self._render_register_view()
    
    def _render_login_view(self):
        """渲染登录页面"""
        st.header("欢迎回来", divider="rainbow")
        
        # 居中显示的登录表单
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_container = st.container(border=True)
            with login_container:
                st.subheader("账号登录")
                
                # 使用session_state存储表单值，确保在页面重新加载时保留
                if "login_username" not in st.session_state:
                    st.session_state.login_username = ""
                if "login_password" not in st.session_state:
                    st.session_state.login_password = ""
                
                # 使用callback函数更新session_state
                def update_username():
                    st.session_state.login_username = st.session_state.username_input
                
                def update_password():
                    st.session_state.login_password = st.session_state.password_input
                
                # 使用key参数绑定到session_state
                login_username = st.text_input(
                    "用户名", 
                    key="username_input",
                    value=st.session_state.login_username,
                    placeholder="请输入用户名",
                    on_change=update_username
                )
                
                login_password = st.text_input(
                    "密码", 
                    type="password", 
                    key="password_input",
                    value=st.session_state.login_password,
                    placeholder="请输入密码",
                    on_change=update_password
                )
                
                # 添加间距
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                
                # 居中显示登录按钮
                col_left, col_center, col_right = st.columns([1, 2, 1])
                with col_center:
                    login_button = st.button("登录", type="primary", use_container_width=True)
                
                if login_button:
                    if not login_username or not login_password:
                        st.error("用户名和密码不能为空")
                    else:
                        user_id = self.user_manager.authenticate_user(login_username, login_password)
                        if user_id:
                            # 更新session_state
                            st.session_state.logged_in = True
                            st.session_state.current_user = login_username
                            logger.info(f"用户 {login_username} 登录成功")
                            st.success("登录成功，正在跳转...")
                            # 强制重新加载页面
                            st.rerun()
                        else:
                            st.error("用户名或密码错误")
                
                # 在登录表单内部底部添加注册链接
                st.markdown("<div style='text-align: center; margin-top: 20px;'>没有账号？</div>", unsafe_allow_html=True)
                
                # 使用常规按钮代替JavaScript链接
                if st.button("点此注册", key="register_link", use_container_width=True):
                    st.session_state.auth_view = 'register'
                    st.rerun()
    
    def _render_register_view(self):
        """渲染注册页面"""
        st.header("创建新账号", divider="rainbow")
        
        # 居中显示的注册表单
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_container = st.container(border=True)
            with register_container:
                st.subheader("账号注册")
                
                # 使用session_state存储表单值
                if "reg_username" not in st.session_state:
                    st.session_state.reg_username = ""
                if "reg_password" not in st.session_state:
                    st.session_state.reg_password = ""
                if "reg_password_confirm" not in st.session_state:
                    st.session_state.reg_password_confirm = ""
                
                # 使用callback函数更新session_state
                def update_reg_username():
                    st.session_state.reg_username = st.session_state.reg_username_input
                
                def update_reg_password():
                    st.session_state.reg_password = st.session_state.reg_password_input
                
                def update_reg_password_confirm():
                    st.session_state.reg_password_confirm = st.session_state.reg_password_confirm_input
                
                reg_username = st.text_input(
                    "用户名", 
                    key="reg_username_input",
                    value=st.session_state.reg_username,
                    placeholder="请输入用户名",
                    on_change=update_reg_username
                )
                
                reg_password = st.text_input(
                    "密码", 
                    type="password", 
                    key="reg_password_input",
                    value=st.session_state.reg_password,
                    placeholder="请输入密码",
                    on_change=update_reg_password
                )
                
                reg_password_confirm = st.text_input(
                    "确认密码", 
                    type="password", 
                    key="reg_password_confirm_input",
                    value=st.session_state.reg_password_confirm,
                    placeholder="请再次输入密码",
                    on_change=update_reg_password_confirm
                )
                
                # 添加间距
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                
                # 居中显示注册按钮
                col_left, col_center, col_right = st.columns([1, 2, 1])
                with col_center:
                    reg_button = st.button("注册", type="primary", use_container_width=True)
                
                if reg_button:
                    if reg_password != reg_password_confirm:
                        st.error("两次密码输入不一致")
                    elif not reg_username or not reg_password:
                        st.error("用户名和密码不能为空")
                    else:
                        user_id = self.user_manager.register_user(reg_username, reg_password)
                        if user_id:
                            st.success("注册成功，请登录")
                            # 清除注册表单数据
                            st.session_state.reg_username = ""
                            st.session_state.reg_password = ""
                            st.session_state.reg_password_confirm = ""
                            # 切换到登录页
                            st.session_state.auth_view = 'login'
                            st.rerun()
                        else:
                            st.error("用户名已存在")
                
                # 在注册表单内部底部添加登录链接
                st.markdown("<div style='text-align: center; margin-top: 20px;'>已有账号？</div>", unsafe_allow_html=True)
                
                # 使用常规按钮代替JavaScript链接
                if st.button("返回登录", key="login_link", use_container_width=True):
                    st.session_state.auth_view = 'login'
                    st.rerun()
    
    def _switch_to_register(self):
        """切换到注册页面"""
        st.session_state.auth_view = 'register'
        st.rerun()
    
    def _switch_to_login(self):
        """切换到登录页面"""
        st.session_state.auth_view = 'login'
        st.rerun() 