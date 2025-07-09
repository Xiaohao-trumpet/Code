import streamlit as st
import logging
from typing import Dict

from app.config import UI_CONFIG, setup_logging, DEFAULT_PERSONAS
from app.storage.file_storage import FileStorage
from app.auth.user_manager import UserManager
from app.chat.chat_manager import ChatManager
from app.chat.message_handler import MessageHandler
from app.ui.auth_view import AuthView
from app.ui.sidebar_view import SidebarView
from app.ui.main_view import MainView
from app.ui.persona_view import PersonaView
from app.models.persona import Persona

# 设置日志
logger = setup_logging()

class XiaoHaoAssistant:
    """晓昊助手主应用类"""
    
    def __init__(self):
        # 初始化存储层
        self.storage = FileStorage()
        
        # 初始化服务层
        self.user_manager = UserManager(self.storage)
        self.chat_manager = ChatManager(self.storage)
        self.message_handler = MessageHandler()
        
        # 初始化UI层
        self.auth_view = AuthView(self.user_manager)
        self.persona_view = PersonaView()
        
        # 加载所有角色
        self.personas = self._load_personas()
        
        # 侧边栏视图需要角色列表，所以最后初始化
        self.sidebar_view = SidebarView(self.chat_manager, self.personas)
        self.main_view = MainView()
        
        logger.info("应用初始化完成")
    
    def _load_personas(self) -> Dict[str, Persona]:
        """加载所有角色"""
        personas = {}
        
        # 从文件系统加载所有角色
        db_personas = self.storage.load_all_personas()
        
        # 如果没有角色数据，创建默认角色
        if not db_personas:
            logger.info("未找到角色数据，创建默认角色")
            for persona_id, persona_data in DEFAULT_PERSONAS.items():
                persona = Persona(
                    persona_id=persona_id,
                    name=persona_data["name"],
                    description=persona_data["description"],
                    system_prompt=persona_data["system_prompt"]
                )
                self.storage.save_persona(persona)
                personas[persona_id] = persona
        else:
            personas = db_personas
        
        return personas
    
    def _init_session_state(self):
        """初始化会话状态"""
        if 'initialized' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.session_state.chats = []
            st.session_state.deep_thinking = False
            st.session_state.current_persona = "general"
            st.session_state.personas = self.personas
            st.session_state.initialized = True
            logger.info("会话状态初始化完成")
    
    def _handle_new_chat(self):
        """处理新建聊天"""
        # 创建新聊天
        chat = self.chat_manager.create_chat(
            user_id=st.session_state.user_id, 
            persona_id=st.session_state.current_persona
        )
        
        # 更新会话状态
        st.session_state.current_chat_id = chat.chat_id
        st.session_state.messages = []
        st.session_state.chats = self.chat_manager.get_user_chats(st.session_state.user_id)
        
        st.rerun()
    
    def _handle_chat_selected(self, chat_id):
        """处理聊天选择"""
        # 加载选中的聊天记录
        chat = self.storage.load_chat(chat_id)
        if chat:
            # 更新会话状态
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = chat.messages
            st.session_state.current_persona = chat.metadata.get("persona", "general")
            
            st.rerun()
    
    def _handle_logout(self):
        """处理登出"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.current_chat_id = None
        st.session_state.messages = []
        
        st.rerun()
    
    def _handle_persona_change(self, persona_id):
        """处理角色变更"""
        st.session_state.current_persona = persona_id
        
        # 更新当前聊天的元数据
        if st.session_state.current_chat_id:
            self.chat_manager.update_chat_metadata(
                st.session_state.current_chat_id,
                {"persona": persona_id}
            )
    
    def _handle_persona_created(self, persona_id, name, description, system_prompt):
        """处理角色创建"""
        # 检查角色ID是否已存在
        if self.storage.persona_exists(persona_id):
            return False
        
        # 创建新角色
        persona = Persona(
            persona_id=persona_id,
            name=name,
            description=description,
            system_prompt=system_prompt
        )
        
        # 保存角色
        if self.storage.save_persona(persona):
            # 重新加载角色列表
            self.personas = self.storage.load_all_personas()
            st.session_state.personas = self.personas
            return True
        
        return False
    
    def _handle_message_sent(self, message):
        """处理消息发送"""
        if not st.session_state.current_chat_id:
            logger.error("发送消息失败: 无当前聊天ID")
            return
        
        # 保存用户消息到聊天记录
        if not self.chat_manager.save_message(
            st.session_state.current_chat_id, 
            "user", 
            message
        ):
            logger.error("保存用户消息失败")
            return
        
        # 更新会话状态中的消息列表
        st.session_state.messages.append({"role": "user", "content": message})
        
        # 获取当前角色
        current_persona = self.personas.get(st.session_state.current_persona)
        if not current_persona:
            logger.error(f"获取角色失败: {st.session_state.current_persona}")
            current_persona = next(iter(self.personas.values()))
        
        # 处理消息并获取AI回复
        with st.chat_message("assistant"):
            with st.spinner("AI思考中..." if not st.session_state.deep_thinking else "AI深度思考中..."):
                # 处理消息
                ai_response = self.message_handler.process_message(
                    message=message,
                    history=st.session_state.messages,
                    persona=current_persona,
                    deep_thinking=st.session_state.deep_thinking
                )
                
                # 显示回复
                st.markdown(ai_response)
        
        # 保存AI回复到聊天记录
        if not self.chat_manager.save_message(
            st.session_state.current_chat_id, 
            "assistant", 
            ai_response
        ):
            logger.error("保存AI回复失败")
            return
        
        # 更新会话状态中的消息列表
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    def run(self):
        """运行应用"""
        # 设置页面配置
        st.set_page_config(**UI_CONFIG)
        
        # 初始化会话状态
        self._init_session_state()
        
        # 认证流程
        if not st.session_state.authenticated:
            authenticated, user_id, username = self.auth_view.render()
            if authenticated:
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.chats = self.chat_manager.get_user_chats(user_id)
                st.rerun()
            return
        
        # 渲染侧边栏
        deep_thinking, current_persona = self.sidebar_view.render(
            username=st.session_state.username,
            user_id=st.session_state.user_id,
            current_chat_id=st.session_state.current_chat_id,
            current_persona=st.session_state.current_persona,
            on_new_chat=self._handle_new_chat,
            on_chat_selected=self._handle_chat_selected,
            on_logout=self._handle_logout,
            on_persona_change=self._handle_persona_change
        )
        
        # 保存深度思考模式状态
        st.session_state.deep_thinking = deep_thinking
        
        # 初始化或加载当前聊天
        if not st.session_state.current_chat_id:
            if st.session_state.chats:
                # 加载最近的聊天
                most_recent_chat = st.session_state.chats[0]
                self._handle_chat_selected(most_recent_chat["chat_id"])
            else:
                # 创建新聊天
                self._handle_new_chat()
            return
        
        # 获取当前角色
        current_persona_obj = self.personas.get(current_persona)
        if not current_persona_obj:
            logger.error(f"获取角色失败: {current_persona}")
            # 使用默认角色
            current_persona_obj = next(iter(self.personas.values()))
        
        # 渲染主界面
        self.main_view.render(
            messages=st.session_state.messages,
            persona=current_persona_obj,
            deep_thinking=deep_thinking,
            on_message_sent=self._handle_message_sent
        )
        
        # 在主界面下方渲染角色创建器
        self.persona_view.render_creator(on_persona_created=self._handle_persona_created) 