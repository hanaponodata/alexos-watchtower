import React, { useState } from 'react';
import apiService from '../utils/api';
import './AgentRegistration.css';

const AgentRegistration = ({ onAgentRegistered }) => {
  const [formData, setFormData] = useState({
    uuid: '',
    name: '',
    agent_type: '',
    owner: '',
    description: '',
    status: 'offline',
    score: 0,
    crypto_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateUUID = () => {
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : ((r & 0x3) | 0x8);
      return v.toString(16);
    });
    setFormData(prev => ({ ...prev, uuid }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate form
    if (!formData.name || !formData.description || !formData.agent_type || 
        (formData.agent_type.length === 0)) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      const newAgent = await apiService.registerAgent(formData);
      setSuccess('Agent registered successfully!');
      setFormData({
        uuid: '',
        name: '',
        agent_type: '',
        owner: '',
        description: '',
        status: 'offline',
        score: 0,
        crypto_id: ''
      });
      
      if (onAgentRegistered) {
        onAgentRegistered(newAgent);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-registration">
      <h2>Register New Agent</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <form onSubmit={handleSubmit} className="registration-form">
        <div className="form-group">
          <label htmlFor="uuid">Agent UUID *</label>
          <div className="uuid-input">
            <input
              type="text"
              id="uuid"
              name="uuid"
              value={formData.uuid}
              onChange={handleInputChange}
              required
              placeholder="Enter agent UUID"
            />
            <button 
              type="button" 
              onClick={generateUUID}
              className="generate-uuid-btn"
            >
              Generate UUID
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="name">Agent Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            placeholder="Enter agent name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="agent_type">Agent Type *</label>
          <select
            id="agent_type"
            name="agent_type"
            value={formData.agent_type}
            onChange={handleInputChange}
            required
          >
            <option value="">Select agent type</option>
            <option value="monitoring">Monitoring</option>
            <option value="security">Security</option>
            <option value="compliance">Compliance</option>
            <option value="backup">Backup</option>
            <option value="analytics">Analytics</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="owner">Owner</label>
          <input
            type="text"
            id="owner"
            name="owner"
            value={formData.owner}
            onChange={handleInputChange}
            placeholder="Enter owner name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Enter agent description"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleInputChange}
          >
            <option value="offline">Offline</option>
            <option value="online">Online</option>
            <option value="degraded">Degraded</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="score">Score</label>
          <input
            type="number"
            id="score"
            name="score"
            value={formData.score}
            onChange={handleInputChange}
            min="0"
            max="100"
          />
        </div>

        <div className="form-group">
          <label htmlFor="crypto_id">Crypto ID</label>
          <input
            type="text"
            id="crypto_id"
            name="crypto_id"
            value={formData.crypto_id}
            onChange={handleInputChange}
            placeholder="Enter crypto ID (optional)"
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="submit-btn"
        >
          {loading ? 'Registering...' : 'Register Agent'}
        </button>
      </form>
    </div>
  );
};

export default AgentRegistration; 