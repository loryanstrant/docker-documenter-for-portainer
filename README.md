# Portainer Documentation Service

A comprehensive documentation service for Portainer that continuously generates documentation for multiple Portainer environments. This service connects to your Portainer instances via the API and generates readable documentation including stacks, templates, registries, and more on a scheduled basis.

## Features

- **📋 Comprehensive Documentation**: Extract and document all aspects of your Portainer environments
- **🔄 Continuous Service**: Runs as a service with scheduled documentation generation
- **🏢 Multi-Host Support**: Document multiple Portainer instances in separate files
- **🕐 Timezone Aware**: Configurable timezone support for scheduling and logging
- **📅 Daily Scheduling**: Automatic daily documentation generation at configured time
- **📁 File Versioning**: Automatic backup of existing files with timestamps
- **🐳 Stack Documentation**: Include complete Docker Compose files in the output
- **📝 Custom Templates**: Document all custom application templates
- **🔐 Authentication Settings**: Capture LDAP, OAuth, and internal auth configurations (no sensitive data)
- **📊 License Information**: Document Portainer edition and license details
- **🗂️ Registry Management**: List and document all configured registries
- **👥 User Management**: Document users and teams
- **📄 Multiple Formats**: Generate documentation in Markdown or JSON
- **🐳 Containerized**: Runs as a Docker container for easy deployment
- **🔒 Security Focused**: No sensitive information (tokens, passwords) included in documentation

## Quick Start

### Service Mode (Recommended)

Run as a continuous service that generates documentation daily:

```bash
# Create output directory
mkdir -p ./documentation

# Run service with multiple Portainer hosts
docker run -d --name portainer-documenter \
  --restart unless-stopped \
  -v $(pwd)/documentation:/output \
  -e PORTAINER_TIMEZONE="America/New_York" \
  -e PORTAINER_SCHEDULE_TIME="02:00" \
  -e PORTAINER_HOSTS='[
    {
      "name": "production",
      "url": "https://portainer-prod.example.com",
      "token": "ptr_your-production-token"
    },
    {
      "name": "staging",
      "url": "https://portainer-staging.example.com", 
      "username": "admin",
      "password": "your-staging-password"
    }
  ]' \
  ghcr.io/loryanstrant/docker-documenter-for-portainer:latest
```

### Legacy Single-Host Mode

For backward compatibility, you can still use single-host configuration:

```bash
docker run -d --name portainer-documenter \
  --restart unless-stopped \
  -v $(pwd)/documentation:/output \
  -e PORTAINER_URL=https://your-portainer.com \
  -e PORTAINER_TOKEN=your-api-token \
  -e PORTAINER_SCHEDULE_TIME="03:00" \
  ghcr.io/loryanstrant/docker-documenter-for-portainer:latest
```

## Service Configuration

### Environment Variables

The service is configured entirely through environment variables:

#### Core Service Settings

```bash
# Timezone for scheduling and logging (default: UTC)
PORTAINER_TIMEZONE=America/New_York

# Daily documentation generation time in 24-hour format (default: 02:00)  
PORTAINER_SCHEDULE_TIME=02:00

# Output directory for documentation files (default: /output)
PORTAINER_OUTPUT_DIR=/output

# Output format: markdown or json (default: markdown)
PORTAINER_OUTPUT_FORMAT=markdown

# Enable verbose logging (default: false)
PORTAINER_VERBOSE=true
```

#### Multi-Host Configuration

Configure multiple Portainer hosts using a JSON array:

```bash
PORTAINER_HOSTS='[
  {
    "name": "production",
    "url": "https://portainer-prod.example.com",
    "token": "ptr_your-production-api-token"
  },
  {
    "name": "staging",
    "url": "https://portainer-staging.example.com", 
    "username": "admin",
    "password": "your-staging-password"
  },
  {
    "name": "development",
    "url": "https://portainer-dev.example.com",
    "token": "ptr_your-development-api-token"
  }
]'
```

Each host configuration requires:
- `name`: Unique identifier for the host (used in filename)
- `url`: Portainer instance URL
- Authentication: Either `token` OR `username`+`password`

#### Legacy Single-Host Configuration

For backward compatibility:

