import streamlit as st
import logging
from typing import List, Dict, Any, Optional, Callable

from app.chat.message_handler import MessageHandler

logger = logging.getLogger("xiaohaochat.ui.main")

class MainView:
    """主聊天界面组件，处理聊天消息显示和输入"""
    
    def __init__(self, message_handler: MessageHandler):
        """初始化主界面
        
        Args:
            message_handler: 消息处理器实例
        """
        self.message_handler = message_handler
    
    def render(self, 
              messages: List[Dict[str, str]], 
              on_message_sent: Callable[[str], None],
              deep_thinking_mode: bool = False) -> None:
        """渲染主聊天界面
        
        Args:
            messages: 聊天消息列表
            on_message_sent: 消息发送回调函数
            deep_thinking_mode: 是否启用深度思考模式
        """
        # 标题
        st.title("晓昊助手")
        
        # 显示深度思考模式状态
        if deep_thinking_mode:
            st.info("💭 深度思考模式已启用")
        
        st.divider()
        
        # 创建一个聊天消息容器
        chat_container = st.container()
        
        # 显示现有消息
        with chat_container:
            for message in messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # 聊天输入 - 不使用session_state直接设置值
        # 直接使用chat_input并处理返回值
        prompt = st.chat_input("请输入你的问题", key="chat_input_field")
        
        # 处理直接点击发送的情况
        if prompt:
            on_message_sent(prompt)
            # 立即重新渲染页面以显示回复
            st.rerun() 