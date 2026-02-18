#!/usr/bin/env python3
"""
Security Monitor - Comprehensive security monitoring and Wazuh integration
Built for OpenClaw by Helios

Usage: security-monitor.py <command> [options]
"""

import os
import sys
import json
import time
import requests
import subprocess
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'security-monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        self.skill_dir = Path(__file__).parent.parent
        self.config_file = self.skill_dir / 'config' / 'security-monitor.yaml'
        self.config = self.load_config()
        self.wazuh_token = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        
        # Create default configuration
        default_config = {
            'wazuh': {
                'manager_url': 'http://192.168.10.143:55000',
                'username': 'wazuh',
                'password': 'wazuh',
                'verify_ssl': False,
                'timeout': 30
            },
            'monitoring': {
                'alert_threshold': 'medium',
                'scan_frequency': '1h',
                'report_schedule': 'daily',
                'retention_days': 90
            },
            'alerts': {
                'critical': ['malware', 'intrusion', 'rootkit'],
                'high': ['privilege_escalation', 'suspicious_process'],
                'medium': ['failed_auth', 'policy_violation'],
                'low': ['info_gathering', 'reconnaissance']
            }
        }
        
        # Create config directory and file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
            
        return default_config
    
    def authenticate_wazuh(self) -> Optional[str]:
        """Authenticate with Wazuh API and get token"""
        try:
            wazuh_config = self.config['wazuh']
            auth_url = f"{wazuh_config['manager_url']}/security/user/authenticate"
            
            # Create basic auth header
            credentials = f"{wazuh_config['username']}:{wazuh_config['password']}"
            encoded_creds = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {encoded_creds}'
            }
            
            response = requests.get(
                auth_url,
                headers=headers,
                verify=wazuh_config.get('verify_ssl', False),
                timeout=wazuh_config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.wazuh_token = data.get('data', {}).get('token')
                return self.wazuh_token
            else:
                logger.error(f"Wazuh authentication failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Wazuh authentication error: {e}")
            return None
    
    def wazuh_api_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Wazuh API"""
        if not self.wazuh_token:
            if not self.authenticate_wazuh():
                return None
        
        try:
            wazuh_config = self.config['wazuh']
            url = f"{wazuh_config['manager_url']}{endpoint}"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.wazuh_token}'
            }
            
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params or {},
                verify=wazuh_config.get('verify_ssl', False),
                timeout=wazuh_config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Wazuh API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Wazuh API error: {e}")
            return None
    
    def check_wazuh_status(self) -> Dict[str, Any]:
        """Check Wazuh manager and agent status"""
        status = {
            'manager': 'unknown',
            'agents': [],
            'total_agents': 0,
            'active_agents': 0,
            'alerts_last_24h': 0
        }
        
        # Check manager status
        manager_info = self.wazuh_api_request('/manager/info')
        if manager_info:
            status['manager'] = 'active'
        
        # Check agents
        agents_info = self.wazuh_api_request('/agents')
        if agents_info and 'data' in agents_info:
            agents = agents_info['data']['affected_items']
            status['total_agents'] = len(agents)
            
            for agent in agents:
                agent_status = {
                    'id': agent.get('id'),
                    'name': agent.get('name'),
                    'ip': agent.get('ip'),
                    'status': agent.get('status'),
                    'version': agent.get('version'),
                    'last_keep_alive': agent.get('lastKeepAlive')
                }
                status['agents'].append(agent_status)
                
                if agent.get('status') == 'active':
                    status['active_agents'] += 1
        
        # Get recent alerts count
        alerts = self.wazuh_api_request('/security/events', params={
            'date': (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d'),
            'limit': 1
        })
        if alerts and 'data' in alerts:
            status['alerts_last_24h'] = alerts['data'].get('total_affected_items', 0)
        
        return status
    
    def get_security_alerts(self, last_hours: int = 24, severity: str = 'all') -> List[Dict]:
        """Get security alerts from Wazuh"""
        alerts = []
        
        try:
            params = {
                'date': (datetime.now() - timedelta(hours=last_hours)).strftime('%Y-%m-%d'),
                'limit': 100,
                'sort': '-timestamp'
            }
            
            if severity != 'all':
                severity_levels = {
                    'low': [0, 3],
                    'medium': [4, 7],
                    'high': [8, 12],
                    'critical': [13, 15]
                }
                if severity in severity_levels:
                    level_range = severity_levels[severity]
                    params['rule.level'] = f"{level_range[0]}-{level_range[1]}"
            
            response = self.wazuh_api_request('/security/events', params=params)
            if response and 'data' in response:
                alerts = response['data'].get('affected_items', [])
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
        
        return alerts
    
    def run_security_scan(self, scan_type: str = 'quick') -> Dict[str, Any]:
        """Run security scan of local system"""
        scan_results = {
            'timestamp': datetime.now().isoformat(),
            'scan_type': scan_type,
            'findings': {
                'processes': [],
                'network': [],
                'files': [],
                'users': []
            },
            'summary': {
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        try:
            # Check for suspicious processes
            suspicious_processes = self.scan_processes()
            scan_results['findings']['processes'] = suspicious_processes
            
            # Check network connections
            if scan_type == 'full':
                network_issues = self.scan_network()
                scan_results['findings']['network'] = network_issues
            
            # Check file integrity (basic)
            file_issues = self.scan_files()
            scan_results['findings']['files'] = file_issues
            
            # Update summary
            for category in scan_results['findings']:
                for finding in scan_results['findings'][category]:
                    severity = finding.get('severity', 'low')
                    scan_results['summary'][severity] += 1
                    scan_results['summary']['total_issues'] += 1
            
        except Exception as e:
            logger.error(f"Security scan error: {e}")
            scan_results['error'] = str(e)
        
        return scan_results
    
    def scan_processes(self) -> List[Dict]:
        """Scan for suspicious processes"""
        suspicious = []
        suspicious_patterns = [
            'xmrig', 'stratum', 'mining', 'cryptonight',
            'nc -l', 'ncat -l', 'netcat',
            'python -c', 'perl -e', 'ruby -e'
        ]
        
        try:
            result = subprocess.run(['ps', 'auxf'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    for pattern in suspicious_patterns:
                        if pattern.lower() in line.lower():
                            suspicious.append({
                                'process': line.strip(),
                                'pattern': pattern,
                                'severity': 'high' if pattern in ['xmrig', 'nc -l'] else 'medium',
                                'description': f'Suspicious process matching pattern: {pattern}'
                            })
                            break
        except Exception as e:
            logger.error(f"Process scan error: {e}")
        
        return suspicious
    
    def scan_network(self) -> List[Dict]:
        """Scan network connections"""
        issues = []
        
        try:
            result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
            if result.returncode == 0:
                listening_ports = []
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            if ':' in address:
                                port = address.split(':')[-1]
                                listening_ports.append(port)
                
                # Check for unusual high ports
                for port in listening_ports:
                    try:
                        port_num = int(port)
                        if port_num > 9000 and port_num < 65535:
                            issues.append({
                                'port': port,
                                'severity': 'low',
                                'description': f'Unusual high port listening: {port}'
                            })
                    except ValueError:
                        continue
                        
        except Exception as e:
            logger.error(f"Network scan error: {e}")
        
        return issues
    
    def scan_files(self) -> List[Dict]:
        """Basic file integrity check"""
        issues = []
        critical_files = [
            '/etc/passwd',
            '/etc/shadow', 
            '/etc/sudoers',
            '/root/.ssh/authorized_keys'
        ]
        
        for file_path in critical_files:
            try:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    # Check permissions
                    if file_path == '/etc/shadow' and stat.st_mode & 0o077:
                        issues.append({
                            'file': file_path,
                            'issue': 'incorrect_permissions',
                            'severity': 'high',
                            'description': f'Critical file has overly permissive permissions: {file_path}'
                        })
            except Exception as e:
                logger.error(f"File scan error for {file_path}: {e}")
        
        return issues
    
    def generate_report(self, report_type: str = 'daily') -> Dict[str, Any]:
        """Generate security report"""
        if report_type == 'daily':
            hours = 24
        elif report_type == 'weekly':
            hours = 168
        else:
            hours = 24
        
        report = {
            'report_type': report_type,
            'generated': datetime.now().isoformat(),
            'period': f'Last {hours} hours',
            'wazuh_status': self.check_wazuh_status(),
            'alerts': self.get_security_alerts(last_hours=hours),
            'scan_results': self.run_security_scan('quick'),
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if report['wazuh_status']['active_agents'] < report['wazuh_status']['total_agents']:
            report['recommendations'].append({
                'priority': 'high',
                'category': 'infrastructure',
                'message': 'Some Wazuh agents are not active - check connectivity'
            })
        
        if len(report['alerts']) > 100:
            report['recommendations'].append({
                'priority': 'medium',
                'category': 'monitoring',
                'message': 'High volume of security alerts - consider tuning detection rules'
            })
        
        return report
    
    def print_status(self):
        """Print current security status"""
        print("\n🛡️  Security Monitor Status")
        print("=" * 40)
        
        # Wazuh status
        wazuh_status = self.check_wazuh_status()
        print(f"\n📊 Wazuh Manager: {wazuh_status['manager']}")
        print(f"👥 Agents: {wazuh_status['active_agents']}/{wazuh_status['total_agents']} active")
        print(f"⚠️  Alerts (24h): {wazuh_status['alerts_last_24h']}")
        
        # Recent alerts
        recent_alerts = self.get_security_alerts(last_hours=1, severity='high')
        if recent_alerts:
            print(f"\n🔥 Recent High Severity Alerts:")
            for alert in recent_alerts[:3]:
                timestamp = alert.get('timestamp', 'N/A')
                rule_desc = alert.get('rule', {}).get('description', 'Unknown')
                print(f"   • {timestamp}: {rule_desc}")
        
        # System scan
        print(f"\n🔍 Quick System Scan:")
        scan_results = self.run_security_scan('quick')
        summary = scan_results['summary']
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: security-monitor.py <command> [options]")
        print("\nCommands:")
        print("  status                     - Show security status")
        print("  alerts [--last HOURS]      - Show security alerts")
        print("  scan [--quick|--full]      - Run security scan")
        print("  report [--daily|--weekly]  - Generate security report")
        print("  wazuh-status              - Show Wazuh status details")
        sys.exit(1)
    
    command = sys.argv[1]
    monitor = SecurityMonitor()
    
    if command == 'status':
        monitor.print_status()
    
    elif command == 'alerts':
        hours = 24
        if '--last' in sys.argv:
            try:
                idx = sys.argv.index('--last')
                hours = int(sys.argv[idx + 1])
            except (ValueError, IndexError):
                hours = 24
        
        alerts = monitor.get_security_alerts(last_hours=hours)
        print(f"\n🚨 Security Alerts (Last {hours} hours)")
        print("=" * 50)
        
        for alert in alerts[:10]:  # Show top 10
            timestamp = alert.get('timestamp', 'N/A')
            rule = alert.get('rule', {})
            level = rule.get('level', 0)
            desc = rule.get('description', 'Unknown')
            agent = alert.get('agent', {}).get('name', 'Unknown')
            
            print(f"\n[Level {level}] {timestamp}")
            print(f"Agent: {agent}")
            print(f"Rule: {desc}")
    
    elif command == 'scan':
        scan_type = 'quick'
        if '--full' in sys.argv:
            scan_type = 'full'
        
        print(f"\n🔍 Running {scan_type} security scan...")
        results = monitor.run_security_scan(scan_type)
        
        print(f"\n📊 Scan Results ({results['timestamp']})")
        print("=" * 50)
        summary = results['summary']
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}")
        
        # Show critical/high findings
        for category, findings in results['findings'].items():
            critical_high = [f for f in findings if f.get('severity') in ['critical', 'high']]
            if critical_high:
                print(f"\n🚨 {category.title()} Issues:")
                for finding in critical_high:
                    print(f"   [{finding['severity'].upper()}] {finding['description']}")
    
    elif command == 'report':
        report_type = 'daily'
        if '--weekly' in sys.argv:
            report_type = 'weekly'
        
        print(f"\n📋 Generating {report_type} security report...")
        report = monitor.generate_report(report_type)
        
        # Save report
        reports_dir = Path(__file__).parent.parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"security-report-{report_type}-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report saved to: {report_file}")
        
        # Print summary
        print(f"\n📊 {report_type.title()} Security Summary")
        print("=" * 50)
        print(f"Period: {report['period']}")
        print(f"Wazuh Status: {report['wazuh_status']['manager']}")
        print(f"Active Agents: {report['wazuh_status']['active_agents']}/{report['wazuh_status']['total_agents']}")
        print(f"Total Alerts: {len(report['alerts'])}")
        print(f"Scan Issues: {report['scan_results']['summary']['total_issues']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   [{rec['priority'].upper()}] {rec['message']}")
    
    elif command == 'wazuh-status':
        status = monitor.check_wazuh_status()
        print(f"\n🛡️  Wazuh Status Details")
        print("=" * 40)
        print(f"Manager: {status['manager']}")
        print(f"Total Agents: {status['total_agents']}")
        print(f"Active Agents: {status['active_agents']}")
        print(f"Alerts (24h): {status['alerts_last_24h']}")
        
        print(f"\n👥 Agent Details:")
        for agent in status['agents']:
            status_icon = "🟢" if agent['status'] == 'active' else "🔴"
            print(f"   {status_icon} {agent['name']} ({agent['ip']}) - {agent['status']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()