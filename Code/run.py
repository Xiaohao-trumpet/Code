#!/usr/bin/env python3
"""
晓昊助手 - 启动脚本
用于启动晓昊助手应用
"""

from app.main import XiaoHaoAssistant

def main():
    """主入口点函数"""
    app = XiaoHaoAssistant()
    app.run()

if __name__ == "__main__":
    main() 