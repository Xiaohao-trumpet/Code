import logging
import re
from typing import List, Dict, Any, Optional

from app.llm.ollama_client import OllamaClient

logger = logging.getLogger("xiaohaochat.message")

class MessageHandler:
    """消息处理类，负责与LLM交互，处理消息内容"""
    
    def __init__(self, llm_client: OllamaClient):
        """初始化消息处理器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.client = llm_client
    
    def _format_thinking(self, response: str) -> str:
        """格式化思考内容，将<think>标签转换为Markdown引用块
        
        Args:
            response: 原始响应文本
            
        Returns:
            格式化后的响应文本
        """
        # 使用正则表达式捕获<think>和</think>之间的内容
        pattern = r'<think>(.*?)</think>'
        
        def replacer(match):
            # 获取思考内容
            thinking = match.group(1).strip()
            # 将思考内容转换为Markdown引用块格式
            # 在每一行前添加>符号
            formatted_thinking = '\n\n> **思考过程：**\n'
            for line in thinking.split('\n'):
                formatted_thinking += f'> {line}\n'
            formatted_thinking += '\n'
            return formatted_thinking
        
        # 替换所有匹配
        formatted_response = re.sub(pattern, replacer, response, flags=re.DOTALL)
        return formatted_response
    
    def _remove_thinking(self, response: str) -> str:
        """移除思考内容，去除<think>标签及其内容
        
        Args:
            response: 原始响应文本
            
        Returns:
            移除思考内容后的响应文本
        """
        # 使用正则表达式移除<think>标签及其内容
        pattern = r'<think>.*?</think>'
        clean_response = re.sub(pattern, '', response, flags=re.DOTALL)
        return clean_response.strip()
    
    def get_response(self, message: str, history: List[Dict[str, str]], 
                    system_prompt: str, deep_thinking_mode: bool = False) -> str:
        """处理用户消息，获取AI回复
        
        Args:
            message: 用户输入的消息
            history: 聊天历史记录
            system_prompt: 系统提示词
            deep_thinking_mode: 是否启用深度思考模式
            
        Returns:
            AI的回复内容
        """
        try:
            logger.info(f"处理消息: 深度思考={deep_thinking_mode}")
            
            # 准备发送给API的消息，首先添加系统提示词
            current_prompt = system_prompt
            
            # 如果启用深度思考模式，添加思考指令到系统提示词
            if deep_thinking_mode:
                current_prompt += "\n\n当你需要思考复杂问题时，请使用<think>标签包围你的思考过程，如：<think>这里是我的分析...</think>，然后再给出你的回答。"
            
            messages_for_api = [
                {"role": "system", "content": current_prompt}
            ]
            
            # 添加历史消息
            messages_for_api.extend(history)
            
            # 添加当前用户消息
            messages_for_api.append({"role": "user", "content": message})
            
            # 发送到Ollama API
            response = self.client.chat(messages_for_api, deep_thinking_mode)
            
            # 提取回复内容
            if response and 'message' in response and 'content' in response['message']:
                ai_response = response['message']['content']
                logger.info("成功获取AI回复")
                
                # 处理回复内容
                if deep_thinking_mode:
                    # 如果启用深度思考模式，将<think>标签转换为Markdown引用块
                    return self._format_thinking(ai_response)
                else:
                    # 如果未启用深度思考模式，移除<think>标签及其内容
                    return self._remove_thinking(ai_response)
            else:
                logger.error("AI回复格式错误")
                return "抱歉，我无法生成回复。请稍后再试。"
                
        except Exception as e:
            logger.error(f"获取AI回复失败: {str(e)}")
            return f"抱歉，发生了错误: {str(e)}" 
    
    # 保留旧方法以兼容可能的调用
    def process_message(self, message: str, history: List[Dict[str, str]], 
                        persona, deep_thinking: bool = False) -> str:
        """处理用户消息的兼容方法
        
        Args:
            message: 用户输入的消息
            history: 聊天历史记录
            persona: 当前使用的角色
            deep_thinking: 是否启用深度思考模式
            
        Returns:
            AI的回复内容
        """
        return self.get_response(message, history, persona.system_prompt, deep_thinking) 