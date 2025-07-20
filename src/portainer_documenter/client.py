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