#!/usr/bin/env python3
"""
晓昊助手 - 启动脚本
用于启动晓昊助手应用
"""

import os
import sys
import argparse
import subprocess
import streamlit as st
from app.main import XiaoHaoAssistant

# 解析命令行参数
parser = argparse.ArgumentParser(description="晓昊助手启动脚本")
parser.add_argument("--use-ngrok", action="store_true", help="使用ngrok进行内网穿透")
parser.add_argument("--ngrok-token", type=str, help="ngrok授权token")
args = parser.parse_args()

# 如果指定了ngrok参数，设置环境变量
if args.use_ngrok:
    os.environ["USE_NGROK"] = "true"
    if args.ngrok_token:
        os.environ["NGROK_TOKEN"] = args.ngrok_token
        print(f"已设置ngrok token: {args.ngrok_token[:5]}...")
    else:
        print("警告: 未提供ngrok token，将使用默认设置")

# 定义主函数
def main():
    """应用入口点"""
    app = XiaoHaoAssistant()
    app.run()

# 直接运行应用
if __name__ == "__main__":
    # 检查是否由streamlit直接运行
    if os.environ.get("STREAMLIT_RUNNING") == "true":
        main()
    else:
        # 设置环境变量标记，避免递归调用
        os.environ["STREAMLIT_RUNNING"] = "true"
        # 启动streamlit
        print("正在启动晓昊助手...")
        subprocess.call(["streamlit", "run", __file__]) 