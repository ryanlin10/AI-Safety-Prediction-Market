import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

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
  
  generateClaims: (count?: number, categories?: string[]) =>
    apiClient.post('/ideas/generate', { count, categories }),
  
  // Investigations
  getInvestigations: (params?: { status?: string; limit?: number; offset?: number }) =>
    apiClient.get('/investigations', { params }),
  
  getInvestigation: (id: number) =>
    apiClient.get(`/investigations/${id}`),
  
  createInvestigation: (ideaId: number) =>
    apiClient.post(`/ideas/${ideaId}/investigate`),
  
  // Markets
  getMarkets: (params?: { status?: string; limit?: number; offset?: number }) =>
    apiClient.get('/markets', { params }),
  
  getMarket: (id: number) =>
    apiClient.get(`/markets/${id}`),
  
  createMarket: (data: any) =>
    apiClient.post('/markets', data),
  
  generateMarket: (keyword: string) =>
    apiClient.post('/markets/generate', { keyword }),
  
  // Bets
  placeBet: (marketId: number, data: any) =>
    apiClient.post(`/markets/${marketId}/bets`, data),
  
  getMarketPrices: (marketId: number) =>
    apiClient.get(`/markets/${marketId}/prices`),
  
  buyShares: (marketId: number, outcome: string, amount: number) =>
    apiClient.post(`/markets/${marketId}/buy`, { outcome, amount }),
  
  getPriceHistory: (marketId: number) =>
    apiClient.get(`/markets/${marketId}/price-history`),
  
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
  
  // Workspaces
  createWorkspace: (data: { investigation_id?: number; agent_id?: number; name: string; description?: string; files?: any; generate_ai_code?: boolean }) =>
    apiClient.post('/workspaces', data),
  
  getWorkspace: (workspaceId: number) =>
    apiClient.get(`/workspaces/${workspaceId}`),
  
  getFiles: (workspaceId: number) =>
    apiClient.get(`/workspaces/${workspaceId}/files`),
  
  getFile: (workspaceId: number, filePath: string) =>
    apiClient.get(`/workspaces/${workspaceId}/file/${filePath}`),
  
  saveFile: (workspaceId: number, filePath: string, content: string) =>
    apiClient.post(`/workspaces/${workspaceId}/file/${filePath}`, { content }),
  
  deleteFile: (workspaceId: number, filePath: string) =>
    apiClient.delete(`/workspaces/${workspaceId}/file/${filePath}`),
  
  getWorkspaceRuns: (workspaceId: number) =>
    apiClient.get(`/workspaces/${workspaceId}/runs`),
  
  // Runs
  runWorkspace: (workspaceId: number) =>
    apiClient.post(`/workspaces/${workspaceId}/run`),
  
  getRunStatus: (runId: number) =>
    apiClient.get(`/runs/${runId}`),
};

