#!/usr/bin/env python3
"""
Portainer Documentation Service - Main Entry Point

This service continuously generates documentation for Portainer environments including:
- Custom templates
- Stacks with Docker Compose contents
- License information
- Authentication configurations
- Registry configurations

The service supports multiple Portainer hosts and runs on a configurable schedule.
"""

import sys
import os
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from portainer_documenter.service import PortainerDocumentationService
from portainer_documenter.config import Config


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter with timezone-aware timestamps
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %Z'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def main():
    """
    Start the Portainer Documentation Service.
    
    The service will:
    1. Load configuration from environment variables
    2. Generate documentation immediately on startup
    3. Schedule daily documentation generation
    4. Keep running to maintain the schedule
    """
    # Check for verbose logging
    verbose = os.getenv('PORTAINER_VERBOSE', '').lower() in ['true', '1', 'yes', 'on']
    
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Portainer Documentation Service")
        
        # Load configuration
        config = Config()
        
        # Log configuration info (without sensitive data)
        logger.info(f"Service configuration:")
        logger.info(f"  - Timezone: {config.portainer_timezone}")
        logger.info(f"  - Schedule: {config.portainer_schedule_time}")
        logger.info(f"  - Output directory: {config.portainer_output_dir}")
        logger.info(f"  - Output format: {config.output_format}")
        logger.info(f"  - Configured hosts: {len(config.get_hosts())}")
        
        # Create and start service
        service = PortainerDocumentationService(config)
        service.start_service()
        
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Service startup failed: {e}")
        if verbose:
            logger.exception("Full exception details:")
        sys.exit(1)


if __name__ == '__main__':
    main()