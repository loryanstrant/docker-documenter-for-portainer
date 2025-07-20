"""
Portainer Documentation Service

Service class that handles scheduling and multi-host documentation generation.
"""

import time
import logging
import pytz
from datetime import datetime
from typing import Dict, Any, List
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .client import PortainerClient
from .documenter import PortainerDocumenter
from .config import Config


class PortainerDocumentationService:
    """Service for automated Portainer documentation generation"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scheduler = BlockingScheduler()
        
        # Set up timezone
        try:
            self.timezone = pytz.timezone(self.config.portainer_timezone)
        except pytz.UnknownTimeZoneError:
            self.logger.warning(f"Unknown timezone '{self.config.portainer_timezone}', using UTC")
            self.timezone = pytz.UTC
        
        # Parse schedule time
        try:
            schedule_parts = self.config.portainer_schedule_time.split(':')
            self.schedule_hour = int(schedule_parts[0])
            self.schedule_minute = int(schedule_parts[1])
        except (ValueError, IndexError):
            self.logger.warning(f"Invalid schedule time '{self.config.portainer_schedule_time}', using 02:00")
            self.schedule_hour = 2
            self.schedule_minute = 0
    
    def generate_documentation_for_host(self, host_config: Dict[str, Any]) -> bool:
        """Generate documentation for a single host"""
        host_name = host_config.get('name', 'Unknown')
        
        try:
            self.logger.info(f"Generating documentation for host: {host_name}")
            
            # Initialize Portainer client
            client = PortainerClient(
                url=host_config['url'],
                username=host_config.get('username'),
                password=host_config.get('password'),
                token=host_config.get('token')
            )
            
            # Test connection
            if not client.test_connection():
                self.logger.error(f"Failed to connect to Portainer host: {host_name}")
                return False
            
            self.logger.info(f"Successfully connected to Portainer host: {host_name}")
            
            # Initialize documenter
            documenter = PortainerDocumenter(client, self.config, host_config)
            
            # Generate documentation
            documenter.generate_documentation()
            
            self.logger.info(f"Documentation generation completed for host: {host_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating documentation for host {host_name}: {e}")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception("Full exception details:")
            return False
    
    def generate_all_documentation(self):
        """Generate documentation for all configured hosts"""
        self.logger.info("Starting documentation generation for all hosts")
        
        hosts = self.config.get_hosts()
        if not hosts:
            self.logger.error("No hosts configured")
            return
        
        success_count = 0
        total_count = len(hosts)
        
        for host_config in hosts:
            if self.generate_documentation_for_host(host_config):
                success_count += 1
        
        self.logger.info(f"Documentation generation completed: {success_count}/{total_count} hosts successful")
    
    def start_service(self):
        """Start the documentation service"""
        self.logger.info("Starting Portainer Documentation Service")
        self.logger.info(f"Timezone: {self.config.portainer_timezone}")
        self.logger.info(f"Schedule: Daily at {self.config.portainer_schedule_time}")
        self.logger.info(f"Output directory: {self.config.portainer_output_dir}")
        self.logger.info(f"Configured hosts: {len(self.config.get_hosts())}")
        
        # Validate configuration
        if not self.config.validate():
            self.logger.error("Configuration validation failed")
            return
        
        # Run documentation generation immediately on startup
        self.logger.info("Running initial documentation generation...")
        self.generate_all_documentation()
        
        # Schedule daily runs
        trigger = CronTrigger(
            hour=self.schedule_hour,
            minute=self.schedule_minute,
            timezone=self.timezone
        )
        
        self.scheduler.add_job(
            func=self.generate_all_documentation,
            trigger=trigger,
            id='daily_documentation',
            name='Daily Documentation Generation',
            replace_existing=True
        )
        
        self.logger.info(f"Scheduled daily documentation generation at {self.schedule_hour:02d}:{self.schedule_minute:02d} {self.config.portainer_timezone}")
        
        # Start the scheduler
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
            self.scheduler.shutdown()
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception("Full exception details:")
            self.scheduler.shutdown()
    
    def stop_service(self):
        """Stop the documentation service"""
        self.logger.info("Stopping Portainer Documentation Service")
        if self.scheduler.running:
            self.scheduler.shutdown()