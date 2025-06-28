# ALEX OS Integration Package for Watchtower

## Overview

This package provides everything needed to integrate Watchtower as a native ALEX OS module and replace Watchtower's built-in web dashboard with ALEX OS's comprehensive web interface. The integration provides seamless container monitoring, automated updates, and management through the unified ALEX OS platform.

## Features

- **Native ALEX OS Integration**: Watchtower functionality as a native ALEX OS agent
- **Unified Web Dashboard**: Single interface for all ALEX OS functionality including Watchtower
- **Real-time Monitoring**: Live container status and update notifications via WebSocket
- **Comprehensive API**: Full REST API for programmatic access to Watchtower features
- **Docker Integration**: Direct Docker API integration for container management
- **Custom Raspberry Pi Distribution**: Pre-built image with ALEX OS and Watchtower
- **Automated Deployment**: Scripts for easy deployment to Raspberry Pi

## Architecture

```
ALEX OS Core
├── Watchtower Agent (modules/watchtower.py)
├── API Routes (api/watchtower_routes.py)
├── Web Dashboard (web/templates/watchtower.html)
├── Configuration (config/watchtower_config.py)
└── Deployment Scripts (scripts/)
```

## Quick Start

### 1. Install Dependencies

```bash
# Install ALEX OS dependencies
pip install fastapi uvicorn psutil docker pyyaml

# Install additional packages for Raspberry Pi
pip install RPi.GPIO
```

### 2. Copy Integration Files

```bash
# Copy to your ALEX OS installation
cp -r alexos_integration/modules/* /path/to/alexos/modules/
cp -r alexos_integration/api/* /path/to/alexos/api/
cp -r alexos_integration/web/* /path/to/alexos/web/
cp -r alexos_integration/config/* /path/to/alexos/config/
```

### 3. Update API Server

```python
# In your main API server file
from api.watchtower_routes import register_watchtower_routes, set_watchtower_agent

# Register routes
register_watchtower_routes(app)

# Set agent reference (after creating the agent)
set_watchtower_agent(watchtower_agent)
```

### 4. Update Web Dashboard

```python
# In your web dashboard routes
@app.get("/web/watchtower", response_class=HTMLResponse)
async def watchtower_page(request: Request):
    return templates.TemplateResponse("watchtower.html", {"request": request})
```

### 5. Spawn Watchtower Agent

```python
# In your orchestrator startup
from modules.watchtower import create_watchtower_agent

watchtower_config = {
    'watchtower': {
        'update_interval': 300,
        'cleanup': True,
        'auto_update': False,
        'monitoring_enabled': True,
        'monitoring_interval': 30
    }
}

watchtower_agent = create_watchtower_agent(
    "watchtower-001",
    "Watchtower Monitor",
    event_bus=event_bus,
    ledger=ledger,
    config=watchtower_config
)

await watchtower_agent.start()
set_watchtower_agent(watchtower_agent)
```

## API Endpoints

### Core Endpoints

- `GET /api/watchtower/status` - Get Watchtower agent status
- `GET /api/watchtower/containers` - Get monitored containers
- `GET /api/watchtower/updates` - Get update history
- `POST /api/watchtower/check-updates` - Force update check

### Container Management

- `GET /api/watchtower/containers/{container_id}` - Get container details
- `POST /api/watchtower/containers/{container_id}/update` - Update container
- `POST /api/watchtower/containers/{container_id}/restart` - Restart container
- `POST /api/watchtower/containers/{container_id}/stop` - Stop container
- `POST /api/watchtower/containers/{container_id}/start` - Start container
- `DELETE /api/watchtower/containers/{container_id}` - Remove container

### Docker Management

- `GET /api/watchtower/images` - Get Docker images
- `POST /api/watchtower/images/{image_name}/pull` - Pull Docker image

### Configuration

- `GET /api/watchtower/config` - Get Watchtower configuration
- `PUT /api/watchtower/config` - Update Watchtower configuration

### Statistics

- `GET /api/watchtower/stats` - Get Watchtower statistics

## Configuration

### Watchtower Configuration

```yaml
watchtower:
  enabled: true
  update_interval: 300  # 5 minutes
  cleanup: true
  auto_update: false
  monitoring_enabled: true
  monitoring_interval: 30
  docker_socket: /var/run/docker.sock
  http_api: true
  http_api_port: 8080
```

### Notifications

```yaml
notifications:
  slack:
    enabled: false
    webhook_url: null
    channel: "#watchtower"
  email:
    enabled: false
    smtp_host: null
    smtp_port: 587
    username: null
    password: null
    from: null
    to: []
```

### Security

```yaml
security:
  api_key_required: true
  allowed_ips: []
  rate_limit:
    enabled: true
    requests_per_minute: 60
```

