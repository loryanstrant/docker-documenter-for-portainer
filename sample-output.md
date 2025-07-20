# Portainer Environment Documentation

Generated on: 2024-01-15 14:30:22
Portainer URL: https://portainer.example.com

---

## License and Version Information
- **Edition**: Business
- **Version**: 2.19.1
- **License Type**: Commercial
- **License Expiry**: 2024-12-31

## Authentication Configuration
- **Method**: LDAP

### LDAP Configuration
- **Server**: ldaps://ldap.company.com:636
- **Anonymous Mode**: false
- **Base DN**: dc=company,dc=com

## Endpoints (3 total)

### Production Docker
- **Type**: Docker
- **URL**: tcp://prod-docker:2376
- **Status**: Up
- **Group ID**: 1

### Staging Kubernetes
- **Type**: Kubernetes
- **URL**: https://k8s-staging.company.com:6443
- **Status**: Up
- **Group ID**: 2

### Development Environment
- **Type**: Docker
- **URL**: tcp://dev-docker:2376
- **Status**: Up
- **Tags**: [1, 3]

## Stacks (5 total)

### Web Application Stack
- **Status**: Running
- **Endpoint ID**: 1
- **Environment Variables**:
  - `DATABASE_URL=postgresql://user:pass@db:5432/webapp`
  - `REDIS_URL=redis://redis:6379`
  - `API_KEY=api_key_value`

**Docker Compose File:**
```yaml
version: '3.8'
services:
  web:
    image: webapp:latest
    ports:
      - "80:8080"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=webapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### Monitoring Stack
- **Status**: Running
- **Endpoint ID**: 1
- **Environment Variables**:
  - `GRAFANA_ADMIN_PASSWORD=secure_password`

**Docker Compose File:**
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

### API Gateway
- **Status**: Running
- **Endpoint ID**: 2
- **Environment Variables**:
  - `API_RATE_LIMIT=1000`
  - `BACKEND_URL=http://backend:8080`

**Docker Compose File:**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped

  backend:
    image: api-backend:v1.2.0
    environment:
      - RATE_LIMIT=${API_RATE_LIMIT}
    restart: unless-stopped
```

### Database Cluster
- **Status**: Running
- **Endpoint ID**: 1

**Docker Compose File:**
```yaml
version: '3.8'
services:
  mysql-master:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_REPLICATION_MODE=master
      - MYSQL_REPLICATION_USER=repl_user
      - MYSQL_REPLICATION_PASSWORD=repl_password
    volumes:
      - mysql_master_data:/var/lib/mysql
    restart: unless-stopped

  mysql-slave:
    image: mysql:8.0
    environment:
      - MYSQL_REPLICATION_MODE=slave
      - MYSQL_REPLICATION_USER=repl_user
      - MYSQL_REPLICATION_PASSWORD=repl_password
      - MYSQL_MASTER_HOST=mysql-master
    volumes:
      - mysql_slave_data:/var/lib/mysql
    depends_on:
      - mysql-master
    restart: unless-stopped

volumes:
  mysql_master_data:
  mysql_slave_data:
```

### Development Tools
- **Status**: Running
- **Endpoint ID**: 3

**Docker Compose File:**
```yaml
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
    restart: unless-stopped

  nexus:
    image: sonatype/nexus3
    ports:
      - "8081:8081"
    volumes:
      - nexus_data:/nexus-data
    restart: unless-stopped

  sonarqube:
    image: sonarqube:community
    ports:
      - "9000:9000"
    environment:
      - SONAR_JDBC_URL=jdbc:postgresql://postgres:5432/sonar
      - SONAR_JDBC_USERNAME=sonar
      - SONAR_JDBC_PASSWORD=sonar
    volumes:
      - sonarqube_data:/opt/sonarqube/data
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=sonar
      - POSTGRES_PASSWORD=sonar
      - POSTGRES_DB=sonar
    volumes:
      - postgresql_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  jenkins_home:
  nexus_data:
  sonarqube_data:
  postgresql_data:
```

## Custom Templates (4 total)

### WordPress Application
- **Type**: Container
- **Description**: WordPress with MySQL database
- **Platform**: linux

- **Repository**: https://github.com/company/wordpress-template
- **Stack File**: docker-compose.yml

### Node.js Microservice
- **Type**: Container
- **Description**: Node.js microservice template with Redis cache
- **Platform**: linux

- **Repository**: https://github.com/company/nodejs-microservice
- **Stack File**: docker-compose.yml

### Python Data Pipeline
- **Type**: Container
- **Description**: Python data processing pipeline with PostgreSQL
- **Platform**: linux

- **Repository**: https://github.com/company/python-pipeline
- **Stack File**: docker-compose.yml

### React Frontend
- **Type**: Container
- **Description**: React frontend application with Nginx
- **Platform**: linux

- **Repository**: https://github.com/company/react-frontend
- **Stack File**: docker-compose.yml

## Registries (3 total)

### Docker Hub
- **Type**: dockerhub
- **URL**: registry-1.docker.io
- **Authentication**: Yes
- **Username**: company-docker

### Private Registry
- **Type**: private
- **URL**: registry.company.com
- **Authentication**: Yes
- **Username**: automation

### AWS ECR
- **Type**: ecr
- **URL**: 123456789012.dkr.ecr.us-west-2.amazonaws.com
- **Authentication**: Yes
- **Username**: AWS

## Users and Teams
- **Users**: 12 total
- **Teams**: 4 total

### Users
- **admin** (Role: Administrator)
- **devops-lead** (Role: Administrator)
- **developer1** (Role: User)
- **developer2** (Role: User)
- **qa-lead** (Role: User)
- **qa-tester1** (Role: User)
- **qa-tester2** (Role: User)
- **operations** (Role: User)
- **security-team** (Role: User)
- **intern1** (Role: User)
- **intern2** (Role: User)
- **readonly-user** (Role: User)

### Teams
- **Development Team**
- **QA Team**
- **Operations Team**
- **Security Team**