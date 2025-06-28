# 🔗 ChainBot + Watchtower ALEX OS Integration

## 📋 **Overview**

This document describes the complete integration between **ChainBot** (AI Agent Orchestration Platform) and **Watchtower** (Container Monitoring & Dashboard) as native ALEX OS modules. The integration provides a unified dashboard experience for managing both container infrastructure and AI agent workflows.

## 🏗️ **Architecture**

### **Module Responsibilities**

#### **Watchtower Module**
- **Container Monitoring**: Real-time Docker container status tracking
- **Dashboard Infrastructure**: Provides the main ALEX OS dashboard framework
- **Agent Management**: Manages ALEX OS system agents
- **Event System**: Handles system events and logging
- **WebSocket**: Real-time updates and notifications

#### **ChainBot Module**
- **AI Agent Orchestration**: Manages ChatGPT, Custom GPTs, and future GPT-5 agents
- **Workflow Management**: Visual workflow builder for AI agent chains
- **ALEX OS Framework Agents**: Internal agents via AgentSpawner
- **Session Management**: Multi-agent chat sessions
- **Entanglement Management**: Complex agent relationships

### **Integration Points**

```
ALEX OS System
├── Watchtower Module (Dashboard Infrastructure)
│   ├── Container Monitoring
│   ├── System Agents
│   ├── Events & Logging
│   └── WebSocket Updates
├── ChainBot Module (AI Orchestration)
│   ├── AI Agent Manager
│   ├── Workflow Orchestrator
│   ├── ALEX OS Agent Spawner
│   └── Entanglement Manager
└── Shared Dashboard Interface
    ├── Agents Tab (Combined View)
    ├── Events Tab (Unified Events)
    ├── Compliance Tab (Security)
    └── ChainBot Tab (AI Workflows)
```

## 🚀 **Implementation**

### **1. ChainBot Agent Module**

**File**: `alexos_integration/modules/chainbot_agent.py`

```python
class ChainBotAgent:
    """ALEX OS ChainBot Agent - Integrates ChainBot's AI orchestration platform"""
    
    def __init__(self, agent_id: str, name: str, event_bus=None, ledger=None, config=None):
        # ChainBot-specific configuration
        self.chainbot_config = config.get('chainbot', {})
        self.chainbot_api_url = self.chainbot_config.get('api_url', 'http://localhost:3000')
        
        # Agent state management
        self.alex_framework_agents = {}  # Internal ALEX OS agents
        self.ai_agents = {}              # External AI agents
        self.workflows = {}
        self.status = "initializing"
```

**Key Features**:
- **Health Monitoring**: Continuous ChainBot API health checks
- **Agent Synchronization**: Syncs both ALEX framework and AI agents
- **Event Emission**: Integrates with ALEX OS event bus
- **Workflow Management**: Executes ChainBot workflows

### **2. ChainBot API Routes**

**File**: `alexos_integration/api/chainbot_routes.py`

**Available Endpoints**:
- `GET /api/chainbot/health` - Health status
- `GET /api/chainbot/status` - Detailed status
- `GET /api/chainbot/agents/alex-framework` - ALEX OS framework agents
- `GET /api/chainbot/agents/ai` - AI agents (ChatGPT, Custom GPTs, etc.)
- `GET /api/chainbot/agents/all` - All ChainBot agents
- `GET /api/chainbot/workflows` - AI workflows
- `POST /api/chainbot/workflows/{id}/execute` - Execute workflows

### **3. ChainBot Dashboard**

**File**: `dashboard/templates/chainbot.html`

**Features**:
- **Modern UI**: Tailwind CSS with responsive design
- **Real-time Updates**: WebSocket integration
- **Agent Management**: View and manage both agent types
- **Workflow Execution**: Execute AI workflows directly
- **Health Monitoring**: Real-time status indicators

### **4. Main Application Integration**

**File**: `main.py`

