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

  // Topic clustering logic
  const getTopicFromMarket = (market: Market): string => {
    const question = market.question_text.toLowerCase();
    
    if (question.includes('debate') || question.includes('oversight') || question.includes('scalable')) {
      return 'Alignment & Oversight';
    } else if (question.includes('interpretability') || question.includes('mechanistic') || question.includes('attention')) {
      return 'Interpretability';
    } else if (question.includes('constitutional') || question.includes('harmless') || question.includes('safety')) {
      return 'AI Safety';
    } else if (question.includes('emergent') || question.includes('scaling') || question.includes('capabilities')) {
      return 'Scaling & Capabilities';
    } else if (question.includes('adversarial') || question.includes('robustness') || question.includes('security')) {
      return 'Robustness & Security';
    } else if (question.includes('reward') || question.includes('reinforcement') || question.includes('optimization')) {
      return 'RL & Optimization';
    } else {
      return 'General AI Research';
    }
  };

  // Group markets by topic
  const marketsByTopic = markets.reduce((acc, market) => {
    const topic = getTopicFromMarket(market);
    if (!acc[topic]) {
      acc[topic] = [];
    }
    acc[topic].push(market);
    return acc;
  }, {} as Record<string, Market[]>);

  const topicOrder = [
    'Alignment & Oversight',
    'AI Safety', 
    'Interpretability',
    'Scaling & Capabilities',
    'Robustness & Security',
    'RL & Optimization',
    'General AI Research'
  ];

  if (isLoading) {
    return <div className="loading">Loading markets...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Active Prediction Markets</h1>
      <p className="subtitle">AI Safety Research Claims</p>

      {markets.length === 0 ? (
        <div className="empty-state">
          <p>No active markets yet. Run the scraper to generate markets from research papers.</p>
        </div>
      ) : (
        <div className="topics-container">
          {topicOrder.map((topic) => {
            const topicMarkets = marketsByTopic[topic];
            if (!topicMarkets || topicMarkets.length === 0) return null;
            
            return (
              <div key={topic} className="topic-cluster">
                <div className="topic-header">
                  <h2 className="topic-title">{topic}</h2>
                  <span className="topic-count">{topicMarkets.length} market{topicMarkets.length !== 1 ? 's' : ''}</span>
                </div>
                
                <div className="markets-grid">
                  {topicMarkets.map((market) => (
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
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Dashboard;

