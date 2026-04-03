#!/usr/bin/env python3
"""
AID Ltd. Advanced Dashboard Server

A comprehensive dashboard server that combines task management with OpenClaw monitoring.
Integrates professional oa-cli features from Amyssjj/Agent_Exploration project.
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
import os
from datetime import datetime


class AIDLtdAdvancedHandler(BaseHTTPRequestHandler):
    """Request handler for the advanced AID Ltd. dashboard."""
    
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
        elif parsed_path.path == '/api/config':
            self.api_get_config()
        elif parsed_path.path == '/api/health':
            self.api_get_health()
        elif parsed_path.path == '/api/goals/metrics':
            self.api_get_goal_metrics()
        elif parsed_path.path == '/api/cron-chart':
            self.api_get_cron_chart()
        elif parsed_path.path == '/api/team-health':
            self.api_get_team_health()
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
            dashboard_path = Path(__file__).parent / "advanced_dashboard.html"
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
            # Use the AgentMonitor class to get accurate agent status
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "oa-cli"))
            from oa_cli.agent.monitor import AgentMonitor
            
            monitor = AgentMonitor()
            agents = monitor.list_agents()
            
            # Transform to the expected format
            formatted_agents = []
            for agent in agents:
                formatted_agent = {
                    'name': agent['name'],
                    'path': agent['path'],
                    'status': agent['status']
                }
                formatted_agents.append(formatted_agent)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(formatted_agents, ensure_ascii=False).encode('utf-8'))
        except ImportError:
            # Fallback to mock data if monitor is not available
            agents = [
                {'name': 'main', 'path': '~/.openclaw/agents/main', 'status': 'running'},
                {'name': 'claude', 'path': '~/.openclaw/agents/claude', 'status': 'idle'},
                {'name': 'codex', 'path': '~/.openclaw/agents/codex', 'status': 'idle'}
            ]
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(agents, ensure_ascii=False).encode('utf-8'))
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
    
    def api_get_config(self):
        """API endpoint to get project configuration."""
        try:
            config = {
                "agents": [
                    {"id": "main", "name": "主代理"},
                    {"id": "claude", "name": "Claude代理"},
                    {"id": "codex", "name": "Codex代理"}
                ],
                "goals": [
                    {"id": "cron_reliability", "name": "定时任务可靠性"},
                    {"id": "team_health", "name": "团队健康度"},
                    {"id": "performance", "name": "性能指标"}
                ]
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_health(self):
        """API endpoint to get overall system health."""
        try:
            # Get data from various sources
            health = {
                "overall": "healthy",  # Could be healthy, warning, or critical
                "goals": 3,
                "healthy": 2,
                "warning": 1,
                "critical": 0,
                "lastCollected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(health, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_goal_metrics(self):
        """API endpoint to get time-series metrics for all goals."""
        try:
            # Mock time-series data for demonstration
            metrics = {
                "cron_reliability": [
                    {"date": "2026-04-01", "metric": "成功率", "value": 95.5, "unit": "%", "breakdown": None},
                    {"date": "2026-04-02", "metric": "成功率", "value": 97.2, "unit": "%", "breakdown": None},
                    {"date": "2026-04-03", "metric": "成功率", "value": 98.1, "unit": "%", "breakdown": None}
                ],
                "team_health": [
                    {"date": "2026-04-01", "metric": "活跃代理数", "value": 5, "unit": "个", "breakdown": None},
                    {"date": "2026-04-02", "metric": "活跃代理数", "value": 6, "unit": "个", "breakdown": None},
                    {"date": "2026-04-03", "metric": "活跃代理数", "value": 6, "unit": "个", "breakdown": None}
                ]
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(metrics, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_cron_chart(self):
        """API endpoint to get cron run data for charts."""
        try:
            # Mock cron run data
            cron_data = [
                {"date": "2026-04-03", "cron_name": "daily_backup", "status": "success", "job_id": "backup_001"},
                {"date": "2026-04-03", "cron_name": "memory_cleanup", "status": "success", "job_id": "cleanup_001"},
                {"date": "2026-04-03", "cron_name": "log_rotation", "status": "failed", "job_id": "rotate_001"}
            ]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(cron_data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def api_get_team_health(self):
        """API endpoint to get daily agent activity data."""
        try:
            # Mock team health data
            health_data = [
                {"date": "2026-04-01", "agent_id": "main", "session_count": 12, "memory_logged": 1, "last_active": "2026-04-01T10:30:00"},
                {"date": "2026-04-01", "agent_id": "claude", "session_count": 8, "memory_logged": 1, "last_active": "2026-04-01T11:15:00"},
                {"date": "2026-04-02", "agent_id": "main", "session_count": 15, "memory_logged": 1, "last_active": "2026-04-02T09:45:00"},
                {"date": "2026-04-02", "agent_id": "claude", "session_count": 6, "memory_logged": 1, "last_active": "2026-04-02T14:20:00"},
                {"date": "2026-04-03", "agent_id": "main", "session_count": 10, "memory_logged": 1, "last_active": "2026-04-03T08:30:00"},
                {"date": "2026-04-03", "agent_id": "claude", "session_count": 9, "memory_logged": 1, "last_active": "2026-04-03T12:15:00"}
            ]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(health_data, ensure_ascii=False).encode('utf-8'))
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
    
    def parse_oa_status(self, output):
        """Parse the output of 'oa status' command."""
        # This is a simplified parser - in reality, we'd need to parse the rich table format
        goals = [
            {
                'id': 'cron_reliability',
                'name': '定时任务可靠性',
                'healthStatus': 'healthy',
                'metrics': {
                    'success_rate': {
                        'value': 98.5,
                        'unit': '%',
                        'healthy': 95,
                        'warning': 80,
                        'trend': 2.1
                    }
                },
                'sparkline': [
                    {'date': '2026-04-01', 'value': 95.5},
                    {'date': '2026-04-02', 'value': 97.2},
                    {'date': '2026-04-03', 'value': 98.1}
                ]
            },
            {
                'id': 'team_health',
                'name': '团队健康度',
                'healthStatus': 'warning',
                'metrics': {
                    'active_agent_count': {
                        'value': 3,
                        'unit': 'count',
                        'healthy': 5,
                        'warning': 3,
                        'trend': 0
                    },
                    'memory_discipline': {
                        'value': 75,
                        'unit': '%',
                        'healthy': 80,
                        'warning': 50,
                        'trend': -5
                    }
                },
                'sparkline': [
                    {'date': '2026-04-01', 'value': 5},
                    {'date': '2026-04-02', 'value': 4},
                    {'date': '2026-04-03', 'value': 3}
                ]
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
                    'success_rate': {
                        'value': 98.5,
                        'unit': '%',
                        'healthy': 95,
                        'warning': 80,
                        'trend': 2.1
                    }
                },
                'sparkline': [
                    {'date': '2026-04-01', 'value': 95.5},
                    {'date': '2026-04-02', 'value': 97.2},
                    {'date': '2026-04-03', 'value': 98.1}
                ]
            },
            {
                'id': 'team_health',
                'name': '团队健康度',
                'healthStatus': 'warning',
                'metrics': {
                    'active_agent_count': {
                        'value': 3,
                        'unit': 'count',
                        'healthy': 5,
                        'warning': 3,
                        'trend': 0
                    },
                    'memory_discipline': {
                        'value': 75,
                        'unit': '%',
                        'healthy': 80,
                        'warning': 50,
                        'trend': -5
                    }
                },
                'sparkline': [
                    {'date': '2026-04-01', 'value': 5},
                    {'date': '2026-04-02', 'value': 4},
                    {'date': '2026-04-03', 'value': 3}
                ]
            }
        ]


def start_server(port=8090):
    """Start the dashboard server."""
    server = HTTPServer(('localhost', port), AIDLtdAdvancedHandler)
    print(f"AID Ltd. Advanced Dashboard server starting on http://localhost:{port}")
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