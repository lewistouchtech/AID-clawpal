#!/usr/bin/env python3
"""AID 看板汉化修复脚本"""

import re

files_to_fix = [
    "dashboard.html",
    "advanced_dashboard.html",
    "server.py",
    "advanced_server.py"
]

# 汉化映射表
translations = {
    # 通用
    "Task": "任务",
    "Agent": "代理",
    "Status": "状态",
    "Priority": "优先级",
    "Progress": "进度",
    "Actions": "操作",
    "Dashboard": "看板",
    "Overview": "概览",
    "Settings": "设置",
    
    # 任务相关
    "Pending": "待办",
    "In Progress": "进行中",
    "Completed": "已完成",
    "Failed": "失败",
    "Total Tasks": "任务总数",
    "Pending Tasks": "待办任务",
    "In Progress Tasks": "进行中任务",
    "Completed Tasks": "已完成任务",
    "Failed Tasks": "失败任务",
    
    # 代理相关
    "Active Agents": "活跃代理",
    "Agent Status": "代理状态",
    "Running": "运行中",
    "Idle": "空闲",
    "Busy": "忙碌",
    "Offline": "离线",
    "Unknown": "未知",
    
    # OA 指标
    "Completion Rate": "完成率",
    "Success Rate": "成功率",
    "Avg Completion Time": "平均完成时间",
    "First Pass Yield": "一次验收通过率",
    "File Organization": "文件整理及时率",
    "Corn Reliability": "核心可靠性",
    "Active Agent Count": "活跃代理数",
    
    # 内存系统
    "Memory System": "内存系统",
    "Health": "健康度",
    "L1 Hot Memory": "L1 热记忆",
    "L2 Warm Memory": "L2 温记忆",
    "L3 Cold Memory": "L3 冷记忆",
    "Total Memories": "总记忆数",
    "FTS Status": "全文索引状态",
    
    # 多代理
    "Multi-Agent System": "多代理系统",
    "Swarm Status": "群体状态",
    "Team Orchestration": "团队编排",
    "Collaboration": "协作",
    
    # 时间
    "Created": "创建时间",
    "Updated": "更新时间",
    "Duration": "耗时",
    "Hours": "小时",
    "Minutes": "分钟",
}

def translate_file(filepath):
    """翻译文件中的英文标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        count = 0
        
        # 替换英文标签
        for en, zh in translations.items():
            # 匹配 HTML 标签内的英文
            pattern = f'>([\\s]*){re.escape(en)}([\\s]*)<'
            replacement = f'>\\g<1>{zh}\\g<2><'
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            count += content.count(zh) - original.count(zh)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                content = f.write(content)
            print(f"✅ {filepath}: 已汉化")
        else:
            print(f"⚠️  {filepath}: 无需修改")
            
    except Exception as e:
        print(f"❌ {filepath}: {e}")

if __name__ == "__main__":
    print("开始汉化 AID 看板...")
    for filepath in files_to_fix:
        translate_file(filepath)
    print("汉化完成！")
