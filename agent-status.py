#!/usr/bin/env python3
"""
OpenClaw Agent Status Checker - v4

Get real-time status of all agents (resident + subagents)
Uses sessions_list API for subagents
"""
import subprocess
import json
import sys
from pathlib import Path

def get_resident_agents():
    """Get resident agents from ~/.openclaw/agents/ directory."""
    agents_dir = Path.home() / '.openclaw' / 'agents'
    agents = []
    
    if agents_dir.exists():
        import re
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
                if re.match(r'^[a-zA-Z0-9_-]+$', agent_dir.name):
                    has_files = any([
                        list(agent_dir.glob('*.py')),
                        list(agent_dir.glob('*.json')),
                        list(agent_dir.glob('*.md')),
                        (agent_dir / 'SKILL.md').exists(),
                        (agent_dir / 'agent.json').exists(),
                        (agent_dir / 'config.json').exists()
                    ])
                    
                    if has_files:
                        agents.append({
                            'name': agent_dir.name,
                            'path': str(agent_dir),
                            'status': '空闲',
                            'type': 'resident'
                        })
    
    return agents

def get_active_subagents():
    """Get active subagents using sessions_list API."""
    try:
        # Use sessions_list command
        result = subprocess.run(
            ['openclaw', 'sessions', 'list', '--kinds', 'subagent', '--limit', '50'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            subagents = []
            # Parse output - look for running sessions
            for line in result.stdout.split('\n'):
                line_lower = line.lower()
                if 'subagent' in line_lower or 'running' in line_lower:
                    # Try to extract label/name
                    import re
                    # Match patterns like "memory-plus-p2-fix-json-parser"
                    match = re.search(r'([a-zA-Z0-9_-]+-agent|[a-zA-Z0-9_-]+-p\d+-\S+)', line)
                    if match:
                        label = match.group(1)
                        subagents.append({
                            'name': f'子代理：{label}',
                            'path': '~/.openclaw/sessions/',
                            'status': '运行中',
                            'type': 'subagent'
                        })
            return subagents
    except Exception as e:
        print(f"Error getting subagents: {e}", file=sys.stderr)
    
    # Fallback: check recent sessions directory
    try:
        sessions_dir = Path.home() / '.openclaw' / 'sessions'
        if sessions_dir.exists():
            import time
            now = time.time()
            one_hour_ago = now - 3600
            
            for session_file in sessions_dir.glob('*.json'):
                try:
                    mtime = session_file.stat().st_mtime
                    if mtime > one_hour_ago:
                        with open(session_file, 'r') as f:
                            data = json.load(f)
                            if data.get('kind') == 'subagent' or data.get('runtime') == 'subagent':
                                label = data.get('label', session_file.stem)
                                subagents.append({
                                    'name': f'子代理：{label}',
                                    'path': '~/.openclaw/sessions/',
                                    'status': '运行中',
                                    'type': 'subagent'
                                })
                except:
                    pass
    except Exception as e:
        print(f"Error scanning sessions: {e}", file=sys.stderr)
    
    return []

def main():
    """Main function."""
    resident = get_resident_agents()
    subagents = get_active_subagents()
    
    all_agents = resident + subagents
    
    print(json.dumps(all_agents, ensure_ascii=False, indent=2))
    
    print(f"\n=== 摘要 ===", file=sys.stderr)
    print(f"常驻代理：{len(resident)} 个", file=sys.stderr)
    print(f"活跃子代理：{len(subagents)} 个", file=sys.stderr)
    for sa in subagents:
        print(f"  - {sa['name']}", file=sys.stderr)
    print(f"总计：{len(all_agents)} 个", file=sys.stderr)

if __name__ == '__main__':
    main()
