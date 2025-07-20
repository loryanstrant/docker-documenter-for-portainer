# Portainer Documentation Tool

A comprehensive documentation tool for Portainer that extracts and documents various Portainer-specific configurations and data. This tool connects to your Portainer instance via the API and generates readable documentation including stacks, templates, registries, and more.

## Features

- **📋 Comprehensive Documentation**: Extract and document all aspects of your Portainer environment
- **🐳 Stack Documentation**: Include complete Docker Compose files in the output
- **📝 Custom Templates**: Document all custom application templates
- **🔐 Authentication Settings**: Capture LDAP, OAuth, and internal auth configurations
- **📊 License Information**: Document Portainer edition and license details
- **🗂️ Registry Management**: List and document all configured registries
- **👥 User Management**: Document users and teams
- **🏢 Multi-Environment**: Support for multiple Portainer endpoints
- **📄 Multiple Formats**: Generate documentation in Markdown or JSON
- **🐳 Containerized**: Runs as a Docker container for easy deployment

## Quick Start

### Using Docker (Recommended)

```bash
# Using API token (recommended)
docker run --rm -v $(pwd):/output ghcr.io/loryanstrant/docker-documenter-for-portainer:latest \
  --url https://your-portainer.com \
  --token your-api-token \
  --output /output/portainer-docs.md

# Using username/password
docker run --rm -v $(pwd):/output ghcr.io/loryanstrant/docker-documenter-for-portainer:latest \
  --url https://your-portainer.com \
  --username admin \
  --password your-password \
  --output /output/portainer-docs.md
```

### Using Python Directly

```bash
# Clone the repository
git clone https://github.com/loryanstrant/docker-documenter-for-portainer.git
cd docker-documenter-for-portainer

# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py --url https://your-portainer.com --token your-api-token
```

## Usage

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -u, --url TEXT          Portainer URL (e.g., https://portainer.example.com) [required]
  --username TEXT         Portainer username (can also use PORTAINER_USERNAME env var)
  --password TEXT         Portainer password (can also use PORTAINER_PASSWORD env var)
  --token TEXT            Portainer API token (can also use PORTAINER_TOKEN env var)
  -o, --output TEXT       Output file path (default: portainer-docs.md)
  -f, --format TEXT       Output format [markdown|json] (default: markdown)
  -v, --verbose           Enable verbose logging
  -c, --config TEXT       Configuration file path
  --help                  Show this message and exit
```

### Environment Variables

You can configure the tool using environment variables:

```bash
export PORTAINER_URL=https://your-portainer.com
export PORTAINER_TOKEN=your-api-token
export PORTAINER_OUTPUT_FILE=my-docs.md
export PORTAINER_OUTPUT_FORMAT=markdown

# Run without command line arguments
python main.py
```

### Configuration File

Create a configuration file (YAML or JSON) for repeated use:

**config.yml**:
```yaml
portainer_url: "https://your-portainer.com"
token: "your-api-token"
output_file: "portainer-docs.md"
output_format: "markdown"
include_compose_files: true
include_templates: true
include_registries: true
include_auth_settings: true
include_license_info: true
include_users_teams: true
```

**config.json**:
```json
{
  "portainer_url": "https://your-portainer.com",
  "token": "your-api-token",
  "output_file": "portainer-docs.md",
  "output_format": "markdown",
  "include_compose_files": true,
  "include_templates": true
}
```

Use with: `python main.py --config config.yml`

## Authentication

The tool supports two authentication methods:

### 1. API Token (Recommended)
Generate an API token in Portainer:
1. Go to User settings → Access tokens
2. Create a new token
3. Use with `--token` option or `PORTAINER_TOKEN` environment variable

### 2. Username/Password
Use your Portainer login credentials:
- `--username` and `--password` options
- `PORTAINER_USERNAME` and `PORTAINER_PASSWORD` environment variables

## Docker Usage

### Environment Variables with Docker

```bash
docker run --rm -v $(pwd):/output \
  -e PORTAINER_URL=https://your-portainer.com \
  -e PORTAINER_TOKEN=your-api-token \
  -e PORTAINER_OUTPUT_FILE=/output/docs.md \
  ghcr.io/loryanstrant/docker-documenter-for-portainer:latest
```

### Configuration File with Docker

```bash
# Mount your config file
docker run --rm \
  -v $(pwd)/config.yml:/app/config.yml \
  -v $(pwd):/output \
  ghcr.io/loryanstrant/docker-documenter-for-portainer:latest \
  --config /app/config.yml
```

### Docker Compose

```yaml
version: '3.8'
services:
  portainer-documenter:
    image: ghcr.io/loryanstrant/docker-documenter-for-portainer:latest
    environment:
      - PORTAINER_URL=https://your-portainer.com
      - PORTAINER_TOKEN=your-api-token
      - PORTAINER_OUTPUT_FILE=/output/portainer-docs.md
    volumes:
      - ./output:/output
    command: --verbose
```

## Generated Documentation

The tool generates comprehensive documentation including:

### 📊 License and Version Information
- Portainer edition (Community/Business)
- Version information
- License details and expiry dates

### 🔐 Authentication Configuration
- Authentication method (Internal/LDAP/OAuth)
- LDAP server settings
- OAuth provider configuration

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
- Authentication status
- Registry types and URLs

### 👥 Users and Teams
- User accounts and roles
- Team memberships
- Access permissions

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

The tool is designed for automated documentation generation:

```yaml
# GitHub Actions example
- name: Generate Portainer Documentation
  run: |
    docker run --rm -v ${{ github.workspace }}:/output \
      -e PORTAINER_URL=${{ secrets.PORTAINER_URL }} \
      -e PORTAINER_TOKEN=${{ secrets.PORTAINER_TOKEN }} \
      ghcr.io/loryanstrant/docker-documenter-for-portainer:latest

- name: Commit Documentation
  run: |
    git add portainer-docs.md
    git commit -m "Update Portainer documentation"
    git push
```

## Error Handling and Logging

The tool includes comprehensive error handling:

- **Connection Issues**: Validates API connectivity before proceeding
- **Authentication Errors**: Clear messages for invalid credentials
- **API Failures**: Graceful handling of individual API endpoint failures
- **Partial Data**: Continues operation even if some data cannot be retrieved
- **Verbose Logging**: Detailed logging with `--verbose` flag

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/loryanstrant/docker-documenter-for-portainer/issues)
- 📖 **Documentation**: This README and example files
- 💬 **Discussions**: [GitHub Discussions](https://github.com/loryanstrant/docker-documenter-for-portainer/discussions)

## Roadmap

- [ ] Web UI for configuration
- [ ] Scheduled documentation updates
- [ ] Integration with popular documentation platforms
- [ ] Additional output formats (PDF, HTML)
- [ ] Comparison between different time points
- [ ] Resource usage documentation
