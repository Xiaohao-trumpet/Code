import os
import streamlit as st
import logging
from typing import Dict, List, Optional, Any

from .auth.user_manager import UserManager
from .chat.chat_manager import ChatManager
from .chat.message_handler import MessageHandler
from .llm.ollama_client import OllamaClient
from .storage.file_storage import FileStorage
from .ui.auth_view import AuthView
from .ui.main_view import MainView
from .ui.sidebar_view import SidebarView
from .models.persona import Persona
from .config import get_default_personas

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局变量存储ngrok URL
ngrok_url = None

class XiaoHaoAssistant:
    """晓昊助手应用的主类"""

    def __init__(self):
        """初始化应用"""
        # 初始化存储
        self.file_storage = FileStorage()
        
        # 初始化用户管理器
        self.user_manager = UserManager(self.file_storage)
        
        # 初始化LLM客户端
        self.llm_client = OllamaClient()
        
        # 初始化消息处理器
        self.message_handler = MessageHandler(self.llm_client)
        
        # 初始化聊天管理器
        self.chat_manager = ChatManager(self.file_storage)
        
        # 初始化UI组件
        self.auth_view = AuthView(self.user_manager)
        self.main_view = MainView(self.message_handler)
        self.sidebar_view = SidebarView(self.chat_manager)
        
        # 初始化应用状态
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "current_user" not in st.session_state:
            st.session_state.current_user = None
        if "current_chat_id" not in st.session_state:
            st.session_state.current_chat_id = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "personas" not in st.session_state:
            st.session_state.personas = get_default_personas()
        if "selected_persona" not in st.session_state:
            st.session_state.selected_persona = "default"
        if "deep_thinking_mode" not in st.session_state:
            st.session_state.deep_thinking_mode = False
        
        # 初始化ngrok（如果启用）
        self._setup_ngrok()

    def _setup_ngrok(self):
        """设置ngrok内网穿透（如果启用）"""
        global ngrok_url
        if os.environ.get("USE_NGROK") == "true":
            try:
                # 检查pyngrok是否已安装
                import importlib
                if not importlib.util.find_spec("pyngrok"):
                    print("\n\n请先安装pyngrok: pip install pyngrok\n\n")
                    return
                
                # 导入需要的模块
                from pyngrok import ngrok, conf, installer
                from pyngrok.exception import PyngrokNgrokError
                
                # 获取ngrok token
                ngrok_token = os.environ.get("NGROK_TOKEN")
                
                # 首先尝试获取现有隧道
                try:
                    tunnels = ngrok.get_tunnels()
                    if tunnels:
                        ngrok_url = tunnels[0].public_url
                        print(f"\n\n使用已存在的ngrok隧道: {ngrok_url}\n\n")
                        logger.info(f"使用已存在的ngrok隧道: {ngrok_url}")
                        return
                except Exception as e:
                    logger.warning(f"获取现有隧道失败: {str(e)}")
                
                # 确保ngrok已安装
                ngrok_path = None
                try:
                    # 尝试获取已安装的ngrok路径
                    ngrok_path = conf.get_default().ngrok_path
                    print(f"\n\n找到ngrok路径: {ngrok_path}\n\n")
                except Exception:
                    # 如果获取失败，尝试安装ngrok
                    print("\n\n未找到ngrok，尝试安装...\n\n")
                    try:
                        # 使用installer模块安装ngrok
                        ngrok_path = installer.install_ngrok()
                        print(f"\n\nngrok安装成功: {ngrok_path}\n\n")
                    except Exception as install_err:
                        print(f"\n\nngrok安装失败: {str(install_err)}\n\n")
                        logger.error(f"ngrok安装失败: {str(install_err)}")
                
                # 如果找到或安装了ngrok
                if ngrok_path and os.path.exists(ngrok_path):
                    # 设置ngrok路径
                    conf.get_default().ngrok_path = ngrok_path
                    
                    # 如果有token，设置授权
                    if ngrok_token:
                        try:
                            print(f"\n\n正在设置ngrok token...\n\n")
                            # 使用subprocess直接调用ngrok设置token
                            import subprocess
                            
                            # 直接使用ngrok_path而不是通过API设置token
                            result = subprocess.run(
                                [ngrok_path, "authtoken", ngrok_token],
                                capture_output=True,
                                text=True
                            )
                            
                            if result.returncode == 0:
                                print("\n\nngrok token设置成功\n\n")
                                logger.info("ngrok token设置成功")
                            else:
                                print(f"\n\nngrok token设置失败: {result.stderr}\n\n")
                                logger.error(f"ngrok token设置失败: {result.stderr}")
                        except Exception as e:
                            print(f"\n\nngrok token设置过程中出错: {str(e)}\n\n")
                            logger.error(f"ngrok token设置过程中出错: {str(e)}")
                    
                    # 启动ngrok隧道
                    try:
                        print(f"\n\n正在启动ngrok隧道连接到端口 8501...\n\n")
                        # 使用subprocess启动ngrok
                        import subprocess
                        import threading
                        import time
                        import json
                        
                        # 启动ngrok进程
                        ngrok_process = subprocess.Popen(
                            [ngrok_path, "http", "8501"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        
                        # 等待ngrok启动
                        time.sleep(3)
                        
                        # 检查ngrok是否在运行
                        if ngrok_process.poll() is None:  # 进程仍在运行
                            print("\n\nngrok进程已启动\n\n")
                            
                            # 尝试从API获取URL
                            try:
                                # 使用requests获取URL
                                import requests
                                response = requests.get("http://127.0.0.1:4040/api/tunnels")
                                if response.status_code == 200:
                                    data = response.json()
                                    if "tunnels" in data and len(data["tunnels"]) > 0:
                                        ngrok_url = data["tunnels"][0]["public_url"]
                                        print(f"\n\n晓昊助手已通过ngrok部署到: {ngrok_url}\n\n")
                                        logger.info(f"晓昊助手已通过ngrok部署到: {ngrok_url}")
                                        return
                            except Exception as url_err:
                                print(f"\n\n获取ngrok URL失败: {str(url_err)}\n\n")
                                logger.error(f"获取ngrok URL失败: {str(url_err)}")
                        else:
                            print("\n\nngrok进程启动失败\n\n")
                            stdout, stderr = ngrok_process.communicate()
                            print(f"\n\nngrok输出: {stdout.decode('utf-8')}\n\n")
                            print(f"\n\nngrok错误: {stderr.decode('utf-8')}\n\n")
                    except Exception as e:
                        print(f"\n\nngrok启动失败: {str(e)}\n\n")
                        logger.error(f"ngrok启动失败: {str(e)}")
                else:
                    print("\n\nngrok路径无效或不存在\n\n")
                    logger.error("ngrok路径无效或不存在")
                
                # 如果以上方法都失败，尝试使用pyngrok的API
                try:
                    print("\n\n尝试使用pyngrok API启动ngrok...\n\n")
                    # 重置所有配置
                    ngrok.kill()
                    # 使用connect方法启动
                    public_url = ngrok.connect(8501)
                    ngrok_url = public_url.public_url
                    print(f"\n\n晓昊助手已通过ngrok部署到(API方式): {ngrok_url}\n\n")
                    logger.info(f"晓昊助手已通过ngrok部署到(API方式): {ngrok_url}")
                    return
                except Exception as api_err:
                    print(f"\n\npyngrok API启动失败: {str(api_err)}\n\n")
                    logger.error(f"pyngrok API启动失败: {str(api_err)}")
                
                # 最后的手动指导
                print("\n\n所有自动方法均失败，请尝试手动安装和启动ngrok:\n")
                print("1. 下载ngrok: https://ngrok.com/download")
                print("2. 解压并将ngrok添加到PATH")
                print("3. 运行: ngrok authtoken YOUR_TOKEN")
                print("4. 运行: ngrok http 8501\n\n")
                
            except Exception as e:
                error_msg = f"ngrok设置过程中出错: {e}"
                print(error_msg)
                logger.error(error_msg)

    def run(self):
        """运行应用"""
        # 设置页面标题和图标
        st.set_page_config(
            page_title="晓昊助手",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 显示ngrok URL（如果有）
        global ngrok_url
        if ngrok_url:
            st.sidebar.success(f"公网访问地址: [点击访问]({ngrok_url})")
        
        # 检查是否有退出登录操作
        if st.session_state.logged_in and st.sidebar.button("退出登录", key="logout_button"):
            self._logout()
            st.rerun()
        
        # 如果用户未登录，显示登录界面
        if not st.session_state.logged_in:
            self.auth_view.render()
            return
        
        # 用户已登录，显示主界面
        # 侧边栏
        self.sidebar_view.render(
            st.session_state.current_user,
            self._on_chat_selected,
            self._on_new_chat,
            self._on_persona_selected,
            self._on_persona_created,
            self._on_deep_thinking_toggled
        )
        
        # 主聊天界面
        self.main_view.render(
            st.session_state.messages,
            self._on_message_sent,
            st.session_state.deep_thinking_mode
        )
    
    def _logout(self):
        """处理退出登录"""
        logger.info(f"用户 {st.session_state.current_user} 退出登录")
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_chat_id = None
        st.session_state.messages = []
    
    def _on_message_sent(self, message: str):
        """处理发送消息事件"""
        if not message.strip():
            return
        
        # 确保有当前聊天ID
        if not st.session_state.current_chat_id:
            self._on_new_chat()
        
        # 获取当前角色
        current_persona = next(
            (p for p in st.session_state.personas if p.id == st.session_state.selected_persona), 
            st.session_state.personas[0]
        )
        
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": message})
        
        # 获取AI回复 - 根据深度思考模式决定是否显示"思考中"
        if st.session_state.deep_thinking_mode:
            # 深度思考模式下显示"思考中"
            with st.spinner("思考中..."):
                response = self.message_handler.get_response(
                    message, 
                    st.session_state.messages[:-1],  # 不包括刚刚添加的用户消息
                    current_persona.system_prompt,
                    st.session_state.deep_thinking_mode
                )
        else:
            # 普通模式下不显示"思考中"
            response = self.message_handler.get_response(
                message, 
                st.session_state.messages[:-1],  # 不包括刚刚添加的用户消息
                current_persona.system_prompt,
                st.session_state.deep_thinking_mode
            )
        
        # 添加AI回复
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 保存聊天历史
        self.chat_manager.save_chat(
            st.session_state.current_user,
            st.session_state.current_chat_id,
            st.session_state.messages,
            current_persona.id
        )
    
    def _on_chat_selected(self, chat_id: str, messages: List[Dict[str, str]], persona_id: str):
        """处理选择聊天事件"""
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = messages
        st.session_state.selected_persona = persona_id
    
    def _on_new_chat(self):
        """处理新建聊天事件"""
        chat_id = self.chat_manager.create_chat(
            st.session_state.current_user,
            st.session_state.selected_persona
        )
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = []
    
    def _on_persona_selected(self, persona_id: str):
        """处理选择角色事件"""
        st.session_state.selected_persona = persona_id
        
        # 如果当前有聊天，更新聊天的角色
        if st.session_state.current_chat_id:
            self.chat_manager.update_chat_persona(
                st.session_state.current_user,
                st.session_state.current_chat_id,
                persona_id
            )
    
    def _on_persona_created(self, persona: Persona):
        """处理创建角色事件"""
        st.session_state.personas.append(persona)
        st.session_state.selected_persona = persona.id
    
    def _on_deep_thinking_toggled(self, enabled: bool):
        """处理深度思考模式切换事件"""
        st.session_state.deep_thinking_mode = enabled 