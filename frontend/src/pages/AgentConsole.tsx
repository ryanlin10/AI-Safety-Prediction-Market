import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Agent, Market } from '../types';
import './AgentConsole.css';

interface Investigation {
  id: number;
  idea_id: number;
  agent_id: number;
  formalized_claim: string;
  test_criteria: string[];
  status: string;
  reasoning_steps: any[];
  evidence: any[];
  conclusion: string;
  confidence: number;
  summary: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  idea: {
    id: number;
    title: string;
    extracted_claim: string;
  };
}

const AgentConsole: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedMarketId, setSelectedMarketId] = useState<number>(0);
  const [expandedInvestigation, setExpandedInvestigation] = useState<number | null>(null);

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents(),
  });

  const { data: marketsData } = useQuery({
    queryKey: ['markets'],
    queryFn: () => api.getMarkets({ status: 'active' }),
  });

  const { data: investigationsData, isLoading: investigationsLoading } = useQuery({
    queryKey: ['investigations'],
    queryFn: () => api.getInvestigations({ limit: 50 }),
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
  const investigations: Investigation[] = investigationsData?.data?.investigations || [];
  const researcherAgents = agents.filter((a) => a.agent_type === 'researcher');

  const getConclusionColor = (conclusion: string) => {
    switch (conclusion) {
      case 'true':
      case 'likely_true':
        return '#4CAF50';
      case 'false':
        return '#f44336';
      case 'inconclusive':
        return '#FF9800';
      default:
        return '#666';
    }
  };

  const getConclusionLabel = (conclusion: string) => {
    switch (conclusion) {
      case 'true':
        return '✅ TRUE';
      case 'likely_true':
        return '✓ LIKELY TRUE';
      case 'false':
        return '❌ FALSE';
      case 'inconclusive':
        return '❓ INCONCLUSIVE';
      default:
        return conclusion;
    }
  };

  if (agentsLoading || investigationsLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="agent-console">
      <h1>Agent Console</h1>
      <p className="subtitle">Manage and monitor AI agents</p>

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
              <div className="agent-type">🔬 {agent.agent_type}</div>
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

      <div className="investigations-section">
        <h2>🔬 Automated Investigations</h2>
        <p className="section-description">
          AI agents automatically investigate research claims, analyzing evidence and determining truth values.
        </p>

        {investigations.length === 0 ? (
          <div className="empty-state">
            <p>No investigations yet. Click "Automated Test" on any idea in the Ideas Explorer to start an investigation.</p>
          </div>
        ) : (
          <div className="investigations-list">
            {investigations.map((inv) => (
              <div key={inv.id} className="investigation-card">
                <div className="investigation-header">
                  <div>
                    <h3 className="investigation-title">{inv.idea?.title || 'Investigation'}</h3>
                    <p className="investigation-claim">{inv.idea?.extracted_claim}</p>
                  </div>
                  {inv.status === 'completed' && inv.conclusion ? (
                    <div className="investigation-conclusion" style={{ borderColor: getConclusionColor(inv.conclusion) }}>
                      <div className="conclusion-label" style={{ color: getConclusionColor(inv.conclusion) }}>
                        {getConclusionLabel(inv.conclusion)}
                      </div>
                      <div className="confidence-score">
                        Confidence: {inv.confidence ? (inv.confidence * 100).toFixed(0) : 0}%
                      </div>
                    </div>
                  ) : (
                    <div className="investigation-conclusion" style={{ borderColor: '#999' }}>
                      <div className="conclusion-label" style={{ color: '#999' }}>
                        {inv.status === 'investigating' ? '⚙️ IN PROGRESS' : 
                         inv.status === 'failed' ? '❌ FAILED' : '⏳ PENDING'}
                      </div>
                    </div>
                  )}
                </div>

                {inv.summary && (
                  <div className="investigation-summary">
                    <strong>Summary:</strong>
                    <p>{inv.summary}</p>
                  </div>
                )}

                <div className="investigation-meta">
                  <span className={`status-badge status-${inv.status}`}>{inv.status}</span>
                  <span className="investigation-date">
                    {inv.completed_at 
                      ? `Completed: ${new Date(inv.completed_at).toLocaleString()}`
                      : inv.started_at
                        ? `Started: ${new Date(inv.started_at).toLocaleString()}`
                        : `Created: ${new Date(inv.created_at).toLocaleString()}`
                    }
                  </span>
                  <button
                    onClick={() => setExpandedInvestigation(
                      expandedInvestigation === inv.id ? null : inv.id
                    )}
                    className="expand-btn"
                  >
                    {expandedInvestigation === inv.id ? '▼ Hide Details' : '▶ Show Details'}
                  </button>
                </div>

                {expandedInvestigation === inv.id && (
                  <div className="investigation-details">
                    <div className="reasoning-steps">
                      <h4>🧠 Reasoning Steps</h4>
                      {inv.reasoning_steps && inv.reasoning_steps.length > 0 ? (
                        <ol>
                          {inv.reasoning_steps.map((step: any, idx: number) => (
                            <li key={idx} className="reasoning-step">
                              <strong>{step.action}:</strong>
                              <p>{step.description}</p>
                              <div className="step-result">
                                <strong>Result:</strong> {step.result}
                              </div>
                            </li>
                          ))}
                        </ol>
                      ) : (
                        <p>No reasoning steps available</p>
                      )}
                    </div>

                    <div className="evidence-section">
                      <h4>📊 Evidence</h4>
                      {inv.evidence && inv.evidence.length > 0 ? (
                        <div className="evidence-list">
                          {inv.evidence.map((ev: any, idx: number) => (
                            <div key={idx} className="evidence-item">
                              <strong>{ev.type?.replace(/_/g, ' ') || 'Evidence'}:</strong>
                              <pre>{JSON.stringify(ev, null, 2)}</pre>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p>No evidence available</p>
                      )}
                    </div>

                    {inv.test_criteria && inv.test_criteria.length > 0 && (
                      <div className="test-criteria">
                        <h4>📋 Test Criteria</h4>
                        <ul>
                          {inv.test_criteria.map((criterion, idx) => (
                            <li key={idx}>{criterion}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentConsole;