```python
# Initialize ALEX OS ChainBot agent
chainbot_config = {
    'chainbot': {
        'api_url': os.getenv('CHAINBOT_API_URL', 'http://localhost:3000'),
        'api_key': os.getenv('CHAINBOT_API_KEY'),
        'health_check_interval': 30,
        'sync_interval': 60
    }
}

chainbot_agent = create_chainbot_agent(
    "chainbot-001",
    "ChainBot Orchestrator",
    event_bus=None,
    ledger=None,
    config=chainbot_config
)

await chainbot_agent.start()
initialize_chainbot_routes(chainbot_agent)
```

## 🎯 **Usage Guide**

### **Starting the Integrated System**

1. **Set Environment Variables**:
```bash
export CHAINBOT_API_URL=http://localhost:3000
export CHAINBOT_API_KEY=your_api_key_here
export WATCHTOWER_PORT=8000
```

2. **Start the Application**:
```bash
WATCHTOWER_PORT=8000 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access Dashboards**:
- **Main Dashboard**: http://localhost:8000/dashboard/
- **Watchtower Dashboard**: http://localhost:8000/dashboard/watchtower
- **ChainBot Dashboard**: http://localhost:8000/dashboard/chainbot

### **API Usage Examples**

#### **Get All ChainBot Agents**
```bash
curl http://localhost:8000/api/chainbot/agents/all
```

**Response**:
```json
{
  "agents": [
    {
      "id": "agent-001",
      "name": "Data Processor",
      "status": "running",
      "agent_type": "alex_os_framework_agent",
      "source": "chainbot",
      "capabilities": ["data_processing", "api_integration"]
    },
    {
      "id": "chatgpt-001",
      "name": "GPT-4 Assistant",
      "status": "running",
      "agent_type": "chatgpt",
      "source": "chainbot",
      "provider": "openai",
      "model": "gpt-4"
    }
  ],
  "count": 2,
  "alex_framework_count": 1,
  "ai_agents_count": 1
}
```

#### **Execute a Workflow**
```bash
curl -X POST http://localhost:8000/api/chainbot/workflows/workflow-001/execute \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"prompt": "Hello, world!"}}'
```

#### **Get System Health**
```bash
curl http://localhost:8000/api/chainbot/health
```

## 🧪 **Testing**

### **Run Integration Tests**
```bash
python3 test_chainbot_integration.py
```

**Test Coverage**:
1. ✅ Application startup and health
2. ✅ Watchtower container monitoring
3. ✅ ChainBot agent integration
4. ✅ Dashboard integration
5. ✅ API integration between modules
6. ✅ WebSocket connectivity
7. ✅ Workflow execution

### **Manual Testing**

1. **Health Checks**:
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/watchtower/health
curl http://localhost:8000/api/chainbot/health
```

2. **Dashboard Access**:
```bash
curl http://localhost:8000/dashboard/
curl http://localhost:8000/dashboard/watchtower
curl http://localhost:8000/dashboard/chainbot
```

3. **Agent Management**:
```bash
curl http://localhost:8000/api/chainbot/agents/all
curl http://localhost:8000/api/watchtower/containers
```

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAINBOT_API_URL` | `http://localhost:3000` | ChainBot API endpoint |
| `CHAINBOT_API_KEY` | `None` | ChainBot API authentication key |
| `WATCHTOWER_PORT` | `5000` | Application port |
| `WATCHTOWER_DEBUG` | `False` | Debug mode |

### **ChainBot Configuration**

```yaml
chainbot:
  api_url: http://localhost:3000
  api_key: your_api_key_here
  health_check_interval: 30
  sync_interval: 60
  monitoring_enabled: true
  event_integration: true
```

### **Watchtower Configuration**

```yaml
watchtower:
  update_interval: 300
  cleanup: true
  auto_update: false
  monitoring_enabled: true
  monitoring_interval: 30
  webhook_enabled: true
  log_level: INFO
```

## 📊 **Monitoring & Events**

