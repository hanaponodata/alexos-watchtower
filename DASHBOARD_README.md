# Watchtower Enterprise Dashboard

A comprehensive, enterprise-grade dashboard for the Watchtower platform with real-time monitoring, agent management, and compliance tracking.

## 🚀 Features

### Core Features
- **Real-time Monitoring**: Live system metrics, agent status, and event streaming
- **Modern UI/UX**: Beautiful, responsive interface with dark/light mode support
- **Interactive Visualizations**: Charts, graphs, and metrics with Recharts
- **Agent Management**: Monitor and manage connected agents
- **Event Monitoring**: Real-time event filtering and search
- **Compliance Tracking**: Security and compliance monitoring
- **Settings Management**: Comprehensive configuration options

### Technical Features
- **WebSocket Integration**: Real-time data streaming
- **RESTful APIs**: Clean, documented API endpoints
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: WCAG compliant with proper ARIA labels
- **Performance**: Optimized React components with lazy loading
- **Security**: Authentication and authorization ready

## 📊 Dashboard Pages

### 1. Main Dashboard (`/`)
- **System Overview**: Real-time system health and metrics
- **Key Performance Indicators**: CPU, memory, disk, network usage
- **Live Charts**: CPU and memory usage over time
- **Recent Events**: Latest system events with severity indicators
- **Agent Status**: Quick overview of connected agents
- **Compliance Score**: Overall system compliance status

### 2. Agents (`/agents`)
- **Agent List**: Comprehensive table of all agents
- **Status Monitoring**: Active, idle, and offline agents
- **Health Scores**: Visual health indicators for each agent
- **Last Seen**: Timestamp of last agent activity
- **Actions**: View details and configure agents

### 3. Events (`/events`)
- **Event Log**: Complete event history with filtering
- **Severity Filtering**: Filter by critical, error, warning, info
- **Search**: Search events by message or source
- **Real-time Updates**: New events appear automatically
- **Event Statistics**: Counts by severity level

### 4. Compliance (`/compliance`)
- **Overall Score**: System-wide compliance percentage
- **Certifications**: SOC2, GDPR, ISO27001 status
- **Compliance Checks**: Individual check status and scores
- **Violations**: Current compliance violations
- **Pending Reviews**: Security reviews requiring attention

### 5. Settings (`/settings`)
- **General Settings**: Timezone, language, theme, refresh rate
- **Notifications**: Email, Slack, webhook configuration
- **Security Settings**: Session timeout, login attempts, API limits
- **System Settings**: Logging, backup configuration

## 🛠️ Architecture

### Frontend (React)
```
dashboard/frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom React hooks
│   ├── utils/         # Utility functions
│   └── index.css      # Tailwind CSS styles
├── public/            # Static assets
├── package.json       # Dependencies and scripts
└── tailwind.config.js # Tailwind configuration
```

### Backend (FastAPI)
```
dashboard/
├── api.py            # REST API endpoints
├── websocket.py      # WebSocket handlers
└── __init__.py       # Module initialization
```

### Key Technologies
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first styling
- **Headless UI**: Accessible components
- **Recharts**: Data visualization
- **FastAPI**: Backend API framework
- **WebSockets**: Real-time communication

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd dashboard/frontend
npm install
```

### 2. Build Dashboard

**Option A: Using the build script**
```bash
python scripts/build_dashboard.py
```

**Option B: Manual build**
```bash
cd dashboard/frontend
npm run build
```

### 3. Start the Application

```bash
python main.py
```

### 4. Access Dashboard

Visit `http://localhost:5000/dashboard` in your browser.

## 🔧 Development

### Development Mode

For development, you can run the frontend separately:

```bash
cd dashboard/frontend
npm start
```

This will start the React dev server at `http://localhost:3000` with hot reloading.

### API Endpoints

The dashboard provides the following API endpoints:

- `GET /dashboard/` - Serve dashboard HTML
- `GET /dashboard/api/status` - System status
- `GET /dashboard/api/agents` - Agent list
- `GET /dashboard/api/events` - Event list
- `GET /dashboard/api/metrics` - Combined metrics
- `GET /dashboard/api/health` - Health check

### WebSocket Events

The dashboard subscribes to these WebSocket events:

- `metrics_update` - System metrics updates
- `new_event` - New system events
- `alert` - System alerts
- `agents` - Agent status updates

## 🎨 Customization

### Themes

The dashboard supports custom theming through Tailwind CSS. Modify `dashboard/frontend/tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          // Your custom colors
        }
      }
    }
  }
}
```

### Components

All components are modular and can be customized:

- **Layout**: Modify `Sidebar.js` and `Header.js`
- **Pages**: Customize page components in `pages/`
- **Charts**: Extend chart components with Recharts
- **Styling**: Update CSS classes in `index.css`

### API Integration

To integrate with different backends:

1. Modify `useWebSocket.js` for different WebSocket protocols
2. Update API calls in page components
3. Adjust data models in `api.py`

## 📈 Performance

### Optimization Features
- **Code Splitting**: Lazy-loaded page components
- **Memoization**: React.memo for expensive components
- **Debounced Updates**: WebSocket message throttling
- **Optimized Charts**: Efficient re-rendering with Recharts
- **Static Assets**: Optimized build output

### Monitoring
- **Bundle Analysis**: `npm run build` includes bundle analysis
- **Performance Metrics**: Built-in performance monitoring
- **Error Tracking**: Comprehensive error boundaries

## 🔒 Security

### Authentication
The dashboard is ready for authentication integration:

```python
# In dashboard/api.py
from auth.rbac import get_current_user, User

@router.get("/api/status")
async def get_system_status(
    current_user: User = Depends(get_current_user)
) -> SystemStatus:
    # Protected endpoint
```

### Authorization
Role-based access control is supported:

```python
# Check user permissions
if not current_user.has_permission("dashboard:read"):
    raise HTTPException(status_code=403, detail="Access denied")
```

## 🚀 Deployment

### Production Build

1. **Build the frontend:**
   ```bash
   python scripts/build_dashboard.py
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

3. **Start the application:**
   ```bash
   python main.py
   ```

### Docker Deployment

The dashboard is included in the Docker setup:

```yaml
# docker-compose.yml
services:
  watchtower:
    build: .
    ports:
      - "5000:5000"
    environment:
      - WATCHTOWER_ENV=production
```

### Kubernetes Deployment

Use the provided Kubernetes manifests:

```bash
kubectl apply -f devops/k8s.yaml
kubectl apply -f devops/secrets.yaml
```

## 🐛 Troubleshooting

### Common Issues

**Dashboard not loading:**
- Check if frontend is built: `ls dashboard/frontend/build/`
- Verify static files are mounted in FastAPI
- Check browser console for errors

**WebSocket connection failed:**
- Ensure WebSocket server is running
- Check firewall settings
- Verify WebSocket URL in browser

**Build errors:**
- Update Node.js to version 16+
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

### Debug Mode

Enable debug logging:

```python
# In config/settings.py
WATCHTOWER_DEBUG = True
WATCHTOWER_LOG_LEVEL = "DEBUG"
```

## 📚 API Documentation

### REST API

The dashboard API is documented with OpenAPI/Swagger at:
`http://localhost:5000/docs`

### WebSocket API

WebSocket messages follow this format:

```json
{
  "action": "subscribe",
  "channels": ["metrics", "events", "agents"]
}
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
3. **Make changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Code Style

- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort
- **Type Hints**: Use type hints in Python
- **Documentation**: Update README files

## 📄 License

This dashboard is part of the Watchtower project and follows the same license terms.

---

**Need Help?** Check the main project documentation or open an issue on GitHub. 