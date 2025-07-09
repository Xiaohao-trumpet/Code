import logging
from typing import List, Dict, Any, Optional

from app.llm import ollama_client
from app.models.persona import Persona

logger = logging.getLogger("xiaohaochat.message")

class MessageHandler:
    """消息处理类，负责与LLM交互，处理消息内容"""
    
    def __init__(self):
        self.client = ollama_client
    
    def process_message(self, message: str, history: List[Dict[str, str]], 
                        persona: Persona, deep_thinking: bool = False) -> str:
        """处理用户消息，获取AI回复
        
        Args:
            message: 用户输入的消息
            history: 聊天历史记录
            persona: 当前使用的角色
            deep_thinking: 是否启用深度思考模式
            
        Returns:
            AI的回复内容
        """
        try:
            logger.info(f"处理消息: 角色={persona.persona_id}, 深度思考={deep_thinking}")
            
            # 准备发送给API的消息，首先添加系统提示词
            messages_for_api = [
                {"role": "system", "content": persona.system_prompt}
            ]
            
            # 添加历史消息
            messages_for_api.extend(history)
            
            # 发送到Ollama API
            response = self.client.chat(messages_for_api, deep_thinking=deep_thinking)
            
            # 提取回复内容
            if response and 'message' in response and 'content' in response['message']:
                ai_response = response['message']['content']
                logger.info("成功获取AI回复")
                return ai_response
            else:
                logger.error("AI回复格式错误")
                return "抱歉，我无法生成回复。请稍后再试。"
                
        except Exception as e:
            logger.error(f"获取AI回复失败: {str(e)}")
            return f"抱歉，发生了错误: {str(e)}" 