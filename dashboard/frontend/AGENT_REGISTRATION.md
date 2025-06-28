# Agent Registration Dashboard

This document describes the agent registration functionality in the Watchtower dashboard frontend.

## Features

### Agent Registration Form
- **UUID Generation**: Automatic UUID generation with a button to generate new UUIDs
- **Required Fields**: UUID, Name, and Agent Type are required
- **Optional Fields**: Owner, Description, Status, Score, and Crypto ID
- **Validation**: Form validation with error handling
- **Success Feedback**: Success messages and form reset after registration

### Agent Management
- **Real-time Data**: Fetches agents from the API on page load
- **Live Updates**: New agents appear immediately after registration
- **Status Indicators**: Visual status badges (online, degraded, offline)
- **Agent Types**: Support for monitoring, security, compliance, backup, analytics, and custom types
- **Empty State**: Helpful message when no agents are registered

## API Integration

The frontend integrates with the following API endpoints:

- `GET /api/agents/` - Fetch all agents
- `POST /api/agents/` - Register a new agent
- `GET /api/agents/{uuid}` - Get specific agent details
- `PUT /api/agents/{uuid}` - Update agent information
- `DELETE /api/agents/{uuid}` - Delete an agent

## Components

### AgentRegistration
Located in `src/components/AgentRegistration.js`

**Props:**
- `onAgentRegistered`: Callback function called when an agent is successfully registered

**Features:**
- Form validation
- UUID generation
- Error handling
- Success feedback
- Responsive design

### Agents Page
Located in `src/pages/Agents.js`

**Features:**
- Agent list display
- Registration form toggle
- Loading states
- Error handling
- Statistics display

## Usage

1. Navigate to the Agents page in the dashboard
2. Click "Register Agent" to show the registration form
3. Fill in the required fields (UUID, Name, Agent Type)
4. Optionally fill in additional fields
5. Click "Register Agent" to submit
6. The new agent will appear in the list immediately

## Styling

The components use Tailwind CSS with custom classes defined in:
- `src/index.css` - Global styles and utility classes
- `src/components/AgentRegistration.css` - Component-specific styles

## Dependencies

- React 18.2.0
- @heroicons/react 2.0.18
- Tailwind CSS 3.3.2
- React Router DOM 6.3.0

## Development

To run the frontend in development mode:

```bash
cd dashboard/frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to `http://localhost:5000`. 