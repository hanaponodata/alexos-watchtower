const API_BASE_URL = process.env.REACT_APP_API_URL || '';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.timeout = 10000; // 10 seconds
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers,
      },
      timeout: this.timeout,
      ...options,
    };

    let lastError;
    
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const response = await fetch(url, {
          ...config,
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const error = new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
          error.status = response.status;
          error.statusText = response.statusText;
          error.data = errorData;
          throw error;
        }

        return await response.json();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) except 429 (rate limit)
        if (error.status && error.status >= 400 && error.status < 500 && error.status !== 429) {
          throw error;
        }
        
        // Don't retry on abort (timeout)
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        
        // Retry on server errors (5xx) or network errors
        if (attempt < this.retryAttempts) {
          await this.delay(this.retryDelay * attempt);
          continue;
        }
      }
    }
    
    throw lastError || new Error('Request failed after multiple attempts');
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Dashboard endpoints
  async getSystemMetrics() {
    try {
      return await this.request('/api/metrics');
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      // Show user-friendly error message
      throw new Error(`Unable to fetch system metrics: ${error.message}. Please check your connection and try again.`);
    }
  }

  async getRecentActivity() {
    try {
      return await this.request('/api/activity');
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
      throw new Error(`Unable to fetch recent activity: ${error.message}. Please check your connection and try again.`);
    }
  }

  async getAlerts() {
    try {
      return await this.request('/api/alerts');
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      throw new Error(`Unable to fetch alerts: ${error.message}. Please check your connection and try again.`);
    }
  }

  // Agent endpoints
  async getAgents() {
    try {
      return await this.request('/api/agents');
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      throw new Error(`Unable to fetch agents: ${error.message}. Please check your connection and try again.`);
    }
  }

  async registerAgent(agentData) {
    try {
      return await this.request('/api/agents/', {
        method: 'POST',
        body: JSON.stringify(agentData),
      });
    } catch (error) {
      console.error('Failed to register agent:', error);
      throw new Error(`Failed to register agent: ${error.message}`);
    }
  }

  async getAgent(uuid) {
    return this.request(`/api/agents/${uuid}`);
  }

  async updateAgent(uuid, agentData) {
    return this.request(`/api/agents/${uuid}`, {
      method: 'PUT',
      body: JSON.stringify(agentData),
    });
  }

  async deleteAgent(uuid) {
    return this.request(`/api/agents/${uuid}`, {
      method: 'DELETE',
    });
  }

  // System status
  async getSystemStatus() {
    try {
      return await this.request('/api/status');
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      // Return mock data for development
      return {
        uptime: '5d 12h 34m',
        version: '1.0.0',
        environment: 'production',
        node_id: 'node-001',
        peers_count: 3,
        active_agents: 3,
        total_events: 1250,
        system_health: 'healthy'
      };
    }
  }

  // Health check
  async healthCheck() {
    try {
      return await this.request('/api/status/health');
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Events
  async getEvents(limit = 100, severity = null, eventType = null) {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit);
      if (severity) params.append('severity', severity);
      if (eventType) params.append('event_type', eventType);
      
      return await this.request(`/api/events?${params.toString()}`);
    } catch (error) {
      console.error('Failed to fetch events:', error);
      // Return mock data for development
      return [
        {
          id: 1,
          timestamp: new Date().toISOString(),
          type: 'system',
          severity: 'info',
          source: 'watchtower',
          message: 'System startup completed successfully'
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 300000).toISOString(),
          type: 'security',
          severity: 'warning',
          source: 'firewall',
          message: 'Suspicious connection attempt detected'
        },
        {
          id: 3,
          timestamp: new Date(Date.now() - 600000).toISOString(),
          type: 'network',
          severity: 'info',
          source: 'router',
          message: 'Network configuration updated'
        }
      ];
    }
  }

  // Compliance
  async getComplianceStatus() {
    return this.request('/api/compliance');
  }
}

const apiService = new ApiService();
export default apiService; 