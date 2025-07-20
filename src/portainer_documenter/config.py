"""
Configuration management for Portainer Documenter
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List


class Config:
    """Configuration manager for Portainer Documenter"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Default configuration for service mode
        self.portainer_hosts = []  # List of host configurations
        self.portainer_timezone = 'UTC'
        self.portainer_schedule_time = '02:00'
        self.portainer_output_dir = '/output'
        
        # Legacy single-host support (for backward compatibility)
        self.portainer_url = None
        self.username = None
        self.password = None
        self.token = None
        self.output_file = 'portainer-docs.md'
        self.output_format = 'markdown'
        
        # Feature flags
        self.include_compose_files = True
        self.include_templates = True
        self.include_registries = True
        self.include_auth_settings = True
        self.include_license_info = True
        self.include_users_teams = True
        
        # Load from config file if provided
        if config_file:
            self._load_from_file(config_file)
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from file (JSON or YAML)"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            self.logger.warning(f"Configuration file not found: {config_file}")
            return
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._update_from_dict(config_data)
            self.logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration file {config_file}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # Service-specific environment variables
        portainer_hosts_json = os.getenv('PORTAINER_HOSTS')
        if portainer_hosts_json:
            try:
                self.portainer_hosts = json.loads(portainer_hosts_json)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing PORTAINER_HOSTS JSON: {e}")
                self.portainer_hosts = []
        
        # Service configuration
        if os.getenv('PORTAINER_TIMEZONE'):
            self.portainer_timezone = os.getenv('PORTAINER_TIMEZONE')
        
        if os.getenv('PORTAINER_SCHEDULE_TIME'):
            self.portainer_schedule_time = os.getenv('PORTAINER_SCHEDULE_TIME')
        
        if os.getenv('PORTAINER_OUTPUT_DIR'):
            self.portainer_output_dir = os.getenv('PORTAINER_OUTPUT_DIR')
        
        # Legacy environment variables (for backward compatibility)
        env_mappings = {
            'PORTAINER_URL': 'portainer_url',
            'PORTAINER_USERNAME': 'username',
            'PORTAINER_PASSWORD': 'password',
            'PORTAINER_TOKEN': 'token',
            'PORTAINER_OUTPUT_FILE': 'output_file',
            'PORTAINER_OUTPUT_FORMAT': 'output_format',
        }
        
        for env_var, attr_name in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                setattr(self, attr_name, value)
        
        # Boolean environment variables
        bool_mappings = {
            'PORTAINER_INCLUDE_COMPOSE_FILES': 'include_compose_files',
            'PORTAINER_INCLUDE_TEMPLATES': 'include_templates',
            'PORTAINER_INCLUDE_REGISTRIES': 'include_registries',
            'PORTAINER_INCLUDE_AUTH_SETTINGS': 'include_auth_settings',
            'PORTAINER_INCLUDE_LICENSE_INFO': 'include_license_info',
            'PORTAINER_INCLUDE_USERS_TEAMS': 'include_users_teams',
        }
        
        for env_var, attr_name in bool_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                setattr(self, attr_name, value.lower() in ['true', '1', 'yes', 'on'])
        
        # Convert legacy single-host config to multi-host format if needed
        self._convert_legacy_config()
    
    def _convert_legacy_config(self) -> None:
        """Convert legacy single-host configuration to multi-host format"""
        if not self.portainer_hosts and self.portainer_url:
            host_config = {
                'name': 'default',
                'url': self.portainer_url,
            }
            
            if self.username:
                host_config['username'] = self.username
            if self.password:
                host_config['password'] = self.password
            if self.token:
                host_config['token'] = self.token
            
            self.portainer_hosts = [host_config]
            self.logger.info("Converted legacy single-host config to multi-host format")
    
    def get_hosts(self) -> List[Dict[str, Any]]:
        """Get list of configured Portainer hosts"""
        return self.portainer_hosts
    
    def has_multiple_hosts(self) -> bool:
        """Check if multiple hosts are configured"""
        return len(self.portainer_hosts) > 1
    
    def validate_host_config(self, host_config: Dict[str, Any]) -> bool:
        """Validate a single host configuration"""
        if not host_config.get('url'):
            self.logger.error(f"Host configuration missing 'url': {host_config}")
            return False
        
        if not host_config.get('token') and not (host_config.get('username') and host_config.get('password')):
            self.logger.error(f"Host configuration missing authentication: {host_config}")
            return False
        
        return True
        """Update configuration from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'portainer_hosts': self.portainer_hosts,
            'portainer_timezone': self.portainer_timezone,
            'portainer_schedule_time': self.portainer_schedule_time,
            'portainer_output_dir': self.portainer_output_dir,
            'portainer_url': self.portainer_url,
            'output_file': self.output_file,
            'output_format': self.output_format,
            'include_compose_files': self.include_compose_files,
            'include_templates': self.include_templates,
            'include_registries': self.include_registries,
            'include_auth_settings': self.include_auth_settings,
            'include_license_info': self.include_license_info,
            'include_users_teams': self.include_users_teams,
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to file"""
        config_path = Path(file_path)
        config_data = self.to_dict()
        
        try:
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(config_data, f, default_flow_style=False)
                else:
                    json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {file_path}: {e}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check if we have any hosts configured
        if not self.portainer_hosts:
            self.logger.error("No Portainer hosts configured")
            return False
        
        # Validate each host configuration
        for i, host_config in enumerate(self.portainer_hosts):
            if not self.validate_host_config(host_config):
                self.logger.error(f"Invalid configuration for host {i}")
                return False
        
        if self.output_format not in ['markdown', 'json']:
            self.logger.error("Output format must be 'markdown' or 'json'")
            return False
        
        # Validate schedule time format
        try:
            from datetime import datetime
            datetime.strptime(self.portainer_schedule_time, '%H:%M')
        except ValueError:
            self.logger.error(f"Invalid schedule time format: {self.portainer_schedule_time}. Use HH:MM format.")
            return False
        
        return True