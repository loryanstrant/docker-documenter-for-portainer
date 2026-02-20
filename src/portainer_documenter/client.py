"""
Portainer API Client

Handles authentication and API interactions with Portainer.
"""

import requests
import logging
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class PortainerAPIError(Exception):
    """Custom exception for Portainer API errors"""
    pass


class PortainerClient:
    """Client for interacting with the Portainer API"""
    
    def __init__(self, url: str, username: str = None, password: str = None, token: str = None):
        self.base_url = url.rstrip('/')
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Set up session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'portainer-documenter/1.0.0'
        })
        
        # Authenticate if credentials provided
        if self.token:
            self.session.headers['Authorization'] = f'Bearer {self.token}'
        elif self.username and self.password:
            self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Portainer using username/password"""
        auth_url = urljoin(self.base_url, '/api/auth')
        
        auth_data = {
            'Username': self.username,
            'Password': self.password
        }
        
        try:
            response = self.session.post(auth_url, json=auth_data, timeout=30)
            response.raise_for_status()
            
            auth_result = response.json()
            jwt_token = auth_result.get('jwt')
            
            if not jwt_token:
                raise PortainerAPIError("Authentication failed: No JWT token received")
            
            self.session.headers['Authorization'] = f'Bearer {jwt_token}'
            self.logger.info("Successfully authenticated with Portainer")
            
        except requests.exceptions.RequestException as e:
            raise PortainerAPIError(f"Authentication failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Portainer API"""
        try:
            status = self.get_status()
            return status is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def _make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        """Make an API request to Portainer"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            raise PortainerAPIError(f"API request failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Portainer status information"""
        return self._make_request('/api/status')
    
    def get_settings(self) -> Dict[str, Any]:
        """Get Portainer settings"""
        return self._make_request('/api/settings')
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Get all endpoints (environments)"""
        return self._make_request('/api/endpoints')
    
    def get_stacks(self) -> List[Dict[str, Any]]:
        """Get all stacks"""
        return self._make_request('/api/stacks')
    
    def get_stack_file(self, stack_id: int) -> Dict[str, Any]:
        """Get stack file contents"""
        return self._make_request(f'/api/stacks/{stack_id}/file')
    
    def get_custom_templates(self) -> List[Dict[str, Any]]:
        """Get custom templates"""
        return self._make_request('/api/custom_templates')
    
    def get_registries(self) -> List[Dict[str, Any]]:
        """Get configured registries"""
        return self._make_request('/api/registries')
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get users"""
        return self._make_request('/api/users')
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get teams"""
        return self._make_request('/api/teams')
    
    def get_auth_settings(self) -> Dict[str, Any]:
        """Get authentication settings"""
        settings = self.get_settings()
        return {
            'AuthenticationMethod': settings.get('AuthenticationMethod', 'Internal'),
            'LDAPSettings': settings.get('LDAPSettings', {}),
            'OAuthSettings': settings.get('OAuthSettings', {}),
            'InternalAuthSettings': settings.get('InternalAuthSettings', {})
        }
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get license information"""
        try:
            status = self.get_status()
            return {
                'Edition': status.get('Edition', 'Community'),
                'Version': status.get('Version', 'Unknown'),
                'License': status.get('License', {})
            }
        except Exception as e:
            self.logger.warning(f"Could not retrieve license info: {e}")
            return {'Edition': 'Unknown', 'Version': 'Unknown', 'License': {}}
    
    def get_endpoint_stacks(self, endpoint_id: int) -> List[Dict[str, Any]]:
        """Get stacks for a specific endpoint"""
        stacks = self.get_stacks()
        return [stack for stack in stacks if stack.get('EndpointId') == endpoint_id]
    
    def get_all_stack_details(self) -> List[Dict[str, Any]]:
        """Get detailed information for all stacks including their compose files"""
        stacks = self.get_stacks()
        detailed_stacks = []
        
        for stack in stacks:
            try:
                stack_file = self.get_stack_file(stack['Id'])
                stack['ComposeFile'] = stack_file.get('StackFileContent', '')
            except Exception as e:
                self.logger.warning(f"Could not get compose file for stack {stack['Id']}: {e}")
                stack['ComposeFile'] = 'Could not retrieve compose file'
            
            detailed_stacks.append(stack)
        
        return detailed_stacks
    
    def get_images(self, endpoint_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all images, optionally filtered by endpoint"""
        try:
            if endpoint_id:
                return self._make_request(f'/api/endpoints/{endpoint_id}/docker/images/json')
            else:
                endpoints = self.get_endpoints()
                all_images = []

                for endpoint in endpoints:
                    try:
                        images = self._make_request(f'/api/endpoints/{endpoint["Id"]}/docker/images/json')
                        for image in images:
                            image['EndpointId'] = endpoint['Id']
                            image['EndpointName'] = endpoint.get('Name', 'Unknown')
                        all_images.extend(images)
                    except Exception as e:
                        self.logger.warning(f"Could not get images for endpoint {endpoint['Id']}: {e}")
                        continue

                return all_images
        except Exception as e:
            self.logger.error(f"Failed to get images: {e}")
            return []

    def get_containers(self, endpoint_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all containers, optionally filtered by endpoint"""
        try:
            if endpoint_id:
                # Get containers for specific endpoint
                return self._make_request(f'/api/endpoints/{endpoint_id}/docker/containers/json?all=true')
            else:
                # Get containers for all endpoints
                endpoints = self.get_endpoints()
                all_containers = []
                
                for endpoint in endpoints:
                    try:
                        containers = self._make_request(f'/api/endpoints/{endpoint["Id"]}/docker/containers/json?all=true')
                        # Add endpoint info to each container
                        for container in containers:
                            container['EndpointId'] = endpoint['Id']
                            container['EndpointName'] = endpoint.get('Name', 'Unknown')
                        all_containers.extend(containers)
                    except Exception as e:
                        self.logger.warning(f"Could not get containers for endpoint {endpoint['Id']}: {e}")
                        continue
                
                return all_containers
        except Exception as e:
            self.logger.error(f"Failed to get containers: {e}")
            return []
    
    def analyze_stack_deployments(self) -> Dict[str, Any]:
        """Analyze stack deployments by cross-referencing with running containers"""
        stacks = self.get_stacks()
        containers = self.get_containers()
        
        stack_deployments = {}
        
        for stack in stacks:
            stack_name = stack.get('Name', '')
            stack_id = stack.get('Id')
            endpoint_id = stack.get('EndpointId')
            
            # Find containers for this stack
            stack_containers = []
            
            for container in containers:
                # Skip if container is on different endpoint
                if container.get('EndpointId') != endpoint_id:
                    continue
                
                # Check Docker Compose labels
                labels = container.get('Labels', {}) or {}
                
                # Check for stack match using various label patterns
                matches_stack = False
                
                # Pattern 1: com.docker.compose.project
                compose_project = labels.get('com.docker.compose.project', '')
                if compose_project.lower() == stack_name.lower():
                    matches_stack = True
                
                # Pattern 2: io.portainer.stack.name (Portainer-specific)
                portainer_stack = labels.get('io.portainer.stack.name', '')
                if portainer_stack.lower() == stack_name.lower():
                    matches_stack = True
                
                # Pattern 3: Stack name in container name
                container_names = container.get('Names', [])
                for name in container_names:
                    # Remove leading slash and check if stack name is in container name
                    clean_name = name.lstrip('/')
                    if stack_name.lower() in clean_name.lower():
                        matches_stack = True
                        break
                
                if matches_stack:
                    stack_containers.append({
                        'Id': container.get('Id', ''),
                        'Names': container.get('Names', []),
                        'Image': container.get('Image', ''),
                        'State': container.get('State', ''),
                        'Status': container.get('Status', ''),
                        'Labels': labels
                    })
            
            # Count running vs total containers
            running_containers = [c for c in stack_containers if c.get('State') == 'running']
            
            stack_deployments[stack_name] = {
                'stack_info': stack,
                'containers': stack_containers,
                'total_containers': len(stack_containers),
                'running_containers': len(running_containers),
                'deployment_status': 'active' if running_containers else ('partial' if stack_containers else 'none'),
                'status_indicator': '✅' if running_containers else ('⚠️' if stack_containers else '❌')
            }
        
        return stack_deployments
    
    def analyze_template_deployments(self) -> Dict[str, Any]:
        """Analyze which custom templates have been deployed as stacks"""
        try:
            templates = self.get_custom_templates()
            stacks = self.get_stacks()
            
            template_deployments = {}
            
            for template in templates:
                template_title = template.get('Title', '')
                template_id = template.get('Id')
                
                # Find stacks that might be deployed from this template
                deployed_stacks = []
                
                for stack in stacks:
                    stack_name = stack.get('Name', '')
                    
                    # Check if stack name matches or contains template title
                    if (template_title.lower() in stack_name.lower() or 
                        stack_name.lower() in template_title.lower()):
                        deployed_stacks.append({
                            'name': stack_name,
                            'id': stack.get('Id'),
                            'status': stack.get('Status'),
                            'endpoint_id': stack.get('EndpointId')
                        })
                
                deployment_count = len(deployed_stacks)
                template_deployments[template_title] = {
                    'template_info': template,
                    'deployed_stacks': deployed_stacks,
                    'deployment_count': deployment_count,
                    'deployment_status': 'deployed' if deployment_count > 0 else 'unused',
                    'status_indicator': '✅' if deployment_count > 0 else '❌'
                }
            
            return template_deployments
            
        except Exception as e:
            self.logger.error(f"Failed to analyze template deployments: {e}")
            return {}