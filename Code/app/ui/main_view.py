import streamlit as st
import logging
from typing import List, Dict, Any, Optional, Callable

from app.models.persona import Persona
from app.models.chat import Chat

logger = logging.getLogger("xiaohaochat.ui.main")

class MainView:
    """主聊天界面组件，处理聊天消息显示和输入"""
    
    def __init__(self):
        pass
    
    def render(self, 
              messages: List[Dict[str, str]], 
              persona: Persona,
              deep_thinking: bool,
              on_message_sent: Callable[[str], None]) -> None:
        """渲染主聊天界面
        
        Args:
            messages: 聊天消息列表
            persona: 当前使用的角色
            deep_thinking: 是否启用深度思考模式
            on_message_sent: 消息发送回调函数
        """
        # 标题和角色信息
        st.title("晓昊助手")
        
        # 显示角色信息
        from app.ui.persona_view import PersonaView
        persona_view = PersonaView()
        persona_view.render_info(persona)
        
        # 显示深度思考模式状态
        if deep_thinking:
            st.info("深度思考模式已启用")
        
        st.divider()
        
        # 显示现有消息
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 聊天输入
        prompt = st.chat_input("请输入你的问题")
        
        if prompt:
            # 显示用户消息
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 处理消息发送
            on_message_sent(prompt) 