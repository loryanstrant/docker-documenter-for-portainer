"""
Portainer Documentation Generator

Generates comprehensive documentation from Portainer API data.
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

from .client import PortainerClient
from .config import Config

_UTC_DATETIME_FMT = '%Y-%m-%d %H:%M:%S UTC'


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
        
        # Images
        if self.config.include_images:
            self.logger.info("Collecting images...")
            try:
                self.collected_data['images'] = self.client.get_images()
            except Exception as e:
                self.logger.warning(f"Could not collect images: {e}")
                self.collected_data['images'] = []
        
        # Container deployment analysis
        self.logger.info("Analyzing container deployments...")
        try:
            self.collected_data['stack_deployments'] = self.client.analyze_stack_deployments()
            self.collected_data['template_deployments'] = self.client.analyze_template_deployments()
        except Exception as e:
            self.logger.warning(f"Could not analyze deployments: {e}")
            self.collected_data['stack_deployments'] = {}
            self.collected_data['template_deployments'] = {}
        
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
        
        # Images
        if self.config.include_images:
            content.extend(self._generate_images_section())
        
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

        _endpoint_types = {1: 'Docker', 2: 'Agent', 3: 'Azure ACI', 4: 'Edge Agent (Docker)',
                           5: 'Local Kubernetes', 6: 'Kubernetes (Agent)', 7: 'Edge Agent (Kubernetes)'}
        _endpoint_statuses = {1: 'Up', 2: 'Down'}

        content.append(f"\n## Endpoints ({len(endpoints)} total)")

        for endpoint in endpoints:
            content.append(f"\n### {endpoint.get('Name', 'Unknown')}")

            raw_type = endpoint.get('Type', 'Unknown')
            content.append(f"- **Type**: {_endpoint_types.get(raw_type, raw_type)}")
            content.append(f"- **URL**: {endpoint.get('URL', 'Not specified')}")

            if endpoint.get('PublicURL'):
                content.append(f"- **Public URL**: {endpoint.get('PublicURL')}")

            raw_status = endpoint.get('Status', 'Unknown')
            content.append(f"- **Status**: {_endpoint_statuses.get(raw_status, raw_status)}")

            if endpoint.get('TagIds'):
                content.append(f"- **Tags**: {endpoint.get('TagIds', [])}")

            if endpoint.get('GroupId'):
                content.append(f"- **Group ID**: {endpoint.get('GroupId')}")

            # Snapshot data (container/image/volume counts)
            snapshots = endpoint.get('Snapshots') or []
            if snapshots:
                snap = snapshots[0]
                running = snap.get('RunningContainerCount', snap.get('runningContainerCount', 'N/A'))
                total = snap.get('ContainerCount', snap.get('containerCount', 'N/A'))
                images = snap.get('ImageCount', snap.get('imageCount', 'N/A'))
                volumes = snap.get('VolumeCount', snap.get('volumeCount', 'N/A'))
                content.append(f"- **Containers**: {running}/{total} running")
                content.append(f"- **Images**: {images}")
                content.append(f"- **Volumes**: {volumes}")

        return content
    
    def _generate_stacks_section(self) -> List[str]:
        """Generate stacks section with deployment analysis"""
        content = []
        stacks = self.collected_data.get('stacks', [])
        stack_deployments = self.collected_data.get('stack_deployments', {})

        _stack_types = {1: 'Swarm', 2: 'Compose', 3: 'Kubernetes'}
        _stack_statuses = {1: 'Active', 2: 'Inactive'}

        content.append(f"\n## Stacks ({len(stacks)} total)")
        
        for stack in stacks:
            stack_name = stack.get('Name', 'Unknown')
            content.append(f"\n### {stack_name}")
            
            # Add deployment status if available
            deployment_info = stack_deployments.get(stack_name, {})
            if deployment_info:
                status_indicator = deployment_info.get('status_indicator', '❓')
                deployment_status = deployment_info.get('deployment_status', 'unknown')
                total_containers = deployment_info.get('total_containers', 0)
                running_containers = deployment_info.get('running_containers', 0)
                
                content.append(f"- **Deployment Status**: {status_indicator} {deployment_status.title()}")
                content.append(f"- **Containers**: {running_containers}/{total_containers} running")
                
                # Add container details if available
                containers = deployment_info.get('containers', [])
                if containers:
                    content.append("- **Container Details**:")
                    for container in containers:
                        container_name = container.get('Names', ['Unknown'])[0].lstrip('/')
                        image = container.get('Image', 'Unknown')
                        state = container.get('State', 'Unknown')
                        state_icon = '🟢' if state == 'running' else ('🟡' if state == 'paused' else '🔴')
                        content.append(f"  - {state_icon} `{container_name}` ({image}) - {state}")
            
            # Stack type
            raw_type = stack.get('Type')
            if raw_type is not None:
                content.append(f"- **Type**: {_stack_types.get(raw_type, raw_type)}")

            # Original stack information
            raw_status = stack.get('Status')
            content.append(f"- **Status**: {_stack_statuses.get(raw_status, raw_status)}")
            content.append(f"- **Endpoint ID**: {stack.get('EndpointId', 'Unknown')}")

            # Creation / update metadata
            if stack.get('CreationDate'):
                created_dt = datetime.fromtimestamp(stack['CreationDate'], tz=timezone.utc).strftime(_UTC_DATETIME_FMT)
                line = f"- **Created**: {created_dt}"
                if stack.get('CreatedBy'):
                    line += f" by {stack['CreatedBy']}"
                content.append(line)

            if stack.get('UpdateDate'):
                updated_dt = datetime.fromtimestamp(stack['UpdateDate'], tz=timezone.utc).strftime(_UTC_DATETIME_FMT)
                line = f"- **Last Updated**: {updated_dt}"
                if stack.get('UpdatedBy'):
                    line += f" by {stack['UpdatedBy']}"
                content.append(line)

            # Git configuration
            git_config = stack.get('GitConfig')
            if git_config and git_config.get('URL'):
                content.append(f"- **Git Repository**: {git_config['URL']}")
                if git_config.get('ReferenceName'):
                    content.append(f"- **Git Branch/Ref**: {git_config['ReferenceName']}")
                if git_config.get('ConfigFilePath'):
                    content.append(f"- **Compose File Path**: {git_config['ConfigFilePath']}")

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
        """Generate custom templates section with deployment analysis"""
        content = []
        templates = self.collected_data.get('templates', [])
        template_deployments = self.collected_data.get('template_deployments', {})

        _template_types = {1: 'Swarm', 2: 'Compose', 3: 'Kubernetes'}
        _template_platforms = {1: 'Linux', 2: 'Windows'}
        
        content.append(f"\n## Custom Templates ({len(templates)} total)")
        
        # Add deployment summary
        if template_deployments:
            deployed_count = sum(1 for t in template_deployments.values() if t.get('deployment_count', 0) > 0)
            unused_count = len(template_deployments) - deployed_count
            content.append(f"- **Deployment Summary**: {deployed_count} deployed, {unused_count} unused")
        
        for template in templates:
            template_title = template.get('Title', 'Unknown')
            content.append(f"\n### {template_title}")
            
            # Add deployment status if available
            deployment_info = template_deployments.get(template_title, {})
            if deployment_info:
                status_indicator = deployment_info.get('status_indicator', '❓')
                deployment_count = deployment_info.get('deployment_count', 0)
                deployment_status = deployment_info.get('deployment_status', 'unknown')
                
                content.append(f"- **Deployment Status**: {status_indicator} {deployment_status.title()}")
                if deployment_count > 0:
                    content.append(f"- **Active Deployments**: {deployment_count}")
                    
                    # List deployed stacks
                    deployed_stacks = deployment_info.get('deployed_stacks', [])
                    if deployed_stacks:
                        content.append("- **Deployed as Stacks**:")
                        for stack in deployed_stacks:
                            content.append(f"  - `{stack.get('name', 'Unknown')}` (Status: {stack.get('status', 'Unknown')})")
            
            # Original template information
            raw_type = template.get('Type')
            content.append(f"- **Type**: {_template_types.get(raw_type, raw_type)}")
            if template.get('Description'):
                content.append(f"- **Description**: {template.get('Description')}")

            if template.get('Note'):
                content.append(f"- **Note**: {template.get('Note')}")

            raw_platform = template.get('Platform')
            if raw_platform is not None:
                content.append(f"- **Platform**: {_template_platforms.get(raw_platform, raw_platform)}")

            if template.get('Categories'):
                content.append(f"- **Categories**: {', '.join(template['Categories'])}")

            if template.get('Logo'):
                content.append(f"- **Logo**: {template.get('Logo')}")

            if template.get('Repository'):
                repo = template['Repository']
                content.append(f"- **Repository**: {repo.get('url', 'Unknown')}")
                if repo.get('stackfile'):
                    content.append(f"- **Stack File**: {repo.get('stackfile')}")

            # Default environment variables defined by the template
            if template.get('Env'):
                content.append("- **Environment Variables**:")
                for env_var in template['Env']:
                    label = env_var.get('label') or env_var.get('name', 'Unknown')
                    default = env_var.get('default', '')
                    default_str = f" (default: `{default}`)" if default else ''
                    content.append(f"  - `{env_var.get('name', 'Unknown')}` — {label}{default_str}")

            # Template variables (mustache-style)
            if template.get('Variables'):
                content.append("- **Template Variables**:")
                for var in template['Variables']:
                    label = var.get('label') or var.get('name', 'Unknown')
                    content.append(f"  - `{var.get('name', 'Unknown')}` — {label}")
        
        return content
    
    def _generate_registries_section(self) -> List[str]:
        """Generate registries section"""
        content = []
        registries = self.collected_data.get('registries', [])

        _registry_types = {1: 'Quay', 2: 'Azure', 3: 'Custom', 4: 'GitLab',
                           5: 'ProGet', 6: 'DockerHub', 7: 'ECR', 8: 'GitHub'}

        content.append(f"\n## Registries ({len(registries)} total)")
        
        for registry in registries:
            content.append(f"\n### {registry.get('Name', 'Unknown')}")
            if registry.get('Id') is not None:
                content.append(f"- **ID**: {registry.get('Id')}")
            raw_type = registry.get('Type', 'Unknown')
            content.append(f"- **Type**: {_registry_types.get(raw_type, raw_type)}")
            content.append(f"- **URL**: {registry.get('URL', 'Unknown')}")
            if registry.get('BaseURL') and registry.get('BaseURL') != registry.get('URL'):
                content.append(f"- **Base URL**: {registry.get('BaseURL')}")
            content.append(f"- **Authentication**: {'Yes' if registry.get('Authentication') else 'No'}")
            
            if registry.get('Username'):
                content.append(f"- **Username**: {registry.get('Username')}")
        
        return content
    
    def _generate_users_teams_section(self) -> List[str]:
        """Generate users and teams section"""
        content = []
        users = self.collected_data.get('users', [])
        teams = self.collected_data.get('teams', [])

        _role_names = {1: 'Administrator', 2: 'Standard User'}

        content.append(f"\n## Users and Teams")
        content.append(f"- **Users**: {len(users)} total")
        content.append(f"- **Teams**: {len(teams)} total")
        
        if users:
            content.append("\n### Users")
            for user in users:
                raw_role = user.get('Role', 'Unknown')
                role_name = _role_names.get(raw_role, raw_role)
                content.append(f"- **{user.get('Username', 'Unknown')}** (Role: {role_name})")
        
        if teams:
            content.append("\n### Teams")
            for team in teams:
                content.append(f"- **{team.get('Name', 'Unknown')}**")
        
        return content

    def _generate_images_section(self) -> List[str]:
        """Generate images section"""
        content = []
        images = self.collected_data.get('images', [])

        content.append(f"\n## Images ({len(images)} total)")

        for image in images:
            repo_tags = image.get('RepoTags') or []
            image_id_raw = image.get('Id') or ''
            short_id = image_id_raw[7:19] if image_id_raw.startswith('sha256:') else image_id_raw[:12]
            tag_label = repo_tags[0] if repo_tags else (short_id or 'Unknown')
            content.append(f"\n### {tag_label}")

            if len(repo_tags) > 1:
                content.append(f"- **Tags**: {', '.join(repo_tags)}")

            content.append(f"- **ID**: {short_id}")

            repo_digests = image.get('RepoDigests') or []
            if repo_digests:
                content.append(f"- **Digest**: {repo_digests[0]}")

            size = image.get('Size', 0)
            if size:
                size_mb = size / (1024 * 1024)
                content.append(f"- **Size**: {size_mb:.1f} MB")

            virtual_size = image.get('VirtualSize') or image.get('virtualSize', 0)
            if virtual_size and virtual_size != size:
                virtual_size_mb = virtual_size / (1024 * 1024)
                content.append(f"- **Virtual Size**: {virtual_size_mb:.1f} MB")

            created = image.get('Created')
            if created:
                content.append(f"- **Created**: {datetime.fromtimestamp(created, tz=timezone.utc).strftime(_UTC_DATETIME_FMT)}")

            containers_count = image.get('Containers')
            if containers_count is not None:
                content.append(f"- **Containers Using Image**: {containers_count}")

            if image.get('EndpointName'):
                content.append(f"- **Endpoint**: {image.get('EndpointName')}")

            if image.get('Labels'):
                labels = image['Labels']
                content.append("- **Labels**:")
                for key, value in labels.items():
                    content.append(f"  - `{key}`: {value}")

        return content