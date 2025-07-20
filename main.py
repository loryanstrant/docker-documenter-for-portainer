#!/usr/bin/env python3
"""
Portainer Documentation Tool - Main Entry Point

This tool extracts and documents various Portainer configurations including:
- Custom templates
- Stacks with Docker Compose contents
- License information
- Authentication configurations
- Registry configurations
"""

import sys
import os
import logging
import click
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from portainer_documenter.client import PortainerClient
from portainer_documenter.documenter import PortainerDocumenter
from portainer_documenter.config import Config


@click.command()
@click.option('--url', '-u', required=True, help='Portainer URL (e.g., https://portainer.example.com)')
@click.option('--username', help='Portainer username (can also use PORTAINER_USERNAME env var)')
@click.option('--password', help='Portainer password (can also use PORTAINER_PASSWORD env var)')
@click.option('--token', help='Portainer API token (can also use PORTAINER_TOKEN env var)')
@click.option('--output', '-o', default='portainer-docs.md', help='Output file path')
@click.option('--format', '-f', default='markdown', type=click.Choice(['markdown', 'json']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Configuration file path')
def main(url, username, password, token, output, format, verbose, config):
    """
    Generate comprehensive documentation for Portainer environments.
    
    This tool connects to a Portainer instance and extracts configuration data
    to generate readable documentation including stacks, templates, and settings.
    """
    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config_obj = Config(config_file=config)
        
        # Override with command line arguments
        if url:
            config_obj.portainer_url = url
        if username:
            config_obj.username = username
        if password:
            config_obj.password = password
        if token:
            config_obj.token = token
        if output:
            config_obj.output_file = output
        if format:
            config_obj.output_format = format
            
        # Validate configuration
        if not config_obj.portainer_url:
            logger.error("Portainer URL is required")
            sys.exit(1)
            
        if not config_obj.token and not (config_obj.username and config_obj.password):
            logger.error("Either API token or username/password is required")
            sys.exit(1)
        
        logger.info(f"Connecting to Portainer at {config_obj.portainer_url}")
        
        # Initialize Portainer client
        client = PortainerClient(
            url=config_obj.portainer_url,
            username=config_obj.username,
            password=config_obj.password,
            token=config_obj.token
        )
        
        # Test connection
        if not client.test_connection():
            logger.error("Failed to connect to Portainer")
            sys.exit(1)
        
        logger.info("Successfully connected to Portainer")
        
        # Initialize documenter
        documenter = PortainerDocumenter(client, config_obj)
        
        # Generate documentation
        logger.info("Generating documentation...")
        documenter.generate_documentation()
        
        logger.info(f"Documentation generated successfully: {config_obj.output_file}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if verbose:
            logger.exception("Full exception details:")
        sys.exit(1)


if __name__ == '__main__':
    main()