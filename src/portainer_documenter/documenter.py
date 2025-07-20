"""
Portainer Documentation Generator

Generates comprehensive documentation from Portainer API data.
"""

import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .client import PortainerClient
from .config import Config


class PortainerDocumenter:
    """Main documentation generator for Portainer"""
    
    def __init__(self, client: PortainerClient, config: Config, host_config: Dict[str, Any] = None):
        self.client = client
        self.config = config
        self.host_config = host_config or {}
        self.logger = logging.getLogger(__name__)
        self.collected_data = {}
    
    def get_output_filename(self) -> str:
        """Generate output filename for this host"""
        host_name = self.host_config.get('name', 'default')
        # Sanitize host name for filename
        safe_name = "".join(c for c in host_name if c.isalnum() or c in ('-', '_')).rstrip()
        return f"{safe_name}-docs.md"
    
    def get_output_path(self) -> Path:
        """Get full output path for this host"""
        filename = self.get_output_filename()
        return Path(self.config.portainer_output_dir) / filename
    
    def backup_existing_file(self) -> None:
        """Backup existing documentation file with timestamp"""
        output_path = self.get_output_path()
        
        if output_path.exists():
            # Create timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{output_path.stem}_{timestamp}{output_path.suffix}"
            backup_path = output_path.parent / backup_name
            
            try:
                shutil.copy2(output_path, backup_path)
                self.logger.info(f"Backed up existing file to: {backup_path}")
            except Exception as e:
                self.logger.warning(f"Could not backup existing file: {e}")
    
    def collect_data(self) -> None:
        """Collect all data from Portainer API"""
        self.logger.info("Collecting data from Portainer...")
        
        # Basic status and license info
        if self.config.include_license_info:
            self.logger.info("Collecting license information...")
            self.collected_data['license'] = self.client.get_license_info()
            self.collected_data['status'] = self.client.get_status()
        
        # Settings and authentication
        if self.config.include_auth_settings:
            self.logger.info("Collecting authentication settings...")
            self.collected_data['auth_settings'] = self.client.get_auth_settings()
            self.collected_data['settings'] = self.client.get_settings()
        
        # Endpoints (environments)
        self.logger.info("Collecting endpoints...")
        self.collected_data['endpoints'] = self.client.get_endpoints()
        
        # Stacks with compose files
        if self.config.include_compose_files:
            self.logger.info("Collecting stacks and compose files...")
            self.collected_data['stacks'] = self.client.get_all_stack_details()
        else:
            self.collected_data['stacks'] = self.client.get_stacks()
        
        # Custom templates
        if self.config.include_templates:
            self.logger.info("Collecting custom templates...")
            try:
                self.collected_data['templates'] = self.client.get_custom_templates()
            except Exception as e:
                self.logger.warning(f"Could not collect templates: {e}")
                self.collected_data['templates'] = []
        
        # Registries
        if self.config.include_registries:
            self.logger.info("Collecting registries...")
            try:
                self.collected_data['registries'] = self.client.get_registries()
            except Exception as e:
                self.logger.warning(f"Could not collect registries: {e}")
                self.collected_data['registries'] = []
        
        # Users and teams
        if self.config.include_users_teams:
            self.logger.info("Collecting users and teams...")
            try:
                self.collected_data['users'] = self.client.get_users()
                self.collected_data['teams'] = self.client.get_teams()
            except Exception as e:
                self.logger.warning(f"Could not collect users/teams: {e}")
                self.collected_data['users'] = []
                self.collected_data['teams'] = []
        
        self.logger.info("Data collection completed")
    
    def generate_documentation(self) -> None:
        """Generate documentation in the specified format"""
        self.collect_data()
        
        # Backup existing file before generating new one
        self.backup_existing_file()
        
        # Ensure output directory exists
        output_path = self.get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.output_format == 'markdown':
            self._generate_markdown()
        elif self.config.output_format == 'json':
            self._generate_json()
        else:
            raise ValueError(f"Unsupported output format: {self.config.output_format}")
    
    def _generate_markdown(self) -> None:
        """Generate markdown documentation"""
        content = []
        
        # Header
        host_name = self.host_config.get('name', 'Unknown')
        host_url = self.host_config.get('url', 'Unknown')
        
        content.append(f"# Portainer Environment Documentation - {host_name}")
        content.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Portainer URL: {host_url}")
        content.append("\n---")
        
        # License and version info
        if self.config.include_license_info:
            content.extend(self._generate_license_section())
        
        # Authentication settings
        if self.config.include_auth_settings:
            content.extend(self._generate_auth_section())
        
        # Endpoints
        content.extend(self._generate_endpoints_section())
        
        # Stacks
        content.extend(self._generate_stacks_section())
        
        # Templates
        if self.config.include_templates:
            content.extend(self._generate_templates_section())
        
        # Registries
        if self.config.include_registries:
            content.extend(self._generate_registries_section())
        
        # Users and Teams
        if self.config.include_users_teams:
            content.extend(self._generate_users_teams_section())
        
        # Write to file
        output_path = self.get_output_path()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        self.logger.info(f"Documentation generated: {output_path}")
    
    def _generate_json(self) -> None:
        """Generate JSON documentation"""
        host_name = self.host_config.get('name', 'Unknown')
        host_url = self.host_config.get('url', 'Unknown')
        
        output_data = {
            'generated_at': datetime.now().isoformat(),
            'host_name': host_name,
            'portainer_url': host_url,
            'data': self.collected_data
        }
        
        output_path = self.get_output_path()
        if self.config.output_format == 'json':
            # Change extension to .json for JSON output
            output_path = output_path.with_suffix('.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        self.logger.info(f"Documentation generated: {output_path}")
    
    def _generate_license_section(self) -> List[str]:
        """Generate license and version information section"""
        content = []
        license_info = self.collected_data.get('license', {})
        status = self.collected_data.get('status', {})
        
        content.append("\n## License and Version Information")
        content.append(f"- **Edition**: {license_info.get('Edition', 'Unknown')}")
        content.append(f"- **Version**: {license_info.get('Version', 'Unknown')}")
        
        if license_info.get('License'):
            license_data = license_info['License']
            content.append(f"- **License Type**: {license_data.get('Type', 'N/A')}")
            if license_data.get('ExpiryDate'):
                content.append(f"- **License Expiry**: {license_data.get('ExpiryDate')}")
        
        return content
    
    def _generate_auth_section(self) -> List[str]:
        """Generate authentication settings section"""
        content = []
        auth_settings = self.collected_data.get('auth_settings', {})
        
        content.append("\n## Authentication Configuration")
        content.append(f"- **Method**: {auth_settings.get('AuthenticationMethod', 'Internal')}")
        
        if auth_settings.get('LDAPSettings') and auth_settings['LDAPSettings']:
            ldap = auth_settings['LDAPSettings']
            content.append("\n### LDAP Configuration")
            content.append(f"- **Server**: {ldap.get('URL', 'Not configured')}")
            content.append(f"- **Anonymous Mode**: {ldap.get('AnonymousMode', False)}")
            content.append(f"- **Base DN**: {ldap.get('BaseDN', 'Not configured')}")
        
        if auth_settings.get('OAuthSettings') and auth_settings['OAuthSettings']:
            oauth = auth_settings['OAuthSettings']
            content.append("\n### OAuth Configuration")
            content.append(f"- **Provider**: {oauth.get('Provider', 'Not configured')}")
            # Remove client ID as it could be considered sensitive
            content.append("- **Client ID**: [Configured]" if oauth.get('ClientID') else "- **Client ID**: Not configured")
        
        return content
    
    def _generate_endpoints_section(self) -> List[str]:
        """Generate endpoints (environments) section"""
        content = []
        endpoints = self.collected_data.get('endpoints', [])
        
        content.append(f"\n## Endpoints ({len(endpoints)} total)")
        
        for endpoint in endpoints:
            content.append(f"\n### {endpoint.get('Name', 'Unknown')}")
            content.append(f"- **Type**: {endpoint.get('Type', 'Unknown')}")
            content.append(f"- **URL**: {endpoint.get('URL', 'Not specified')}")
            content.append(f"- **Status**: {endpoint.get('Status', 'Unknown')}")
            
            if endpoint.get('TagIds'):
                content.append(f"- **Tags**: {endpoint.get('TagIds', [])}")
            
            # Group info
            if endpoint.get('GroupId'):
                content.append(f"- **Group ID**: {endpoint.get('GroupId')}")
        
        return content
    
    def _generate_stacks_section(self) -> List[str]:
        """Generate stacks section"""
        content = []
        stacks = self.collected_data.get('stacks', [])
        
        content.append(f"\n## Stacks ({len(stacks)} total)")
        
        for stack in stacks:
            content.append(f"\n### {stack.get('Name', 'Unknown')}")
            content.append(f"- **Status**: {stack.get('Status', 'Unknown')}")
            content.append(f"- **Endpoint ID**: {stack.get('EndpointId', 'Unknown')}")
            
            if stack.get('Env'):
                content.append("- **Environment Variables**:")
                for env in stack['Env']:
                    content.append(f"  - `{env.get('name', 'Unknown')}={env.get('value', 'Unknown')}`")
            
            # Include compose file if available
            if self.config.include_compose_files and stack.get('ComposeFile'):
                content.append("\n**Docker Compose File:**")
                content.append("```yaml")
                content.append(stack['ComposeFile'])
                content.append("```")
        
        return content
    
    def _generate_templates_section(self) -> List[str]:
        """Generate custom templates section"""
        content = []
        templates = self.collected_data.get('templates', [])
        
        content.append(f"\n## Custom Templates ({len(templates)} total)")
        
        for template in templates:
            content.append(f"\n### {template.get('Title', 'Unknown')}")
            content.append(f"- **Type**: {template.get('Type', 'Unknown')}")
            if template.get('Description'):
                content.append(f"- **Description**: {template.get('Description')}")
            
            if template.get('Platform'):
                content.append(f"- **Platform**: {template.get('Platform')}")
            
            if template.get('Repository'):
                repo = template['Repository']
                content.append(f"- **Repository**: {repo.get('url', 'Unknown')}")
                if repo.get('stackfile'):
                    content.append(f"- **Stack File**: {repo.get('stackfile')}")
        
        return content
    
    def _generate_registries_section(self) -> List[str]:
        """Generate registries section"""
        content = []
        registries = self.collected_data.get('registries', [])
        
        content.append(f"\n## Registries ({len(registries)} total)")
        
        for registry in registries:
            content.append(f"\n### {registry.get('Name', 'Unknown')}")
            content.append(f"- **Type**: {registry.get('Type', 'Unknown')}")
            content.append(f"- **URL**: {registry.get('URL', 'Unknown')}")
            content.append(f"- **Authentication**: {'Yes' if registry.get('Authentication') else 'No'}")
            
            if registry.get('Username'):
                content.append(f"- **Username**: {registry.get('Username')}")
        
        return content
    
    def _generate_users_teams_section(self) -> List[str]:
        """Generate users and teams section"""
        content = []
        users = self.collected_data.get('users', [])
        teams = self.collected_data.get('teams', [])
        
        content.append(f"\n## Users and Teams")
        content.append(f"- **Users**: {len(users)} total")
        content.append(f"- **Teams**: {len(teams)} total")
        
        if users:
            content.append("\n### Users")
            for user in users:
                content.append(f"- **{user.get('Username', 'Unknown')}** (Role: {user.get('Role', 'Unknown')})")
        
        if teams:
            content.append("\n### Teams")
            for team in teams:
                content.append(f"- **{team.get('Name', 'Unknown')}**")
        
        return content