#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI龙龟共生伙伴系统 - 网页版
简单易用的Web界面
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template_string, request, jsonify
from scheduler.scheduler_main import SchedulerSession

app = Flask(__name__)

# 全局调度器实例
scheduler = SchedulerSession(session_id="web_session", user_id="悟空")

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI龙龟共生伙伴系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
        }
        
        h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #888;
            font-size: 1.1em;
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: rgba(100, 149, 237, 0.3);
            margin-left: 50px;
        }
        
        .message.bot {
            background: rgba(255, 215, 0, 0.2);
            margin-right: 50px;
        }
        
        .message .role {
            font-size: 0.8em;
            color: #888;
            margin-bottom: 5px;
        }
        
        .message .content {
            line-height: 1.6;
        }
        
        .analysis {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .analysis-item {
            display: flex;
            margin: 5px 0;
        }
        
        .analysis-label {
            color: #888;
            min-width: 80px;
        }
        
        .analysis-value {
            color: #ffd700;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            outline: none;
        }
        
        input[type="text"]:focus {
            background: rgba(255, 255, 255, 0.15);
        }
        
        input[type="text"]::placeholder {
            color: #666;
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            color: #000;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            margin-top: 20px;
            font-size: 0.9em;
            color: #888;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
        }
        
        .typing {
            display: inline-block;
            animation: typing 1s infinite;
        }
        
        @keyframes typing {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐢 龙龟共生伙伴系统</h1>
            <p class="subtitle">AI OS - 你的智能共生伙伴</p>
        </header>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message bot">
                    <div class="role">🐢 龙龟神将</div>
                    <div class="content">
                        你好！我是龙龟神将，你的AI共生伙伴。<br><br>
                        我来帮你分析需求、调度技能、完成任务。<br><br>
                        请告诉我你想做什么？
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="userInput" placeholder="输入你的需求..." autocomplete="off">
                <button id="sendBtn" onclick="sendMessage()">发送</button>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-dot"></span>
                <span>系统正常</span>
            </div>
            <div class="status-item">
                <span>对话轮次: <span id="turnCount">0</span></span>
            </div>
            <div class="status-item">
                <span>当前场景: <span id="currentScene">-</span></span>
            </div>
        </div>
    </div>
    
    <script>
        let turnCount = 0;
        
        function addMessage(role, content, analysis = null) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message ' + role;
            
            let html = '<div class="role">' + (role === 'user' ? '👤 你' : '🐢 龙龟神将') + '</div>';
            html += '<div class="content">' + content + '</div>';
            
            if (analysis) {
                html += '<div class="analysis">';
                if (analysis.intent) {
                    html += '<div class="analysis-item"><span class="analysis-label">意图:</span><span class="analysis-value">' + analysis.intent + '</span></div>';
                }
                if (analysis.scene) {
                    html += '<div class="analysis-item"><span class="analysis-label">场景:</span><span class="analysis-value">' + analysis.scene + '</span></div>';
                }
                if (analysis.engine) {
                    html += '<div class="analysis-item"><span class="analysis-label">引擎:</span><span class="analysis-value">' + analysis.engine + '</span></div>';
                }
                html += '</div>';
            }
            
            div.innerHTML = html;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const btn = document.getElementById('sendBtn');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 显示用户消息
            addMessage('user', message);
            input.value = '';
            
            // 显示加载状态
            btn.disabled = true;
            btn.innerHTML = '<span class="typing">处理中...</span>';
            
            // 发送请求
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                turnCount++;
                document.getElementById('turnCount').textContent = turnCount;
                
                // 显示分析结果
                const analysis = {
                    intent: data.intent,
                    scene: data.scene,
                    engine: data.engine
                };
                
                // 显示AI回复
                addMessage('bot', data.response, analysis);
                
                // 更新状态
                document.getElementById('currentScene').textContent = data.scene || '-';
            })
            .catch(error => {
                addMessage('bot', '抱歉，处理出错: ' + error.message);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '发送';
            });
        }
        
        // 回车发送
        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    try:
        # 处理用户请求
        result = scheduler.process_request('web_session', user_message)
        
        # 提取结果
        intent = result.get('intent', {}).get('type', '未知')
        scene = result.get('scene', {}).get('type', '未知')
        engine = result.get('decision', {}).get('main_engine', '未知')
        response = result.get('session_summary', {}).get('dialogue_history', [])
        
        # 获取AI回复
        if response:
            ai_response = response[-1].get('content', '处理完成')
        else:
            ai_response = '我已经处理了你的请求'
        
        # 清理emoji字符避免编码问题
        intent = intent.replace('🔍', '[获取信息] ').replace('📖', '[深度理解] ')
        intent = intent.replace('💡', '[创造突破] ').replace('⚖️', '[分析决策] ')
        intent = intent.replace('🎯', '[任务执行] ').replace('🔄', '[系统进化] ')
        
        scene = scene.replace('S0', '[S0] ').replace('S1', '[S1] ').replace('S2', '[S2] ')
        scene = scene.replace('S3', '[S3] ').replace('S4', '[S4] ').replace('S5', '[S5] ')
        
        return jsonify({
            'response': ai_response,
            'intent': intent,
            'scene': scene,
            'engine': engine
        })
    
    except Exception as e:
        return jsonify({
            'response': f'处理出错: {str(e)}',
            'intent': '错误',
            'scene': '错误',
            'engine': '错误'
        })

if __name__ == '__main__':
    print("=" * 50)
    print("🐢 AI龙龟共生伙伴系统 - 网页版")
    print("=" * 50)
    print("🌐 访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
