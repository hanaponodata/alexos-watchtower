# Watchtower Dashboard Frontend

A modern React-based dashboard for the Watchtower enterprise platform.

## Features

- **Real-time Updates**: WebSocket-powered live data streaming
- **Modern UI**: Built with Tailwind CSS and Headless UI
- **Dark Mode**: Full dark/light theme support
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Real-time metrics visualization with Recharts
- **Enterprise Features**: Agent management, event monitoring, compliance tracking

## Pages

- **Dashboard**: System overview with real-time metrics and charts
- **Agents**: Monitor and manage connected agents
- **Events**: View and filter system events
- **Compliance**: Security and compliance monitoring
- **Settings**: Configure dashboard preferences

## Development

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
cd dashboard/frontend
npm install
```

### Development Server

```bash
npm start
```

The dashboard will be available at `http://localhost:3000` and will proxy API requests to the FastAPI backend at `http://localhost:5000`.

### Building for Production

```bash
npm run build
```

This creates a `build/` directory with optimized production files that will be served by the FastAPI backend.

### Testing

```bash
npm test
```

## Architecture

- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Headless UI**: Accessible UI components
- **Recharts**: Chart library for data visualization
- **Axios**: HTTP client for API requests
- **React Hot Toast**: Toast notifications
- **Framer Motion**: Animation library

## WebSocket Integration

The dashboard connects to the backend WebSocket endpoint for real-time updates:

- System metrics (CPU, memory, disk usage)
- Agent status changes
- New events and alerts
- Compliance status updates

## Environment Variables

The dashboard uses the following environment variables:

- `REACT_APP_API_URL`: Backend API URL (defaults to proxy)
- `REACT_APP_WS_URL`: WebSocket URL (auto-detected from current host)

## Deployment

1. Build the frontend: `npm run build`
2. The FastAPI backend will serve the built files from `/dashboard/`
3. Ensure the backend is configured to serve static files

## Customization

### Themes

The dashboard supports custom theming through Tailwind CSS. Modify `tailwind.config.js` to customize colors, fonts, and other design tokens.

### Components

All components are modular and can be easily customized or extended. See the `src/components/` directory for reusable UI components.

### API Integration

The dashboard uses a custom hook (`useWebSocket`) for real-time data. Modify this hook to integrate with different backend APIs or add new data sources. 