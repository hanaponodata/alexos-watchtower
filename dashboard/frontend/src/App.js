import React, { useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Events from './pages/Events';
import Compliance from './pages/Compliance';
import Settings from './pages/Settings';
import ErrorBoundary from './components/ErrorBoundary';
import { ThemeProvider } from './hooks/useTheme';
import { WebSocketProvider } from './hooks/useWebSocket';

console.log('App.js: useLocation:', typeof useLocation);

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <WebSocketProvider>
          <div className="h-screen flex overflow-hidden bg-gray-50 dark:bg-gray-900">
            <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
            <div className="flex-1 overflow-auto focus:outline-none">
              <Header onMenuClick={() => setSidebarOpen(true)} />
              <main className="flex-1 relative z-0 overflow-y-auto py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/agents" element={<Agents />} />
                    <Route path="/events" element={<Events />} />
                    <Route path="/compliance" element={<Compliance />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </div>
              </main>
            </div>
          </div>
        </WebSocketProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App; 