```bash
PORTAINER_URL=https://your-portainer.com
PORTAINER_TOKEN=your-api-token
# OR
PORTAINER_USERNAME=admin
PORTAINER_PASSWORD=your-password
```

#### Feature Flags

Control what information is included in documentation:

```bash
PORTAINER_INCLUDE_COMPOSE_FILES=true    # Include Docker Compose files
PORTAINER_INCLUDE_TEMPLATES=true        # Include custom templates
PORTAINER_INCLUDE_REGISTRIES=true       # Include registry configurations  
PORTAINER_INCLUDE_AUTH_SETTINGS=true    # Include authentication settings
PORTAINER_INCLUDE_LICENSE_INFO=true     # Include license information
PORTAINER_INCLUDE_USERS_TEAMS=true      # Include user and team information
```

### Docker Compose Example

Use the provided `docker-compose.service.yml` file:

```yaml
version: '3.8'

services:
  portainer-documenter:
    image: ghcr.io/loryanstrant/docker-documenter-for-portainer:latest
    container_name: portainer-documenter
    restart: unless-stopped
    
    environment:
      PORTAINER_TIMEZONE: "America/New_York"
      PORTAINER_SCHEDULE_TIME: "02:00"
      PORTAINER_HOSTS: |
        [
          {
            "name": "production",
            "url": "https://portainer-prod.example.com",
            "token": "ptr_your-production-token"
          },
          {
            "name": "staging", 
            "url": "https://portainer-staging.example.com",
            "username": "admin",
            "password": "your-staging-password"
          }
        ]
    
    volumes:
      - ./documentation:/output
```

Deploy with: `docker-compose -f docker-compose.service.yml up -d`

## Generated Documentation Files

### Multi-Host Mode

Each configured host generates its own documentation file:
- `{host-name}-docs.md` (or `.json` for JSON format)
- Example: `production-docs.md`, `staging-docs.md`

### File Versioning

Before generating new documentation, existing files are automatically backed up with timestamps:
- Original: `production-docs.md`
- Backup: `production-docs_20240120_143052.md`

### Legacy Mode

Single file output (backward compatibility):
- `portainer-docs.md` (or configured filename)

## Service Behavior

1. **Startup**: Service starts and immediately generates documentation for all configured hosts
2. **Scheduling**: Sets up daily documentation generation at the configured time
3. **Continuous Running**: Service remains running to maintain the schedule
4. **File Management**: Automatically backs up existing files before generating new ones
5. **Error Handling**: Failed host connections don't prevent other hosts from being documented
6. **Logging**: Comprehensive logging with timezone-aware timestamps

## Authentication

The service supports two authentication methods per host:

### 1. API Token (Recommended)
Generate an API token in Portainer:
1. Go to User settings → Access tokens
2. Create a new token
3. Use in host configuration: `"token": "ptr_your-token-here"`

### 2. Username/Password
Use your Portainer login credentials:
- Include in host configuration: `"username": "admin", "password": "your-password"`

**Security Note**: Authentication credentials are used only for API connections and are never included in the generated documentation.

## Generated Documentation

The service generates comprehensive documentation including:

### 📊 License and Version Information
- Portainer edition (Community/Business)
- Version information
- License details and expiry dates

### 🔐 Authentication Configuration
- Authentication method (Internal/LDAP/OAuth)
- LDAP server settings (no sensitive data)
- OAuth provider configuration (no client secrets)

### 🏢 Endpoints (Environments)
- All configured Docker environments
- Connection details and status
- Group and tag assignments

### 📚 Stacks
- Complete stack inventory
- Docker Compose file contents
- Environment variables
- Deployment status

### 📝 Custom Templates
- Application templates
- Template descriptions and platforms
- Repository information

### 🗂️ Registries
- Configured Docker registries
- Authentication status (no credentials)
- Registry types and URLs

### 👥 Users and Teams
- User accounts and roles
- Team memberships
- Access permissions

## Sample Output

The service generates comprehensive documentation. Here's an example of what the markdown output looks like:

- **License Information**: Edition, version, and license details
- **Authentication**: LDAP/OAuth configuration details (no sensitive data)
- **Endpoints**: All Docker/Kubernetes environments with connection details
- **Stacks**: Complete inventory with Docker Compose files included
- **Templates**: Custom application templates with repository information
- **Registries**: All configured Docker registries (no credentials)
- **Users & Teams**: User accounts and team memberships

