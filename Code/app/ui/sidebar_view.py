import streamlit as st
import uuid
import logging
from typing import List, Dict, Any, Optional, Callable

from app.chat.chat_manager import ChatManager
from app.models.persona import Persona
from app.ui.persona_view import PersonaView

logger = logging.getLogger("xiaohaochat.ui.sidebar")

class SidebarView:
    """侧边栏视图，包含设置、聊天历史等组件"""
    
    def __init__(self, chat_manager: ChatManager):
        """初始化侧边栏视图
        
        Args:
            chat_manager: 聊天管理器实例
        """
        self.chat_manager = chat_manager
        self.persona_view = PersonaView()
    
    def render(self, 
              current_user: str,
              on_chat_selected: Callable[[str, List[Dict[str, str]], str], None],
              on_new_chat: Callable[[], None],
              on_persona_selected: Callable[[str], None],
              on_persona_created: Callable[[Persona], None],
              on_deep_thinking_toggled: Callable[[bool], None]) -> None:
        """渲染侧边栏
        
        Args:
            current_user: 当前用户ID
            on_chat_selected: 选择聊天回调函数
            on_new_chat: 新建聊天回调函数
            on_persona_selected: 选择角色回调函数
            on_persona_created: 创建角色回调函数
            on_deep_thinking_toggled: 切换深度思考模式回调函数
        """
        with st.sidebar:
            # 用户信息和新建按钮
            st.subheader(f"👤 {current_user}")
            
            # 新建对话按钮
            if st.button("✨ 新建对话", use_container_width=True):
                on_new_chat()
                st.rerun()
            
            st.divider()
            
            # 聊天历史
            st.subheader("💬 对话历史")
            chats = self.chat_manager.get_user_chats(current_user)
            
            for chat in chats:
                chat_id = chat["chat_id"]
                title = chat["title"] if "title" in chat and chat["title"] else f"对话 {chat_id[:6]}"
                
                if st.button(title, key=chat_id, use_container_width=True):
                    chat_data = self.chat_manager.load_chat(current_user, chat_id)
                    if chat_data:
                        on_chat_selected(
                            chat_id, 
                            chat_data["messages"], 
                            chat_data["persona_id"]
                        )
                        st.rerun()
            
            st.divider()
            
            # 设置部分
            st.subheader("⚙️ 设置")
            
            # 角色选择
            st.subheader("🎭 选择角色")
            personas = st.session_state.personas
            persona_options = {p.id: p.name for p in personas}
            selected_persona = st.selectbox(
                "角色",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                key="persona_selector"
            )
            
            if selected_persona != st.session_state.selected_persona:
                on_persona_selected(selected_persona)
            
            # 在侧边栏显示创建角色的表单
            with st.expander("创建新角色", expanded=False):
                self.persona_view.render_creator(on_persona_created)
            
            # 深度思考模式切换
            st.subheader("🧠 思考模式")
            deep_thinking = st.checkbox("启用深度思考", value=st.session_state.deep_thinking_mode)
            
            if deep_thinking != st.session_state.deep_thinking_mode:
                on_deep_thinking_toggled(deep_thinking)
                st.rerun() 