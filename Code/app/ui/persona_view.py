import streamlit as st
import uuid
import logging
from typing import Dict, Callable, Optional

from app.models.persona import Persona

logger = logging.getLogger("xiaohaochat.ui.persona")

class PersonaView:
    """角色管理UI组件，处理自定义角色的创建"""
    
    def __init__(self):
        pass
    
    def render_creator(self, on_persona_created: Callable[[Persona], None]) -> None:
        """渲染角色创建界面
        
        Args:
            on_persona_created: 角色创建成功回调函数
        """
        new_persona_id = st.text_input("角色ID (英文字母和数字)", key="new_persona_id", 
                                      value=f"custom_{uuid.uuid4().hex[:8]}")
        new_persona_name = st.text_input("角色名称", key="new_persona_name")
        new_persona_desc = st.text_area("角色描述", key="new_persona_desc")
        new_persona_prompt = st.text_area(
            "系统提示词", 
            key="new_persona_prompt",
            help="这是发送给AI的系统提示词，用于定义角色的行为。"
        )
        
        if st.button("创建角色", key="create_persona"):
            if not new_persona_name or not new_persona_prompt:
                st.error("角色名称和系统提示词为必填项")
            else:
                # 创建新角色对象
                new_persona = Persona(
                    persona_id=new_persona_id,
                    name=new_persona_name,
                    description=new_persona_desc,
                    system_prompt=new_persona_prompt
                )
                
                # 调用回调函数
                on_persona_created(new_persona)
                
                # 清空表单
                st.session_state.new_persona_id = f"custom_{uuid.uuid4().hex[:8]}"
                st.session_state.new_persona_name = ""
                st.session_state.new_persona_desc = ""
                st.session_state.new_persona_prompt = ""
                
                st.success("角色创建成功")
    
    def render_info(self, persona: Optional[Persona] = None) -> None:
        """渲染角色信息
        
        Args:
            persona: 要显示的角色对象
        """
        if persona:
            st.write(f"### 🎭 {persona.name}")
            if persona.description:
                st.write(f"*{persona.description}*")
            st.divider() 