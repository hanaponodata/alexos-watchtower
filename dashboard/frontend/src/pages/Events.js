import React, { useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { BellIcon } from '@heroicons/react/24/outline';

export default function Events() {
  const { events } = useWebSocket();
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-danger-600 bg-danger-100 dark:bg-danger-900 dark:text-danger-200';
      case 'error':
        return 'text-danger-600 bg-danger-100 dark:bg-danger-900 dark:text-danger-200';
      case 'warning':
        return 'text-warning-600 bg-warning-100 dark:bg-warning-900 dark:text-warning-200';
      case 'info':
        return 'text-primary-600 bg-primary-100 dark:bg-primary-900 dark:text-primary-200';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'system':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200';
      case 'security':
        return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200';
      case 'network':
        return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200';
      case 'agent':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const filteredEvents = events.filter(event => {
    const matchesFilter = filter === 'all' || event.severity === filter;
    const matchesSearch = event.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.source.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const severityCounts = {
    critical: events.filter(e => e.severity === 'critical').length,
    error: events.filter(e => e.severity === 'error').length,
    warning: events.filter(e => e.severity === 'warning').length,
    info: events.filter(e => e.severity === 'info').length,
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Events</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Monitor system events and alerts
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="metric-card">
          <div className="flex items-center">
            <BellIcon className="h-8 w-8 text-gray-400" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Total Events</dt>
                <dd className="metric-value">{events.length}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-danger-100 dark:bg-danger-900 rounded-full flex items-center justify-center">
              <span className="text-danger-600 dark:text-danger-400 text-sm font-medium">!</span>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Critical</dt>
                <dd className="metric-value">{severityCounts.critical}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-warning-100 dark:bg-warning-900 rounded-full flex items-center justify-center">
              <span className="text-warning-600 dark:text-warning-400 text-sm font-medium">!</span>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Warnings</dt>
                <dd className="metric-value">{severityCounts.warning}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <span className="text-primary-600 dark:text-primary-400 text-sm font-medium">i</span>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Info</dt>
                <dd className="metric-value">{severityCounts.info}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Search Events
              </label>
              <input
                type="text"
                id="search"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                placeholder="Search by message or source..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="filter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Severity Filter
              </label>
              <select
                id="filter"
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Events list */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Event Log</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {filteredEvents.length === 0 ? (
              <div className="text-center py-8">
                <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No events found</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            ) : (
              filteredEvents.map((event, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                    event.severity === 'critical' || event.severity === 'error' ? 'bg-danger-500' :
                    event.severity === 'warning' ? 'bg-warning-500' : 'bg-primary-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {event.message}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(event.type)}`}>
                          {event.type}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(event.severity)}`}>
                          {event.severity}
                        </span>
                      </div>
                    </div>
                    <div className="mt-1 flex items-center justify-between">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Source: {event.source}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 