## Raspberry Pi Deployment

### Automated Deployment

```bash
# Make deployment script executable
chmod +x alexos_integration/scripts/deploy_pi.sh

# Deploy to Raspberry Pi
./alexos_integration/scripts/deploy_pi.sh
```

### Custom Distribution

```bash
# Build custom Raspberry Pi OS image
sudo ./alexos_integration/scripts/create_distribution.sh

# Install on SD card
sudo ./alexos-installer.sh
```

## Web Dashboard Features

### Real-time Monitoring

- Live container status updates
- WebSocket-based real-time notifications
- Auto-refresh every 30 seconds
- Visual status indicators

### Container Management

- View all monitored containers
- Container details and statistics
- Start, stop, restart containers
- Manual container updates
- Container removal

### Update Management

- View update history
- Force update checks
- Update status tracking
- Automated update configuration

### Statistics Dashboard

- Total containers count
- Running vs stopped containers
- Update statistics
- System health metrics

## Event System

The Watchtower agent emits events to the ALEX OS event bus:

- `watchtower.watchtower_started` - Agent started
- `watchtower.watchtower_stopped` - Agent stopped
- `watchtower.container_registered` - New container detected
- `watchtower.container_unregistered` - Container removed
- `watchtower.container_status_changed` - Container status changed
- `watchtower.update_detected` - Update available
- `watchtower.update_applied` - Update applied
- `watchtower.update_failed` - Update failed
- `watchtower.watchtower_webhook` - Webhook received

## Docker Integration

The Watchtower agent integrates directly with Docker:

- **Container Discovery**: Automatically detects new containers
- **Status Monitoring**: Tracks container status changes
- **Image Management**: Manages Docker images
- **Update Detection**: Checks for image updates
- **Container Operations**: Start, stop, restart, remove containers

## Security Features

- **API Authentication**: Token-based authentication
- **Rate Limiting**: Configurable request limits
- **IP Whitelisting**: Restrict access by IP address
- **Secure WebSocket**: Encrypted real-time communication
- **Audit Logging**: Comprehensive event logging

## Monitoring and Logging

### Health Monitoring

- Agent status monitoring
- Container health checks
- Update process monitoring
- System resource monitoring

### Logging

- Structured logging with configurable levels
- File-based logging with rotation
- Integration with ALEX OS logging system
- Audit trail for all operations

## Backup and Recovery

### Automated Backups

- Daily backup scheduling
- Container configuration backup
- Image backup (optional)
- Backup retention management

### Recovery Procedures

- Automated recovery scripts
- Configuration restoration
- Container state recovery
- Disaster recovery procedures

## Performance Optimization

### Resource Management

- Efficient container monitoring
- Optimized update checking
- Memory usage optimization
- CPU usage monitoring

### Scalability

- Horizontal scaling support
- Load balancing capabilities
- Multi-node deployment
- Cluster management

## Troubleshooting

### Common Issues

1. **Docker Connection Failed**
   - Check Docker service status
   - Verify Docker socket permissions
   - Ensure user is in docker group

2. **WebSocket Connection Issues**
   - Check firewall settings
   - Verify WebSocket endpoint
   - Check network connectivity

3. **Update Failures**
   - Check image registry access
   - Verify container permissions
   - Review update logs

### Debug Mode

Enable debug logging:

```yaml
logging:
  level: DEBUG
  file: /var/log/alexos/watchtower.log
```

### Health Checks

```bash
# Check agent status
curl http://localhost:8000/api/watchtower/status

# Check container monitoring
curl http://localhost:8000/api/watchtower/containers

# Check system logs
sudo journalctl -u alexos -f
```

## Development

### Adding New Features

1. Extend the `WatchtowerAgent` class
2. Add new API endpoints
3. Update the web dashboard
4. Add configuration options
5. Update documentation

### Testing

```bash
# Run unit tests
python -m pytest tests/test_watchtower.py

# Run integration tests
python -m pytest tests/test_integration.py

# Run API tests
python -m pytest tests/test_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## License

This integration package is licensed under the same license as ALEX OS.

## Support

For support and questions:

- Check the documentation
- Review the troubleshooting guide
- Open an issue on GitHub
- Contact the development team

## Roadmap

### Planned Features

- [ ] Multi-registry support
- [ ] Advanced notification channels
- [ ] Container health checks
- [ ] Automated rollback
- [ ] Performance metrics
- [ ] Cluster management
- [ ] Backup encryption
- [ ] Advanced security features

### Version History

- **v1.0.0** - Initial release with basic integration
- **v1.1.0** - Added real-time monitoring
- **v1.2.0** - Enhanced security features
- **v1.3.0** - Raspberry Pi distribution
- **v1.4.0** - Advanced container management 