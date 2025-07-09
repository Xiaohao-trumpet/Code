import streamlit as st
import logging
from typing import Dict, Callable, Optional

from app.models.persona import Persona

logger = logging.getLogger("xiaohaochat.ui.persona")

class PersonaView:
    """角色管理UI组件，处理自定义角色的创建"""
    
    def __init__(self):
        pass
    
    def render_creator(self, on_persona_created: Callable[[str, str, str, str], bool]) -> None:
        """渲染角色创建界面
        
        Args:
            on_persona_created: 角色创建成功回调函数
        """
        st.subheader("创建自定义角色")
        
        with st.expander("创建新角色"):
            new_persona_id = st.text_input("角色ID (英文字母和数字)", key="new_persona_id")
            new_persona_name = st.text_input("角色名称", key="new_persona_name")
            new_persona_desc = st.text_area("角色描述", key="new_persona_desc")
            new_persona_prompt = st.text_area(
                "系统提示词", 
                key="new_persona_prompt",
                help="这是发送给AI的系统提示词，用于定义角色的行为。"
            )
            
            if st.button("创建角色", key="create_persona"):
                if not new_persona_id or not new_persona_name or not new_persona_prompt:
                    st.error("所有字段都是必填的")
                else:
                    success = on_persona_created(
                        new_persona_id, 
                        new_persona_name, 
                        new_persona_desc, 
                        new_persona_prompt
                    )
                    if success:
                        st.success("角色创建成功")
                    else:
                        st.error("角色ID已存在")
    
    def render_info(self, persona: Persona) -> None:
        """渲染角色信息
        
        Args:
            persona: 要显示的角色对象
        """
        st.subheader(f"当前角色: {persona.name}")
        st.caption(persona.description)
        
        # 可以添加更多角色信息展示 