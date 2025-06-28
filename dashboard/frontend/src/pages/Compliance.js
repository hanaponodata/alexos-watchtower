import React from 'react';
import { ShieldCheckIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export default function Compliance() {
  // Mock compliance data
  const complianceData = {
    overall_score: 95.5,
    last_audit: new Date().toISOString(),
    violations: 2,
    pending_reviews: 5,
    certifications: ['SOC2', 'GDPR', 'ISO27001'],
    checks: [
      { name: 'Access Control', status: 'pass', score: 98 },
      { name: 'Data Encryption', status: 'pass', score: 95 },
      { name: 'Audit Logging', status: 'pass', score: 92 },
      { name: 'Network Security', status: 'warning', score: 85 },
      { name: 'Backup Procedures', status: 'fail', score: 70 },
    ]
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass':
        return <CheckCircleIcon className="h-5 w-5 text-success-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning-500" />;
      case 'fail':
        return <XCircleIcon className="h-5 w-5 text-danger-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pass':
        return 'status-badge-success';
      case 'warning':
        return 'status-badge-warning';
      case 'fail':
        return 'status-badge-danger';
      default:
        return 'status-badge-info';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Security and compliance monitoring
        </p>
      </div>

      {/* Overall score */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Overall Compliance Score</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Last updated: {new Date(complianceData.last_audit).toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {complianceData.overall_score}%
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {complianceData.overall_score >= 90 ? 'Excellent' : 
                 complianceData.overall_score >= 80 ? 'Good' : 
                 complianceData.overall_score >= 70 ? 'Fair' : 'Poor'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="metric-card">
          <div className="flex items-center">
            <ShieldCheckIcon className="h-8 w-8 text-success-500" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Passed Checks</dt>
                <dd className="metric-value">
                  {complianceData.checks.filter(c => c.status === 'pass').length}
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-warning-500" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Warnings</dt>
                <dd className="metric-value">
                  {complianceData.checks.filter(c => c.status === 'warning').length}
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="flex items-center">
            <XCircleIcon className="h-8 w-8 text-danger-500" />
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="metric-label">Violations</dt>
                <dd className="metric-value">{complianceData.violations}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Certifications */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Certifications</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {complianceData.certifications.map((cert, index) => (
              <div key={index} className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <CheckCircleIcon className="h-6 w-6 text-success-500 mr-3" />
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">{cert}</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Certified</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance checks */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Compliance Checks</h3>
        </div>
        <div className="card-body">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Check
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {complianceData.checks.map((check, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {check.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(check.status)}
                        <span className={`ml-2 status-badge ${getStatusColor(check.status)}`}>
                          {check.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full ${
                              check.score >= 90 ? 'bg-success-500' :
                              check.score >= 80 ? 'bg-warning-500' : 'bg-danger-500'
                            }`}
                            style={{ width: `${check.score}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-900 dark:text-white">
                          {check.score}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-primary-600 hover:text-primary-900 dark:hover:text-primary-400 mr-3">
                        View Details
                      </button>
                      {check.status !== 'pass' && (
                        <button className="text-warning-600 hover:text-warning-900 dark:hover:text-warning-400">
                          Remediate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pending reviews */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Pending Reviews</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {Array.from({ length: complianceData.pending_reviews }, (_, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Security Review #{i + 1}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Due: {new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000).toLocaleDateString()}
                  </p>
                </div>
                <button className="btn-primary">
                  Review
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 