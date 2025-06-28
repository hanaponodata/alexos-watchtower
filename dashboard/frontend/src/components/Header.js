import React, { useState, useEffect, useRef } from 'react';
import { Bars3Icon, UserIcon, CogIcon, ArrowRightOnRectangleIcon, BellIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../hooks/useWebSocket';
import apiService from '../utils/api';
import toast from 'react-hot-toast';

export default function Header({ onMenuClick }) {
  const { isConnected, isConnecting, connectionAttempts } = useWebSocket();
  const [showAdminMenu, setShowAdminMenu] = useState(false);
  const [systemStatus, setSystemStatus] = useState('unknown');
  const [notifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const adminMenuRef = useRef(null);
  const notificationRef = useRef(null);

  // Check system status periodically
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const health = await apiService.healthCheck();
        setSystemStatus(health.status || 'unknown');
      } catch (error) {
        setSystemStatus('error');
      }
    };

    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (adminMenuRef.current && !adminMenuRef.current.contains(event.target)) {
        setShowAdminMenu(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAdminClick = () => {
    setShowAdminMenu(!showAdminMenu);
  };

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
  };

  const handleAdminAction = (action) => {
    setShowAdminMenu(false);
    
    switch (action) {
      case 'profile':
        toast.info('User profile management coming soon!', { duration: 3000 });
        break;
      case 'settings':
        toast.info('System settings panel opening...', { duration: 3000 });
        break;
      case 'logout':
        if (window.confirm('Are you sure you want to logout?')) {
          toast.success('Logging out...', { duration: 2000 });
          // Add actual logout logic here
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
        break;
      default:
        break;
    }
  };

  const getConnectionStatusColor = () => {
    if (isConnected) return 'bg-success-500';
    if (isConnecting) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  const getConnectionStatusText = () => {
    if (isConnected) return 'Connected';
    if (isConnecting) return 'Connecting...';
    if (connectionAttempts > 0) return `Reconnecting (${connectionAttempts})`;
    return 'Disconnected';
  };

  const getSystemStatusColor = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'bg-success-500';
      case 'warning':
        return 'bg-warning-500';
      case 'error':
        return 'bg-danger-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        {/* Left side */}
        <div className="flex items-center">
          <button
            type="button"
            className="lg:hidden -m-2.5 p-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            onClick={onMenuClick}
          >
            <span className="sr-only">Open sidebar</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* System Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getSystemStatusColor()}`} />
            <span className="text-sm text-gray-600 dark:text-gray-300 hidden sm:block">
              System: {systemStatus}
            </span>
          </div>

          {/* Connection status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getConnectionStatusColor()}`} />
            <span className="text-sm text-gray-600 dark:text-gray-300 hidden sm:block">
              {getConnectionStatusText()}
            </span>
          </div>

          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <button 
              onClick={handleNotificationClick}
              className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors relative"
              title="Notifications"
            >
              <span className="sr-only">View notifications</span>
              <BellIcon className="h-6 w-6" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                  {notifications.length > 9 ? '9+' : notifications.length}
                </span>
              )}
            </button>

            {/* Notifications dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Notifications</h3>
                </div>
                {notifications.length === 0 ? (
                  <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    <BellIcon className="mx-auto h-8 w-8 mb-2" />
                    <p>No new notifications</p>
                  </div>
                ) : (
                  notifications.map((notification, index) => (
                    <div key={index} className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700">
                      <p className="text-sm text-gray-900 dark:text-white">{notification.message}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {new Date(notification.timestamp).toLocaleString()}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* User/Admin menu */}
          <div className="relative" ref={adminMenuRef}>
            <button 
              onClick={handleAdminClick}
              className="flex items-center space-x-2 text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                <UserIcon className="h-5 w-5 text-white" />
              </div>
              <span className="hidden md:block text-gray-700 dark:text-gray-300">Admin</span>
            </button>

            {/* Admin dropdown menu */}
            {showAdminMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => handleAdminAction('profile')}
                  className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <UserIcon className="h-4 w-4 mr-3" />
                  Profile
                </button>
                <button
                  onClick={() => handleAdminAction('settings')}
                  className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <CogIcon className="h-4 w-4 mr-3" />
                  System Settings
                </button>
                <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                <button
                  onClick={() => handleAdminAction('logout')}
                  className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
} 