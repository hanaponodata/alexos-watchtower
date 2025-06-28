"""
Watchtower Configuration for ALEX OS Integration
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WatchtowerConfig:
    """Watchtower configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/watchtower.yml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Watchtower configuration"""
        default_config = {
            'watchtower': {
                'enabled': True,
                'update_interval': 300,  # 5 minutes
                'cleanup': True,
                'auto_update': False,
                'notification_url': None,
                'docker_socket': '/var/run/docker.sock',
                'include_stopped': False,
                'revive_stopped': False,
                'remove_volumes': False,
                'label_enable': True,
                'scope': 'swarm',  # or 'local'
                'http_api': True,
                'http_api_port': 8080,
                'http_api_token': None,
                'http_api_metrics': True,
                'monitoring_enabled': True,
                'monitoring_interval': 30,
                'webhook_enabled': True,
                'webhook_url': None,
                'webhook_events': ['container_status_changed', 'update_detected', 'update_applied']
            },
            'notifications': {
                'slack': {
                    'enabled': False,
                    'webhook_url': None,
                    'channel': '#watchtower'
                },
                'email': {
                    'enabled': False,
                    'smtp_host': None,
                    'smtp_port': 587,
                    'username': None,
                    'password': None,
                    'from': None,
                    'to': []
                },
                'discord': {
                    'enabled': False,
                    'webhook_url': None
                }
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': None,
                'max_size': '10MB',
                'backup_count': 5
            },
            'security': {
                'api_key_required': True,
                'allowed_ips': [],
                'rate_limit': {
                    'enabled': True,
                    'requests_per_minute': 60
                }
            },
            'backup': {
                'enabled': True,
                'schedule': '0 2 * * *',  # Daily at 2 AM
                'retention_days': 30,
                'include_images': True,
                'include_volumes': False
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    # Merge with defaults
                    self._merge_config(default_config, file_config)
                    logger.info(f"Loaded Watchtower configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load Watchtower config from {self.config_path}: {e}")
                logger.info("Using default configuration")
        else:
            logger.info(f"Configuration file {self.config_path} not found, using defaults")
        
        return default_config
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_watchtower_args(self) -> list:
        """Get Watchtower command line arguments"""
        args = []
        
        # Basic settings
        if self.get('watchtower.update_interval'):
            args.extend(['--interval', str(self.get('watchtower.update_interval'))])
        
        if self.get('watchtower.cleanup'):
            args.append('--cleanup')
        
        if self.get('watchtower.auto_update'):
            args.append('--run-once')
        
        if self.get('watchtower.docker_socket'):
            args.extend(['--docker-socket', self.get('watchtower.docker_socket')])
        
        if self.get('watchtower.include_stopped'):
            args.append('--include-stopped')
        
        if self.get('watchtower.revive_stopped'):
            args.append('--revive-stopped')
        
        if self.get('watchtower.remove_volumes'):
            args.append('--remove-volumes')
        
        if self.get('watchtower.label_enable'):
            args.append('--label-enable')
        
        if self.get('watchtower.scope'):
            args.extend(['--scope', self.get('watchtower.scope')])
        
        # HTTP API
        if self.get('watchtower.http_api'):
            args.append('--http-api')
            args.extend(['--http-api-port', str(self.get('watchtower.http_api_port'))])
            
            if self.get('watchtower.http_api_token'):
                args.extend(['--http-api-token', self.get('watchtower.http_api_token')])
            
            if self.get('watchtower.http_api_metrics'):
                args.append('--http-api-metrics')
        
        # Notifications
        if self.get('watchtower.notification_url'):
            args.extend(['--notification-url', self.get('watchtower.notification_url')])
        
        return args
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check required fields
        if not self.get('watchtower.enabled'):
            errors.append("Watchtower is disabled")
        
        # Validate intervals
        update_interval = self.get('watchtower.update_interval')
        if update_interval and (update_interval < 30 or update_interval > 86400):
            errors.append("Update interval must be between 30 and 86400 seconds")
        
        monitoring_interval = self.get('watchtower.monitoring_interval')
        if monitoring_interval and (monitoring_interval < 10 or monitoring_interval > 300):
            errors.append("Monitoring interval must be between 10 and 300 seconds")
        
        # Validate notification settings
        if self.get('notifications.slack.enabled') and not self.get('notifications.slack.webhook_url'):
            errors.append("Slack notifications enabled but no webhook URL provided")
        
        if self.get('notifications.email.enabled'):
            email_config = self.get('notifications.email')
            required_fields = ['smtp_host', 'username', 'password', 'from', 'to']
            for field in required_fields:
                if not email_config.get(field):
                    errors.append(f"Email notification enabled but {field} not configured")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def get_docker_compose_config(self) -> Dict[str, Any]:
        """Get Docker Compose configuration for Watchtower"""
        return {
            'version': '3.8',
            'services': {
                'watchtower': {
                    'image': 'containrrr/watchtower:latest',
                    'container_name': 'watchtower',
                    'restart': 'unless-stopped',
                    'environment': [
                        'WATCHTOWER_CLEANUP=true',
                        'WATCHTOWER_INCLUDE_STOPPED=false',
                        'WATCHTOWER_REVIVE_STOPPED=false',
                        'WATCHTOWER_REMOVE_VOLUMES=false',
                        'WATCHTOWER_LABEL_ENABLE=true',
                        'WATCHTOWER_HTTP_API=true',
                        'WATCHTOWER_HTTP_API_PORT=8080',
                        'WATCHTOWER_HTTP_API_METRICS=true'
                    ],
                    'volumes': [
                        '/var/run/docker.sock:/var/run/docker.sock',
                        '/var/lib/docker/volumes:/var/lib/docker/volumes'
                    ],
                    'ports': [
                        f"{self.get('watchtower.http_api_port')}:8080"
                    ],
                    'command': ' '.join(self.get_watchtower_args())
                }
            }
        }
    
    def get_systemd_service_config(self) -> str:
        """Get systemd service configuration"""
        return f"""[Unit]
Description=Watchtower Container Update Monitor
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/docker run --rm \\
    --name watchtower \\
    --restart unless-stopped \\
    -v /var/run/docker.sock:/var/run/docker.sock \\
    -v /var/lib/docker/volumes:/var/lib/docker/volumes \\
    -p {self.get('watchtower.http_api_port')}:8080 \\
    containrrr/watchtower:latest \\
    {' '.join(self.get_watchtower_args())}
ExecStop=/usr/bin/docker stop watchtower
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""


# Global configuration instance
watchtower_config = WatchtowerConfig() 