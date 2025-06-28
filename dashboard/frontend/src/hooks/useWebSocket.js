import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import toast from 'react-hot-toast';

const WebSocketContext = createContext();

export function WebSocketProvider({ children }) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);
  const [agents, setAgents] = useState([]);
  const [connectionError, setConnectionError] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;
  const isInitializedRef = useRef(false);

  // Get auth token from localStorage
  useEffect(() => {
    const token = localStorage.getItem('watchtower_auth_token');
    if (token) {
      setAuthToken(token);
    }
  }, []);

  const connect = useCallback(() => {
    if (isConnecting || isConnected) return;
    
    if (connectionAttempts >= maxReconnectAttempts) {
      console.log('Max reconnection attempts reached, stopping WebSocket connection');
      setConnectionError('Maximum reconnection attempts reached. Real-time updates are disabled.');
      toast.error('Real-time connection unavailable - using polling mode');
      return;
    }
    
    setIsConnecting(true);
    setConnectionError(null);
    
    try {
      // Build WebSocket URL with authentication token
      let wsUrl = 'ws://10.42.69.208:5000/ws';
      if (authToken) {
        wsUrl += `?token=${encodeURIComponent(authToken)}`;
      }
      
      console.log('Attempting WebSocket connection to:', wsUrl);
      wsRef.current = new WebSocket(wsUrl);
      
      const connectionTimeout = setTimeout(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
          console.log('WebSocket connection timeout');
          wsRef.current.close();
          setConnectionError('Connection timeout. Real-time updates are disabled.');
        }
      }, 10000);
      
      wsRef.current.onopen = () => {
        clearTimeout(connectionTimeout);
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionAttempts(0);
        setConnectionError(null);
        console.log('WebSocket connected successfully');
        
        // Subscribe to channels
        wsRef.current.send(JSON.stringify({
          action: 'subscribe',
          channels: ['metrics', 'events', 'agents', 'alerts', 'system']
        }));
        
        // Set up heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }
        
        heartbeatIntervalRef.current = setInterval(() => {
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'ping' }));
          }
        }, 30000);
        
        toast.success('Real-time connection established');
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          switch (data.type) {
            case 'metrics_update':
              setMetrics(data.data);
              break;
            case 'new_event':
              setEvents(prev => [data.data, ...prev.slice(0, 99)]);
              if (data.data.severity === 'critical' || data.data.severity === 'error') {
                toast.error(`Critical Event: ${data.data.message}`, { duration: 6000 });
              } else if (data.data.severity === 'warning') {
                toast.warning(`Warning: ${data.data.message}`, { duration: 4000 });
              } else {
                toast.success(`Event: ${data.data.message}`, { duration: 3000 });
              }
              break;
            case 'alert':
              toast.error(`Alert: ${data.data.message}`, { duration: 6000 });
              break;
            case 'events':
              setEvents(data.data);
              break;
            case 'agents':
              setAgents(data.data);
              break;
            case 'subscription_confirmed':
              console.log('Subscribed to channels:', data.channels);
              break;
            case 'pong':
              console.log('Received pong from server');
              break;
            case 'ping':
              // Respond to server ping
              if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ action: 'pong' }));
              }
              break;
            case 'error':
              console.error('WebSocket error from server:', data.message);
              toast.error(`Server Error: ${data.message}`, { duration: 4000 });
              break;
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onclose = (event) => {
        clearTimeout(connectionTimeout);
        setIsConnected(false);
        setIsConnecting(false);
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }
        console.log('WebSocket disconnected:', event.code, event.reason);
        
        // Handle authentication errors
        if (event.code === 4001) {
          console.log('Authentication failed, clearing token');
          localStorage.removeItem('watchtower_auth_token');
          setAuthToken(null);
          setConnectionError('Authentication failed. Please log in again.');
          toast.error('Authentication failed - please log in again');
          return;
        }
        
        if (event.code !== 1000 && connectionAttempts < maxReconnectAttempts) {
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          
          const delay = reconnectDelay * Math.pow(2, connectionAttempts);
          console.log(`Scheduling reconnection attempt ${connectionAttempts + 1} in ${delay}ms`);
          reconnectTimeoutRef.current = setTimeout(() => {
            setConnectionAttempts(prev => prev + 1);
            connect();
          }, delay);
        } else if (connectionAttempts >= maxReconnectAttempts) {
          console.log('Max reconnection attempts reached, WebSocket disabled');
          setConnectionError('Real-time connection unavailable. The system will use polling mode for updates.');
          toast.error('Real-time connection unavailable - using polling mode');
        }
      };
      
      wsRef.current.onerror = (error) => {
        clearTimeout(connectionTimeout);
        console.error('WebSocket error:', error);
        setIsConnecting(false);
        setConnectionError('WebSocket connection error. Real-time updates are disabled.');
      };
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setIsConnecting(false);
      setConnectionError('Failed to create WebSocket connection. Real-time updates are disabled.');
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      const delay = reconnectDelay * Math.pow(2, connectionAttempts);
      reconnectTimeoutRef.current = setTimeout(() => {
        setConnectionAttempts(prev => prev + 1);
        connect();
      }, delay);
    }
  }, [isConnecting, isConnected, connectionAttempts, maxReconnectAttempts, reconnectDelay, authToken]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, cannot send message');
      toast.error('Real-time connection is not available');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'User initiated disconnect');
    }
  }, []);

  const updateAuthToken = useCallback((token) => {
    setAuthToken(token);
    if (token) {
      localStorage.setItem('watchtower_auth_token', token);
    } else {
      localStorage.removeItem('watchtower_auth_token');
    }
    
    // Reconnect with new token
    if (isConnected) {
      disconnect();
      setTimeout(() => {
        setConnectionAttempts(0);
        connect();
      }, 1000);
    }
  }, [isConnected, disconnect, connect]);

  useEffect(() => {
    if (!isInitializedRef.current) {
      isInitializedRef.current = true;
      connect();
    }
    
    return () => {
      disconnect();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [connect, disconnect]);

  const value = {
    isConnected,
    isConnecting,
    connectionAttempts,
    connectionError,
    metrics,
    events,
    agents,
    authToken,
    sendMessage,
    connect,
    disconnect,
    updateAuthToken
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
} 