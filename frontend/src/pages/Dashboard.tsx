import React, { useMemo } from 'react';
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

  // Topic clustering and popularity calculation
  const { topicClusters, maxPopularity } = useMemo(() => {
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

    // Calculate popularity score for each market
    const marketsWithPopularity = markets.map(market => {
      // Simulate popularity based on market ID, creation date, and question length
      // In a real app, this would be based on actual bet volume/stakes
      const basePopularity = Math.random() * 100; // Random for demo
      const recencyBonus = (Date.now() - new Date(market.created_at).getTime()) / (1000 * 60 * 60 * 24); // Days since creation
      const complexityBonus = market.question_text.length / 10; // Longer questions = more complex
      
      return {
        ...market,
        popularity: Math.max(10, basePopularity - recencyBonus + complexityBonus)
      };
    });

    // Group by topic and calculate cluster positions
    const clusters = marketsWithPopularity.reduce((acc, market) => {
      const topic = getTopicFromMarket(market);
      if (!acc[topic]) {
        acc[topic] = [];
      }
      acc[topic].push(market);
      return acc;
    }, {} as Record<string, typeof marketsWithPopularity>);

    const maxPop = Math.max(...marketsWithPopularity.map(m => m.popularity));

    return {
      topicClusters: clusters,
      maxPopularity: maxPop
    };
  }, [markets]);

  // Topic colors and positions for graph layout - spread across full width with left alignment
  const topicConfig = {
    'Alignment & Oversight': { color: '#667eea', x: 8, y: 20 },
    'AI Safety': { color: '#f093fb', x: 30, y: 20 },
    'Interpretability': { color: '#4facfe', x: 55, y: 20 },
    'Scaling & Capabilities': { color: '#43e97b', x: 80, y: 20 },
    'Robustness & Security': { color: '#fa709a', x: 18, y: 60 },
    'RL & Optimization': { color: '#a8edea', x: 45, y: 60 },
    'General AI Research': { color: '#ffecd2', x: 72, y: 60 }
  };

  if (isLoading) {
    return <div className="loading">Loading markets...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Prediction Market Graph</h1>
      <p className="subtitle">AI Safety Research Clusters - Box size reflects popularity</p>

      {markets.length === 0 ? (
        <div className="empty-state">
          <p>No active markets yet. Run the scraper to generate markets from research papers.</p>
        </div>
      ) : (
        <div className="markets-layout">
          {/* Markets grouped by topic */}
          {Object.entries(topicClusters).map(([topic, topicMarkets]) => {
            const config = topicConfig[topic as keyof typeof topicConfig];
            if (!config || !topicMarkets.length) return null;

            return (
              <div key={topic} className="topic-section">
                <h2 className="topic-heading" style={{ color: config.color }}>
                  {topic}
                </h2>
                <div className="topic-grid">
                  {topicMarkets.map((market) => {
                    // Calculate size based on popularity
                    const size = Math.max(240, Math.min(360, 240 + (market.popularity / maxPopularity) * 120));

                    return (
                      <Link
                        to={`/markets/${market.id}`}
                        key={market.id}
                        className="market-card"
                        style={{
                          width: `${size}px`,
                          minHeight: `${size}px`,
                          borderColor: config.color,
                        }}
                      >
                        <div className="topic-label-box" style={{ background: config.color }}>
                          {topic}
                        </div>
                  <div className="market-content">
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
                      <span className="popularity-score">
                        Popularity: {Math.round(market.popularity)}
                      </span>
                    </div>
                        </div>
                      </Link>
                    );
                  })}
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

