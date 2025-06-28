import React, { useState, useEffect } from 'react';
import { UserGroupIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon, PlusIcon } from '@heroicons/react/24/outline';
import AgentRegistration from '../components/AgentRegistration';
import apiService from '../utils/api';

export default function Agents() {
  const [localAgents, setLocalAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showRegistration, setShowRegistration] = useState(false);

  // Fetch agents from API
  const fetchAgents = async () => {
    try {
      const data = await apiService.getAgents();
      setLocalAgents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  // Handle new agent registration
  const handleAgentRegistered = (newAgent) => {
    setLocalAgents(prev => [...prev, newAgent]);
    setShowRegistration(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-success-500" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning-500" />;
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-danger-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'status-badge-success';
      case 'degraded':
        return 'status-badge-warning';
      case 'offline':
        return 'status-badge-danger';
      default:
        return 'status-badge-info';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and manage connected agents
          </p>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <span className="ml-2 text-gray-600">Loading agents...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and manage connected agents
          </p>
        </div>
        <button
          onClick={() => setShowRegistration(!showRegistration)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          {showRegistration ? 'Hide Registration' : 'Register Agent'}
        </button>
      </div>

      {/* Registration Form */}
      {showRegistration && (
        <div className="card">
          <div className="card-body">
            <AgentRegistration onAgentRegistered={handleAgentRegistered} />
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="metric-card">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-gray-400" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Total Agents</dt>
                <dd className="metric-value">{localAgents.length}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-success-500" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Online</dt>
                <dd className="metric-value">{localAgents.filter(a => a.status === 'online').length}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-warning-500" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Degraded</dt>
                <dd className="metric-value">{localAgents.filter(a => a.status === 'degraded').length}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Agents table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Agent List</h3>
        </div>
        <div className="card-body">
          {localAgents.length === 0 ? (
            <div className="text-center py-8">
              <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No agents found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Get started by registering your first agent.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowRegistration(true)}
                  className="btn-primary flex items-center gap-2 mx-auto"
                >
                  <PlusIcon className="h-5 w-5" />
                  Register Agent
                </button>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Agent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Owner
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {localAgents.map((agent) => (
                    <tr key={agent.uuid} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                              <span className="text-primary-600 dark:text-primary-400 font-medium">
                                {agent.name.charAt(0)}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {agent.name}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {agent.uuid}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                          {agent.agent_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(agent.status)}
                          <span className={`ml-2 status-badge ${getStatusColor(agent.status)}`}>
                            {agent.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                            <div 
                              className="bg-success-500 h-2 rounded-full" 
                              style={{ width: `${agent.score}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-900 dark:text-white">
                            {agent.score}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {agent.owner || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-primary-600 hover:text-primary-900 dark:hover:text-primary-400 mr-3">
                          View
                        </button>
                        <button className="text-gray-600 hover:text-gray-900 dark:hover:text-gray-400">
                          Configure
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 