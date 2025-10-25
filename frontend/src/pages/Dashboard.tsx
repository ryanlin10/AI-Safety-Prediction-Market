import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Market } from '../types';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { data: marketsData, isLoading } = useQuery({
    queryKey: ['markets'],
    queryFn: () => api.getMarkets({ status: 'active' }),
  });

  const markets: Market[] = marketsData?.data?.markets || [];

  if (isLoading) {
    return <div className="loading">Loading markets...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Active Prediction Markets</h1>
      <p className="subtitle">AI Safety Research Claims</p>

      <div className="markets-grid">
        {markets.length === 0 ? (
          <div className="empty-state">
            <p>No active markets yet. Run the scraper to generate markets from research papers.</p>
          </div>
        ) : (
          markets.map((market) => (
            <Link to={`/markets/${market.id}`} key={market.id} className="market-card">
              <div className="market-header">
                <span className={`status-badge status-${market.status}`}>
                  {market.status}
                </span>
                <span className="market-id">#{market.id}</span>
              </div>
              
              <h3 className="market-question">{market.question_text}</h3>
              
              <div className="market-outcomes">
                {market.outcomes.map((outcome) => (
                  <div key={outcome} className="outcome-chip">
                    {outcome}
                  </div>
                ))}
              </div>

              <div className="market-footer">
                <span className="market-date">
                  Created {new Date(market.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;

