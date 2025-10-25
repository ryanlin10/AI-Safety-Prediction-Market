import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Market, Experiment } from '../types';
import './MarketDetail.css';

const MarketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const marketId = parseInt(id || '0');
  const queryClient = useQueryClient();
  const [selectedAgentId, setSelectedAgentId] = useState<number>(1);

  const { data: marketData, isLoading: marketLoading } = useQuery({
    queryKey: ['market', marketId],
    queryFn: () => api.getMarket(marketId),
  });

  const { data: experimentsData } = useQuery({
    queryKey: ['experiments', marketId],
    queryFn: () => api.getMarketExperiments(marketId),
  });

  const { data: agentsData } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents(),
  });

  const runExperimentMutation = useMutation({
    mutationFn: () => api.runExperiment(marketId, selectedAgentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments', marketId] });
    },
  });

  const market: Market = marketData?.data;
  const experiments: Experiment[] = experimentsData?.data?.experiments || [];
  const agents = agentsData?.data?.agents || [];

  if (marketLoading) {
    return <div className="loading">Loading market...</div>;
  }

  if (!market) {
    return <div className="error">Market not found</div>;
  }

  const researcherAgents = agents.filter((a: any) => a.type === 'researcher');

  return (
    <div className="market-detail">
      <div className="market-header-section">
        <h1>{market.question_text}</h1>
        <span className={`status-badge status-${market.status}`}>
          {market.status}
        </span>
      </div>

      {market.idea && (
        <div className="idea-section">
          <h2>Research Idea</h2>
          <div className="idea-card">
            <h3>{market.idea.title}</h3>
            <p className="abstract">{market.idea.abstract}</p>
            {market.idea.extracted_claim && (
              <div className="claim">
                <strong>Extracted Claim:</strong> {market.idea.extracted_claim}
              </div>
            )}
            <div className="keywords">
              {market.idea.keywords.map((keyword) => (
                <span key={keyword} className="keyword-tag">{keyword}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="outcomes-section">
        <h2>Outcomes & Current Odds</h2>
        <div className="outcomes-grid">
          {market.outcomes.map((outcome) => (
            <div key={outcome} className="outcome-card">
              <div className="outcome-name">{outcome}</div>
              <div className="outcome-odds">
                {market.current_odds
                  ? `${(market.current_odds[outcome] * 100).toFixed(1)}%`
                  : 'No bets yet'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bets-section">
        <h2>Bets ({market.bets?.length || 0})</h2>
        <div className="bets-list">
          {market.bets && market.bets.length > 0 ? (
            market.bets.map((bet) => (
              <div key={bet.id} className="bet-card">
                <div className="bet-header">
                  <span className="bet-outcome">{bet.outcome}</span>
                  <span className={bet.is_agent_bet ? 'agent-badge' : 'user-badge'}>
                    {bet.is_agent_bet ? '🤖 Agent' : '👤 User'}
                  </span>
                </div>
                <div className="bet-details">
                  <span>Stake: ${bet.stake}</span>
                  <span>Odds: {bet.odds.toFixed(2)}</span>
                </div>
                {bet.rationale && (
                  <div className="bet-rationale">
                    <strong>Rationale:</strong> {bet.rationale}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="empty-message">No bets placed yet</p>
          )}
        </div>
      </div>

      <div className="experiments-section">
        <h2>Experiments</h2>
        <div className="experiment-controls">
          <select
            value={selectedAgentId}
            onChange={(e) => setSelectedAgentId(parseInt(e.target.value))}
            className="agent-select"
          >
            {researcherAgents.map((agent: any) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => runExperimentMutation.mutate()}
            disabled={runExperimentMutation.isPending}
            className="run-experiment-btn"
          >
            {runExperimentMutation.isPending ? 'Running...' : 'Run Experiment'}
          </button>
        </div>

        <div className="experiments-list">
          {experiments.map((exp) => (
            <div key={exp.id} className="experiment-card">
              <div className="experiment-header">
                <span className={`status-badge status-${exp.status}`}>
                  {exp.status}
                </span>
                <span className="experiment-id">Experiment #{exp.id}</span>
              </div>
              
              {exp.result && (
                <div className="experiment-result">
                  <div className="result-metrics">
                    <div className="metric">
                      <label>Baseline:</label>
                      <span>{exp.result.baseline_metric?.toFixed(4)}</span>
                    </div>
                    <div className="metric">
                      <label>Fine-tuned:</label>
                      <span>{exp.result.fine_tuned_metric?.toFixed(4)}</span>
                    </div>
                    <div className="metric">
                      <label>Delta:</label>
                      <span className={exp.result.success ? 'success' : 'failure'}>
                        {exp.result.delta?.toFixed(4)}
                      </span>
                    </div>
                  </div>
                  <div className={`result-badge ${exp.result.success ? 'pass' : 'fail'}`}>
                    {exp.result.success ? 'PASS' : 'FAIL'}
                  </div>
                </div>
              )}

              {exp.logs && (
                <details className="experiment-logs">
                  <summary>View Logs</summary>
                  <pre>{exp.logs}</pre>
                </details>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketDetail;