### **Event Types**

#### **ChainBot Events**
- `chainbot.chainbot_started` - Agent started
- `chainbot.chainbot_stopped` - Agent stopped
- `chainbot.chainbot_health_check` - Health status
- `chainbot.workflow_executed` - Workflow execution
- `chainbot.workflow_execution_failed` - Workflow failure

#### **Watchtower Events**
- `watchtower.container_registered` - Container detected
- `watchtower.watchtower_started` - Watchtower started
- `watchtower.watchtower_stopped` - Watchtower stopped

### **Health Monitoring**

Both modules provide health endpoints:
- `/api/watchtower/health` - Watchtower health
- `/api/chainbot/health` - ChainBot health
- `/api/health` - Overall system health

## 🚀 **Deployment**

### **Production Deployment**

1. **Build and Deploy**:
```bash
# Build the application
docker build -t alexos-watchtower-chainbot .

# Deploy to production
docker run -d \
  --name alexos-watchtower-chainbot \
  -p 8000:8000 \
  -e CHAINBOT_API_URL=http://chainbot:3000 \
  -e CHAINBOT_API_KEY=your_production_key \
  -v /var/run/docker.sock:/var/run/docker.sock \
  alexos-watchtower-chainbot
```

2. **Docker Compose**:
```yaml
version: '3.8'
services:
  alexos-watchtower-chainbot:
    image: alexos-watchtower-chainbot:latest
    ports:
      - "8000:8000"
    environment:
      - CHAINBOT_API_URL=http://chainbot:3000
      - CHAINBOT_API_KEY=${CHAINBOT_API_KEY}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - chainbot
      - chainbot-postgres
```

### **Raspberry Pi Deployment**

```bash
# SSH to Raspberry Pi
ssh alex@10.42.69.208 -p 5420

# Navigate to project directory
cd /opt/alexos/watchtower

# Pull latest changes
git pull origin main

# Start the application
WATCHTOWER_PORT=8000 python3 main.py
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **ChainBot API Connection Failed**:
   - Check `CHAINBOT_API_URL` environment variable
   - Verify ChainBot service is running
   - Check network connectivity

2. **Dashboard Not Loading**:
   - Verify application is running on correct port
   - Check browser console for errors
   - Verify template files exist

3. **WebSocket Connection Issues**:
   - Check firewall settings
   - Verify WebSocket endpoint is accessible
   - Check browser WebSocket support

### **Logs**

Check application logs:
```bash
tail -f logs/watchtower.log
```

### **Debug Mode**

Enable debug mode:
```bash
export WATCHTOWER_DEBUG=true
python3 main.py
```

## 📈 **Performance**

### **Resource Usage**

- **Memory**: ~50-100MB base usage
- **CPU**: Low usage during idle, spikes during workflow execution
- **Network**: Minimal for health checks, variable for workflow execution

### **Scaling**

- **Horizontal**: Deploy multiple instances behind load balancer
- **Vertical**: Increase container resources for higher throughput
- **Database**: Use connection pooling for high-traffic scenarios

## 🔮 **Future Enhancements**

### **Planned Features**

1. **Advanced Workflow Visualization**: Interactive workflow builder
2. **Real-time Collaboration**: Multi-user workflow editing
3. **Advanced Analytics**: Workflow performance metrics
4. **Plugin System**: Extensible agent and workflow types
5. **Mobile Dashboard**: Responsive mobile interface

### **Integration Roadmap**

1. **GPT-5 Integration**: Ready for GPT-5 when available
2. **Multi-Cloud Support**: AWS, Azure, GCP integration
3. **Edge Computing**: Distributed agent deployment
4. **Blockchain Integration**: Decentralized agent networks

## 📚 **References**

- [ChainBot Documentation](https://github.com/chainbot/chainbot)
- [Watchtower Documentation](https://github.com/containrrr/watchtower)
- [ALEX OS Framework](https://github.com/alexos/alexos)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅ 