import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Market, Experiment } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './MarketDetail.css';

const MarketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const marketId = parseInt(id || '0');
  const queryClient = useQueryClient();
  const [selectedAgentId, setSelectedAgentId] = useState<number>(1);
  const [buyAmounts, setBuyAmounts] = useState<{ [key: string]: number }>({});

  const { data: marketData, isLoading: marketLoading } = useQuery({
    queryKey: ['market', marketId],
    queryFn: () => api.getMarket(marketId),
  });

  const { data: pricesData, isLoading: pricesLoading } = useQuery({
    queryKey: ['prices', marketId],
    queryFn: () => api.getMarketPrices(marketId),
    refetchInterval: 5000, // Refresh prices every 5 seconds
  });

  const { data: priceHistoryData } = useQuery({
    queryKey: ['priceHistory', marketId],
    queryFn: () => api.getPriceHistory(marketId),
  });

  const { data: experimentsData } = useQuery({
    queryKey: ['experiments', marketId],
    queryFn: () => api.getMarketExperiments(marketId),
  });

  const { data: agentsData } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents(),
  });

  const buySharesMutation = useMutation({
    mutationFn: ({ outcome, amount }: { outcome: string; amount: number }) =>
      api.buyShares(marketId, outcome, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prices', marketId] });
      queryClient.invalidateQueries({ queryKey: ['priceHistory', marketId] });
      queryClient.invalidateQueries({ queryKey: ['market', marketId] });
    },
  });

  const runExperimentMutation = useMutation({
    mutationFn: () => api.runExperiment(marketId, selectedAgentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments', marketId] });
    },
  });

  const market: Market = marketData?.data;
  const prices = pricesData?.data?.prices || {};
  const priceHistory = priceHistoryData?.data?.history || [];
  const experiments: Experiment[] = experimentsData?.data?.experiments || [];
  const agents = agentsData?.data?.agents || [];

  const handleBuyShares = (outcome: string) => {
    const amount = buyAmounts[outcome] || 10;
    buySharesMutation.mutate({ outcome, amount });
  };

  const setBuyAmount = (outcome: string, amount: number) => {
    setBuyAmounts(prev => ({ ...prev, [outcome]: amount }));
  };

  if (marketLoading) {
    return <div className="loading">Loading market...</div>;
  }

  if (!market) {
    return <div className="error">Market not found</div>;
  }

  const researcherAgents = agents.filter((a: any) => a.agent_type === 'researcher');

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

      <div className="trading-section">
        <h2>Trade Shares</h2>
        
        {/* Price Chart */}
        {priceHistory.length > 1 && (
          <div className="price-chart">
            <h3>Price History</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
                />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <Tooltip 
                  labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                  formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
                />
                <Legend />
                {market.outcomes.map((outcome, idx) => (
                  <Line
                    key={outcome}
                    type="monotone"
                    dataKey={`prices.${outcome}`}
                    name={outcome}
                    stroke={['#4CAF50', '#2196F3', '#FF9800', '#9C27B0'][idx % 4]}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Trading Interface */}
        <div className="outcomes-grid">
          {market.outcomes.map((outcome) => {
            const outcomePrice = prices[outcome] || {};
            const buyPrice = outcomePrice.buy_price || 0;
            const currentPrice = outcomePrice.current_price || 0;
            const amount = buyAmounts[outcome] || 10;
            const totalCost = (buyPrice * amount).toFixed(2);

            return (
              <div key={outcome} className="outcome-trading-card">
                <div className="outcome-header">
                  <h3>{outcome}</h3>
                  <div className="current-probability">
                    {(currentPrice * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="price-display">
                  <div className="price-label">Buy Price</div>
                  <div className="price-value">${buyPrice.toFixed(4)}/share</div>
                </div>

                <div className="trading-controls">
                  <div className="amount-input">
                    <label>Shares:</label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={amount}
                      onChange={(e) => setBuyAmount(outcome, parseInt(e.target.value) || 10)}
                      className="shares-input"
                    />
                  </div>

                  <div className="total-cost">
                    Total: ${totalCost}
                  </div>

                  <button
                    onClick={() => handleBuyShares(outcome)}
                    disabled={buySharesMutation.isPending || market.status !== 'active'}
                    className="buy-button"
                  >
                    {buySharesMutation.isPending ? 'Buying...' : `Buy ${outcome}`}
                  </button>
                </div>

                <div className="liquidity-info">
                  Liquidity: ${(outcomePrice.liquidity || 0).toFixed(2)}
                </div>
              </div>
            );
          })}
        </div>

        {pricesLoading && <div className="loading-overlay">Updating prices...</div>}
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

