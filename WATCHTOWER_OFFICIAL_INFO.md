# Official Watchtower Repository Information

## 📋 **Repository Details**

- **Repository URL**: https://github.com/containrrr/watchtower
- **Description**: A process for automating Docker container base image updates
- **Clone URL**: https://github.com/containrrr/watchtower.git
- **Default Branch**: main
- **Language**: Go
- **License**: Apache-2.0

## 🚀 **Quick Start (Official)**

```bash
docker run --detach \
    --name watchtower \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    containrrr/watchtower
```

## 📁 **Repository Structure**

```
watchtower/
├── .github/              # GitHub workflows and templates
├── cmd/                  # Command line interface
├── docs/                 # Documentation
├── dockerfiles/          # Docker build files
├── grafana/              # Grafana dashboards
├── internal/             # Internal packages
├── pkg/                  # Public packages
├── prometheus/           # Prometheus configuration
├── scripts/              # Build and deployment scripts
├── build.sh              # Build script
├── docker-compose.yml    # Example Docker Compose
├── go.mod                # Go module definition
├── go.sum                # Go module checksums
├── main.go               # Main entry point
├── README.md             # Project documentation
└── LICENSE.md            # Apache 2.0 license
```

## 🔧 **Key Files**

### Main Entry Point
- **File**: `main.go`
- **Purpose**: Application entry point and initialization
- **Language**: Go

### Module Definition
- **File**: `go.mod`
- **Go Version**: 1.20
- **Module**: github.com/containrrr/watchtower

### Docker Compose Example
```yaml
version: '3.7'

services:
  watchtower:
    container_name: watchtower
    build:
      context: ./
      dockerfile: dockerfiles/Dockerfile.dev-self-contained
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    ports:
      - 8080:8080
    command: --interval 10 --http-api-metrics --http-api-token demotoken --debug prometheus grafana parent child
```

### Build Script
- **File**: `build.sh`
- **Purpose**: Automated build process

## 📚 **Documentation**

- **Full Documentation**: https://containrrr.dev/watchtower
- **README**: Comprehensive setup and usage instructions
- **Contributing**: CONTRIBUTING.md
- **Security**: SECURITY.md

## 🐳 **Docker Images**

- **Official Image**: `containrrr/watchtower`
- **Docker Hub**: https://hub.docker.com/r/containrrr/watchtower
- **Pull Count**: High (actively maintained)

## ⚙️ **Configuration**

### Environment Variables
- `WATCHTOWER_CLEANUP` - Clean up old images
- `WATCHTOWER_POLL_INTERVAL` - Update check interval
- `WATCHTOWER_HTTP_API_TOKEN` - API authentication token
- `WATCHTOWER_HTTP_API_METRICS` - Enable metrics endpoint

### Command Line Flags
- `--interval` - Polling interval in seconds
- `--cleanup` - Remove old images
- `--http-api-metrics` - Enable metrics endpoint
- `--http-api-token` - API authentication token
- `--debug` - Enable debug logging

## 🔒 **Security Notes**

- **Not Recommended for Production**: Watchtower is intended for homelabs, media centers, and local dev environments
- **Docker Socket Access**: Requires access to Docker socket for container management
- **API Authentication**: Supports token-based authentication for HTTP API

## 📊 **Monitoring**

- **Prometheus Metrics**: Built-in metrics endpoint
- **Grafana Dashboards**: Included dashboard configurations
- **HTTP API**: REST API for monitoring and control

## 🚨 **Important Notes**

1. **Production Use**: Not recommended for commercial/production environments
2. **Kubernetes Alternative**: For production, consider Kubernetes with MicroK8s or k3s
3. **Docker Socket**: Requires privileged access to Docker socket
4. **Image Registry**: Works with Docker Hub and private registries

## 🔗 **Related Projects**

- **Shoutrrr**: Notification service integration
- **Docker CLI**: Container management
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## 📈 **Development Status**

- **Active Development**: Yes
- **Release Frequency**: Regular releases
- **Community**: Active contributor community
- **CI/CD**: CircleCI integration
- **Code Coverage**: Monitored via Codecov

---

**Note**: This information is current as of the latest repository state. Always refer to the official repository for the most up-to-date information. 