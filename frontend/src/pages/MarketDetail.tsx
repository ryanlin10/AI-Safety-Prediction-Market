import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Market } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './MarketDetail.css';

const MarketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const marketId = parseInt(id || '0');
  const queryClient = useQueryClient();
  const [buyAmounts, setBuyAmounts] = useState<{ [key: string]: number }>({});
  const [claimCount, setClaimCount] = useState<number>(5);

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

  const buySharesMutation = useMutation({
    mutationFn: ({ outcome, amount }: { outcome: string; amount: number }) =>
      api.buyShares(marketId, outcome, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prices', marketId] });
      queryClient.invalidateQueries({ queryKey: ['priceHistory', marketId] });
      queryClient.invalidateQueries({ queryKey: ['market', marketId] });
    },
  });

  const generateClaimsMutation = useMutation({
    mutationFn: (count: number) => api.generateClaims(count),
    onSuccess: (data) => {
      // Invalidate ideas to refresh the list
      queryClient.invalidateQueries({ queryKey: ['ideas'] });
      alert(`✅ Successfully generated ${data.data.generated_count} research claims! Check the Ideas Explorer to see them.`);
    },
  });

  const market: Market = marketData?.data;
  const prices = pricesData?.data?.prices || {};
  const priceHistory = priceHistoryData?.data?.history || [];

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

      {/* Market Resolution Criteria */}
      <div className="resolution-section">
        <h2>📋 Resolution Criteria</h2>
        <div className="resolution-box">
          <div className="resolution-header">
            <span className="resolution-icon">⚖️</span>
            <h3>How This Market Will Be Resolved</h3>
          </div>
          
          {market.resolution_rule ? (
            <div className="resolution-content">
              {typeof market.resolution_rule === 'string' ? (
                <p>{market.resolution_rule}</p>
              ) : (
                <>
                  {market.resolution_rule.description && (
                    <div className="resolution-description">
                      <strong>Description:</strong>
                      <p>{market.resolution_rule.description}</p>
                    </div>
                  )}
                  
                  {market.resolution_rule.criteria && (
                    <div className="resolution-criteria-list">
                      <strong>Criteria:</strong>
                      <ul>
                        {Array.isArray(market.resolution_rule.criteria) ? (
                          market.resolution_rule.criteria.map((criterion: string, idx: number) => (
                            <li key={idx}>{criterion}</li>
                          ))
                        ) : (
                          <li>{market.resolution_rule.criteria}</li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  {market.resolution_rule.source && (
                    <div className="resolution-source">
                      <strong>Source:</strong> {market.resolution_rule.source}
                    </div>
                  )}
                  
                  {market.resolution_rule.deadline && (
                    <div className="resolution-deadline">
                      <strong>Resolution Deadline:</strong> {new Date(market.resolution_rule.deadline).toLocaleDateString()}
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="resolution-placeholder">
              <p>Resolution criteria will be determined by market administrators based on:</p>
              <ul>
                <li>Official announcements from relevant organizations</li>
                <li>Peer-reviewed publication results</li>
                <li>Consensus among domain experts</li>
                <li>Verifiable experimental outcomes</li>
              </ul>
            </div>
          )}
          
          {market.close_date && (
            <div className="resolution-dates">
              <div className="date-item">
                <span className="date-label">Market Closes:</span>
                <span className="date-value">{new Date(market.close_date).toLocaleString()}</span>
              </div>
            </div>
          )}
          
          {market.resolved_at && (
            <div className="resolution-status resolved">
              <strong>✅ RESOLVED:</strong> This market was resolved on {new Date(market.resolved_at).toLocaleString()}
              {market.resolution_outcome && <span className="outcome-badge">{market.resolution_outcome}</span>}
            </div>
          )}
        </div>
      </div>

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

      <div className="generate-claims-section">
        <h2>🔬 Generate Research Claims</h2>
        <div className="generate-claims-box">
          <p className="section-description">
            Generate testable research claims using our AI claim generator. 
            These claims will be added to the Ideas Explorer and can be used to create new prediction markets.
          </p>
          
          <div className="generate-controls">
            <div className="count-selector">
              <label htmlFor="claim-count">Number of Claims:</label>
              <input
                id="claim-count"
                type="number"
                min="1"
                max="20"
                value={claimCount}
                onChange={(e) => setClaimCount(parseInt(e.target.value) || 5)}
                className="claim-count-input"
              />
            </div>
            
            <button
              onClick={() => generateClaimsMutation.mutate(claimCount)}
              disabled={generateClaimsMutation.isPending}
              className="generate-claims-btn"
            >
              {generateClaimsMutation.isPending ? (
                <>
                  <span className="spinner">⚙️</span> Generating...
                </>
              ) : (
                <>
                  <span className="icon">✨</span> Generate Claims
                </>
              )}
            </button>
          </div>

          <div className="claims-info">
            <div className="info-item">
              <span className="info-icon">📊</span>
              <span>Generated claims are based on current AI safety research trends</span>
            </div>
            <div className="info-item">
              <span className="info-icon">🎯</span>
              <span>Each claim includes testable hypotheses and confidence scores</span>
            </div>
            <div className="info-item">
              <span className="info-icon">🔍</span>
              <span>View generated claims in the Ideas Explorer page</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketDetail;

