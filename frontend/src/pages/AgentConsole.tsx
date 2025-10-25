import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Agent, Market } from '../types';
import './AgentConsole.css';

const AgentConsole: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedMarketId, setSelectedMarketId] = useState<number>(0);

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents(),
  });

  const { data: marketsData } = useQuery({
    queryKey: ['markets'],
    queryFn: () => api.getMarkets({ status: 'active' }),
  });

  const placeInitialBetMutation = useMutation({
    mutationFn: ({ agentId, marketId }: { agentId: number; marketId: number }) =>
      api.placeInitialBet(agentId, marketId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['market'] });
      alert('Agent bet placed successfully!');
    },
  });

  const agents: Agent[] = agentsData?.data?.agents || [];
  const markets: Market[] = marketsData?.data?.markets || [];
  const bettorAgents = agents.filter((a) => a.type === 'bettor');
  const researcherAgents = agents.filter((a) => a.type === 'researcher');

  if (agentsLoading) {
    return <div className="loading">Loading agents...</div>;
  }

  return (
    <div className="agent-console">
      <h1>Agent Console</h1>
      <p className="subtitle">Manage and monitor AI agents</p>

      <div className="agents-section">
        <h2>Bettor Agents</h2>
        <div className="agents-grid">
          {bettorAgents.map((agent) => (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <h3>{agent.name}</h3>
                <span className={`status-indicator ${agent.is_active ? 'active' : 'inactive'}`}>
                  {agent.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="agent-type">🤖 {agent.type}</div>
              
              <div className="agent-actions">
                <select
                  onChange={(e) => setSelectedMarketId(parseInt(e.target.value))}
                  className="market-select"
                >
                  <option value="0">Select a market...</option>
                  {markets.map((market) => (
                    <option key={market.id} value={market.id}>
                      Market #{market.id}: {market.question_text.substring(0, 50)}...
                    </option>
                  ))}
                </select>
                <button
                  onClick={() =>
                    selectedMarketId > 0 &&
                    placeInitialBetMutation.mutate({
                      agentId: agent.id,
                      marketId: selectedMarketId,
                    })
                  }
                  disabled={selectedMarketId === 0 || placeInitialBetMutation.isPending}
                  className="place-bet-btn"
                >
                  Place Initial Bet
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="agents-section">
        <h2>Researcher Agents</h2>
        <div className="agents-grid">
          {researcherAgents.map((agent) => (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <h3>{agent.name}</h3>
                <span className={`status-indicator ${agent.is_active ? 'active' : 'inactive'}`}>
                  {agent.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="agent-type">🔬 {agent.type}</div>
              <div className="agent-meta">
                {agent.meta && (
                  <pre>{JSON.stringify(agent.meta, null, 2)}</pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {agents.length === 0 && (
        <div className="empty-state">
          <p>No agents configured. Run the seed script to create default agents.</p>
        </div>
      )}
    </div>
  );
};

export default AgentConsole;

