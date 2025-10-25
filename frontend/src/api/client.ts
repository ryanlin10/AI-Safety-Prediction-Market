import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const apiClient = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const api = {
  // Ideas
  getIdeas: (params?: { query?: string; limit?: number; offset?: number }) =>
    apiClient.get('/ideas', { params }),
  
  getIdea: (id: number) =>
    apiClient.get(`/ideas/${id}`),
  
  // Markets
  getMarkets: (params?: { status?: string; limit?: number; offset?: number }) =>
    apiClient.get('/markets', { params }),
  
  getMarket: (id: number) =>
    apiClient.get(`/markets/${id}`),
  
  createMarket: (data: any) =>
    apiClient.post('/markets', data),
  
  // Bets
  placeBet: (marketId: number, data: any) =>
    apiClient.post(`/markets/${marketId}/bets`, data),
  
  // Agents
  getAgents: () =>
    apiClient.get('/agents'),
  
  placeInitialBet: (agentId: number, marketId: number) =>
    apiClient.post(`/agents/${agentId}/place_initial_bet`, { market_id: marketId }),
  
  // Experiments
  runExperiment: (marketId: number, agentId: number) =>
    apiClient.post(`/markets/${marketId}/run_experiment`, { agent_id: agentId }),
  
  getExperiment: (id: number) =>
    apiClient.get(`/experiments/${id}`),
  
  getMarketExperiments: (marketId: number) =>
    apiClient.get(`/markets/${marketId}/experiments`),
};

