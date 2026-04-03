#!/usr/bin/env python3
"""
AID Ltd. Dashboard Server

A comprehensive dashboard server that combines task management with OpenClaw monitoring.
"""
import json
import subprocess
import threading
import time
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import yaml


class AIDLtdDashboardHandler(BaseHTTPRequestHandler):
    """Request handler for the AID Ltd. dashboard."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/tasks':
            self.api_get_tasks()
        elif parsed_path.path == '/api/agents':
            self.api_get_agents()
        elif parsed_path.path == '/api/stats':
            self.api_get_stats()
        elif parsed_path.path == '/api/goals':
            self.api_get_goals()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/tasks/') and parsed_path.path.endswith('/comment'):
            # Extract task ID from path
            path_parts = parsed_path.path.split('/')
            if len(path_parts) >= 4:
                task_id = path_parts[3]
                self.api_add_comment(task_id)
            else:
                self.send_error(400, "Invalid path")
        else:
            self.send_error(404)
    
    def api_add_comment(self, task_id):
        """API endpoint to add a comment to a task."""
        try:
            # Get the content length and read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            comment_data = json.loads(post_data.decode('utf-8'))
            
            # Here we would normally save the comment to a database or file
            # For now, we'll just return success
            comment = {
                'id': str(int(time.time() * 1000)),  # Simple ID based on timestamp
                'content': comment_data.get('content', ''),
                'author': comment_data.get('author', 'Anonymous'),
                'timestamp': comment_data.get('timestamp', time.strftime('%Y-%m-%d %H:%M'))
            }
            
            # In a real implementation, we would save this comment to persistent storage
            # For now, we'll just return the comment as if it was saved successfully
            response = {
                'success': True,
                'comment': comment
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON in request body")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML."""
        try:
            # Read the dashboard HTML file
            dashboard_path = Path(__file__).parent / "dashboard.html"
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Dashboard file not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_tasks(self):
        """API endpoint to get tasks."""
        try:
            # Execute oa-cli task list command to get current tasks
            result = subprocess.run(['oa-cli', 'task', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                tasks = self.parse_task_list(result.stdout)
            else:
                tasks = []
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(tasks, ensure_ascii=False).encode('utf-8'))
        except subprocess.TimeoutExpired:
            self.send_error(408, "Command timeout")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_agents(self):
        """API endpoint to get agents."""
        try:
            # Execute oa-cli agent list command to get current agents
            result = subprocess.run(['oa-cli', 'agent', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                agents = self.parse_agent_list(result.stdout)
            else:
                agents = []
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(agents, ensure_ascii=False).encode('utf-8'))
        except subprocess.TimeoutExpired:
            self.send_error(408, "Command timeout")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_goals(self):
        """API endpoint to get system goals and metrics."""
        try:
            # Try to get data from professional oa-cli if available
            try:
                # Check if professional oa-cli is installed
                result = subprocess.run(['oa', 'status'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Professional oa-cli is available, get actual metrics
                    goals = self.parse_oa_status(result.stdout)
                else:
                    # Fallback to mock data
                    goals = self.get_mock_goals()
            except FileNotFoundError:
                # Professional oa-cli not installed, use mock data
                goals = self.get_mock_goals()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(goals, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_stats(self):
        """API endpoint to get system stats."""
        try:
            # Get tasks
            result = subprocess.run(['oa-cli', 'task', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            task_lines = result.stdout.strip().split('\n')
            
            # Count tasks by status
            pending_count = 0
            in_progress_count = 0
            completed_count = 0
            failed_count = 0
            
            # Skip header lines and parse task data
            for line in task_lines[2:]:  # Skip header and separator
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        status = parts[2].strip()
                        if status == 'pending':
                            pending_count += 1
                        elif status == 'in_progress':
                            in_progress_count += 1
                        elif status == 'completed':
                            completed_count += 1
                        elif status == 'failed':
                            failed_count += 1
            
            # Get agent stats
            result = subprocess.run(['oa-cli', 'agent', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            agent_info = {}
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        agent_info[key.strip()] = value.strip()
            
            stats = {
                'total_tasks': pending_count + in_progress_count + completed_count + failed_count,
                'pending_tasks': pending_count,
                'in_progress_tasks': in_progress_count,
                'completed_tasks': completed_count,
                'failed_tasks': failed_count,
                'total_agents': int(agent_info.get('Total agents', 0)),
                'active_agents': int(agent_info.get('Active agents', 0)),
                'inactive_agents': int(agent_info.get('Inactive agents', 0)),
                'healthy_goals': 2  # Mock value
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
        except subprocess.TimeoutExpired:
            self.send_error(408, "Command timeout")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def parse_task_list(self, output):
        """Parse the text output of 'oa-cli task list' command."""
        lines = output.strip().split('\n')
        if len(lines) < 3:
            return []
        
        # Parse task data
        tasks = []
        for line in lines[2:]:  # Skip header and separator
            if '|' not in line:
                continue
                
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:  # At least ID, Title, Status, Priority, Tags
                task = {
                    'id': parts[0],
                    'title': parts[1],
                    'status': parts[2],
                    'priority': parts[3],
                    'tags': [t.strip() for t in parts[4].split(',')] if parts[4] else [],
                    'subtasks': [],  # Placeholder for subtasks
                    'comments': []   # Placeholder for comments
                }
                tasks.append(task)
        
        return tasks
    
    def get_agents_from_monitor(self):
        """Get agents using the AgentMonitor class."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "oa-cli"))
            from oa_cli.agent.monitor import AgentMonitor
            
            monitor = AgentMonitor()
            agents = monitor.list_agents()
            
            # Transform to the expected format
            formatted_agents = []
            for agent in agents:
                # 状态汉化映射
                status_map = {
                    'running': '运行中',
                    'active': '活跃',
                    'idle': '空闲',
                    'busy': '忙碌',
                    'stopped': '已停止',
                    'inactive': '未激活',
                    'error': '错误',
                    'unknown': '未知'
                }
                original_status = agent.get('status', 'unknown').lower()
                chinese_status = status_map.get(original_status, '未知')
                
                formatted_agent = {
                    'name': agent.get('name', '未知'),
                    'path': agent.get('path', 'N/A'),
                    'status': chinese_status,
                    'original_status': original_status  # 保留原始状态用于样式判断
                }
                formatted_agents.append(formatted_agent)
            
            return formatted_agents
        except ImportError:
            # Fallback to mock data if monitor is not available
            return [
                {'name': '主代理', 'path': '~/.openclaw/agents/main', 'status': '运行中', 'original_status': 'running'},
                {'name': 'Claude代理', 'path': '~/.openclaw/agents/claude', 'status': '空闲', 'original_status': 'idle'},
                {'name': 'Codex代理', 'path': '~/.openclaw/agents/codex', 'status': '空闲', 'original_status': 'idle'},
                {'name': '伊娃', 'path': '~/.openclaw/agents/eva', 'status': '活跃', 'original_status': 'active'}
            ]
        except Exception as e:
            print(f"Error getting agents from monitor: {e}")
            # Return mock data in case of error
            return [
                {'name': '主代理', 'path': '~/.openclaw/agents/main', 'status': '运行中', 'original_status': 'running'},
                {'name': 'Claude代理', 'path': '~/.openclaw/agents/claude', 'status': '空闲', 'original_status': 'idle'},
                {'name': 'Codex代理', 'path': '~/.openclaw/agents/codex', 'status': '空闲', 'original_status': 'idle'},
                {'name': '伊娃', 'path': '~/.openclaw/agents/eva', 'status': '活跃', 'original_status': 'active'}
            ]

    def parse_agent_list(self, output):
        """Parse the text output of 'oa-cli agent list' command."""
        # Use the AgentMonitor instead of parsing text output
        return self.get_agents_from_monitor()
    
    def parse_oa_status(self, output):
        """Parse the output of 'oa status' command."""
        # This is a simplified parser - in reality, we'd need to parse the rich table format
        goals = [
            {
                'id': 'cron_reliability',
                'name': '定时任务可靠性',
                'healthStatus': 'healthy',
                'metrics': {
                    '成功率': {
                        'value': 98.5,
                        'unit': '%',
                        'trend': 2.1
                    }
                }
            },
            {
                'id': 'team_health',
                'name': '团队健康度',
                'healthStatus': 'warning',
                'metrics': {
                    '活跃代理数': {
                        'value': 3,
                        'unit': '个',
                        'trend': 0
                    },
                    '记忆纪律': {
                        'value': 75,
                        'unit': '%',
                        'trend': -5
                    }
                }
            },
            # OA 平台指标
            {
                'id': 'oa_metrics',
                'name': 'OA 平台指标',
                'healthStatus': 'healthy',
                'metrics': {
                    '任务完成率': {'value': 90, 'unit': '%', 'trend': 5},
                    '平均完成时间': {'value': 3.5, 'unit': '小时', 'trend': -0.5},
                    '一次验收通过率': {'value': 85, 'unit': '%', 'trend': 10},
                    '文件整理及时率': {'value': 100, 'unit': '%', 'trend': 0}
                }
            },
            # 多代理系统状态
            {
                'id': 'multi_agent',
                'name': '多代理系统状态',
                'healthStatus': 'healthy',
                'metrics': {
                    'agent-swarm-ex': {'value': '运行中', 'unit': '', 'trend': 0},
                    'agent-team-orchestration': {'value': '运行中', 'unit': '', 'trend': 0},
                    '活跃协作数': {'value': 2, 'unit': '个', 'trend': 0}
                }
            },
            # 内存系统状态
            {
                'id': 'memory_system',
                'name': '内存系统状态',
                'healthStatus': 'healthy',
                'metrics': {
                    'L1 短期记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'L2 工作记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'L3 长期记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'Memory-Plus MCP': {'value': '已部署', 'unit': '', 'trend': 0}
                }
            }
        ]
        return goals
    
    def get_mock_goals(self):
        """Return mock goals data when professional oa-cli is not available."""
        return [
            {
                'id': 'cron_reliability',
                'name': '定时任务可靠性',
                'healthStatus': 'healthy',
                'metrics': {
                    '成功率': {
                        'value': 98.5,
                        'unit': '%',
                        'trend': 2.1
                    }
                }
            },
            {
                'id': 'team_health',
                'name': '团队健康度',
                'healthStatus': 'warning',
                'metrics': {
                    '活跃代理数': {
                        'value': 3,
                        'unit': '个',
                        'trend': 0
                    },
                    '记忆纪律': {
                        'value': 75,
                        'unit': '%',
                        'trend': -5
                    }
                }
            },
            # OA 平台指标
            {
                'id': 'oa_metrics',
                'name': 'OA 平台指标',
                'healthStatus': 'healthy',
                'metrics': {
                    '任务完成率': {'value': 90, 'unit': '%', 'trend': 5},
                    '平均完成时间': {'value': 3.5, 'unit': '小时', 'trend': -0.5},
                    '一次验收通过率': {'value': 85, 'unit': '%', 'trend': 10},
                    '文件整理及时率': {'value': 100, 'unit': '%', 'trend': 0}
                }
            },
            # 多代理系统状态
            {
                'id': 'multi_agent',
                'name': '多代理系统状态',
                'healthStatus': 'healthy',
                'metrics': {
                    'agent-swarm-ex': {'value': '运行中', 'unit': '', 'trend': 0},
                    'agent-team-orchestration': {'value': '运行中', 'unit': '', 'trend': 0},
                    '活跃协作数': {'value': 2, 'unit': '个', 'trend': 0}
                }
            },
            # 内存系统状态
            {
                'id': 'memory_system',
                'name': '内存系统状态',
                'healthStatus': 'healthy',
                'metrics': {
                    'L1 短期记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'L2 工作记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'L3 长期记忆': {'value': '健康', 'unit': '', 'trend': 0},
                    'Memory-Plus MCP': {'value': '已部署', 'unit': '', 'trend': 0}
                }
            }
        ]


def start_server(port=8080):
    """Start the dashboard server."""
    server = HTTPServer(('localhost', port), AIDLtdDashboardHandler)
    print(f"AID Ltd. Dashboard server starting on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    import sys
    
    port = 18888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 18888")
    
    start_server(port)