For a complete example, see [sample-output.md](sample-output.md) which shows the full structure and formatting of generated documentation.

## Output Formats

### Markdown Format
Generates a comprehensive, human-readable markdown document with:
- Structured sections for each component
- Code blocks for Docker Compose files
- Tables for configuration data
- Links and navigation

### JSON Format
Generates a machine-readable JSON file with:
- Complete API response data
- Timestamp and metadata
- Nested structure for programmatic access

## CI/CD Integration

The service can be integrated into CI/CD pipelines for automated documentation:

```yaml
# GitHub Actions example - Service Mode
- name: Generate Portainer Documentation
  run: |
    docker run --rm -v ${{ github.workspace }}/docs:/output \
      -e PORTAINER_TIMEZONE="UTC" \
      -e PORTAINER_HOSTS='[{
        "name": "production",
        "url": "${{ secrets.PORTAINER_URL }}",
        "token": "${{ secrets.PORTAINER_TOKEN }}"
      }]' \
      -e PORTAINER_VERBOSE=true \
      ghcr.io/loryanstrant/docker-documenter-for-portainer:latest \
      timeout 60s

- name: Commit Documentation
  run: |
    git add docs/
    git commit -m "Update Portainer documentation"
    git push
```

## Monitoring and Maintenance

### Service Health
- Built-in health checks for container monitoring
- Comprehensive logging with timestamps
- Error handling that doesn't stop the service

### Log Monitoring
Monitor service logs for:
```bash
# View service logs
docker logs portainer-documenter

# Follow live logs
docker logs -f portainer-documenter

# Check for errors
docker logs portainer-documenter 2>&1 | grep ERROR
```

### File Management
- Automatic backup of existing documentation
- Timestamped backup files for history
- Configurable output directory

## Error Handling and Logging

The service includes comprehensive error handling:

- **Connection Issues**: Validates API connectivity per host
- **Authentication Errors**: Clear messages for invalid credentials per host
- **API Failures**: Graceful handling of individual API endpoint failures
- **Partial Data**: Continues operation even if some hosts or data cannot be retrieved
- **Service Continuity**: Failed documentation runs don't stop the service
- **Verbose Logging**: Detailed logging with timezone-aware timestamps

## Development and Testing

### Local Development

```bash
# Clone the repository
git clone https://github.com/loryanstrant/docker-documenter-for-portainer.git
cd docker-documenter-for-portainer

# Install dependencies
pip install -r requirements.txt

# Run service locally
PORTAINER_HOSTS='[{"name": "test", "url": "https://demo.portainer.io", "token": "test"}]' \
PORTAINER_VERBOSE=true \
python main.py
```

### Testing with Docker

```bash
# Build test image
docker build -t portainer-documenter:test .

# Test with sample configuration
docker run --rm \
  -e PORTAINER_HOSTS='[{"name": "test", "url": "https://demo.example.com", "token": "test"}]' \
  -e PORTAINER_VERBOSE=true \
  portainer-documenter:test
```

## Migration from CLI Tool

If you're upgrading from the CLI version:

### Configuration Changes
- **Environment Variables**: Use `PORTAINER_HOSTS` instead of individual `PORTAINER_URL`, etc.
- **Service Mode**: Tool now runs continuously instead of one-time execution
- **File Naming**: Multi-host mode uses `{host-name}-docs.md` format
- **Scheduling**: Built-in daily scheduling replaces external cron jobs

### Backward Compatibility
- Legacy single-host environment variables still work
- Converted automatically to multi-host format
- No breaking changes for existing configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/loryanstrant/docker-documenter-for-portainer/issues)
- 📖 **Documentation**: This README and example files
- 💬 **Discussions**: [GitHub Discussions](https://github.com/loryanstrant/docker-documenter-for-portainer/discussions)

## Roadmap

- [x] Service mode with continuous operation
- [x] Multi-host support
- [x] Scheduled documentation generation
- [x] File versioning and backup
- [x] Timezone support
- [ ] Web UI for configuration and monitoring
- [ ] Integration with popular documentation platforms
- [ ] Additional output formats (PDF, HTML)
- [ ] Documentation comparison between time points
- [ ] Resource usage and performance documentation
- [ ] Webhook notifications for documentation updates
