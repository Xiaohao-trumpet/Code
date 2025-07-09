import streamlit as st
import logging
from typing import Tuple, Dict, List, Any, Optional, Callable

from app.chat.chat_manager import ChatManager
from app.models.persona import Persona

logger = logging.getLogger("xiaohaochat.ui.sidebar")

class SidebarView:
    """侧边栏UI组件，处理聊天历史、设置等功能"""
    
    def __init__(self, chat_manager: ChatManager, personas: Dict[str, Persona]):
        self.chat_manager = chat_manager
        self.personas = personas
    
    def render(self, username: str, user_id: str, 
              current_chat_id: Optional[str], 
              current_persona: str,
              on_new_chat: Callable, 
              on_chat_selected: Callable[[str], None],
              on_logout: Callable,
              on_persona_change: Callable[[str], None]) -> Tuple[bool, str]:
        """渲染侧边栏界面
        
        Args:
            username: 当前用户名
            user_id: 当前用户ID
            current_chat_id: 当前选中的聊天ID
            current_persona: 当前选择的角色ID
            on_new_chat: 创建新聊天的回调函数
            on_chat_selected: 聊天被选择时的回调函数
            on_logout: 登出按钮点击的回调函数
            on_persona_change: 角色改变时的回调函数
        
        Returns:
            元组 (深度思考模式状态, 当前角色ID)
        """
        with st.sidebar:
            st.title(f"欢迎, {username}")
            
            # 新建对话按钮
            if st.button("新建对话", key="new_chat"):
                on_new_chat()
            
            # 聊天历史
            st.subheader("对话历史")
            chats = self.chat_manager.get_user_chats(user_id)
            
            for chat in chats:
                chat_title = chat.get("title", "无标题对话")
                if st.button(chat_title, key=f"chat_{chat['chat_id']}"):
                    on_chat_selected(chat["chat_id"])
            
            # 设置区
            st.subheader("设置")
            
            # 深度思考模式
            deep_thinking = st.session_state.get("deep_thinking", False)
            deep_thinking = st.checkbox(
                "深度思考模式", 
                value=deep_thinking,
                help="启用后，AI将会花更多时间思考，给出更详细的回答。"
            )
            st.session_state.deep_thinking = deep_thinking
            
            # 角色选择
            st.subheader("选择角色")
            persona_options = {p.name: pid for pid, p in self.personas.items()}
            
            try:
                current_persona_name = self.personas[current_persona].name
                index = list(persona_options.keys()).index(current_persona_name)
            except (KeyError, ValueError):
                current_persona_name = list(persona_options.keys())[0]
                index = 0
                
            selected_persona_name = st.selectbox(
                "选择助手角色",
                options=list(persona_options.keys()),
                index=index
            )
            
            selected_persona_id = persona_options[selected_persona_name]
            if selected_persona_id != current_persona:
                on_persona_change(selected_persona_id)
            
            # 退出登录按钮
            if st.button("退出登录", key="logout"):
                on_logout()
            
        return deep_thinking, selected_persona_id 