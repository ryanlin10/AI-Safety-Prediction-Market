import React, { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { Market } from '../types';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const [keyword, setKeyword] = useState('');
  const [newlyGeneratedIds, setNewlyGeneratedIds] = useState<Set<number>>(new Set());
  
  const { data: marketsData, isLoading } = useQuery({
    queryKey: ['markets'],
    queryFn: () => api.getMarkets({ status: 'active' }),
  });

  const markets: Market[] = marketsData?.data?.markets || [];

  // Generate market mutation
  const generateMarketMutation = useMutation({
    mutationFn: (searchKeyword: string) => api.generateMarket(searchKeyword),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['markets'] });
      if (response.data?.market?.id) {
        const marketId = response.data.market.id;
        setNewlyGeneratedIds(prev => {
          const updated = new Set(prev);
          updated.add(marketId);
          return updated;
        });
        // Remove highlight after 5 seconds
        setTimeout(() => {
          setNewlyGeneratedIds(prev => {
            const updated = new Set(prev);
            updated.delete(marketId);
            return updated;
          });
        }, 5000);
      }
      setKeyword('');
    },
    onError: (error: any) => {
      console.error('Failed to generate market:', error);
      alert(error.response?.data?.error || 'Failed to generate market. Please try a different keyword.');
    },
  });

  const handleGenerateMarket = () => {
    if (keyword.trim()) {
      generateMarketMutation.mutate(keyword.trim());
    }
  };

  // Topic clustering and popularity calculation
  const { topicClusters, maxPopularity, rankedMarkets } = useMemo(() => {
    const getTopicFromMarket = (market: Market): string => {
      // Use keywords from the associated idea, otherwise fall back to question text
      const keywords = market.idea?.keywords || [];
      const keywordsStr = Array.isArray(keywords) ? keywords.join(' ') : '';
      const keywordsLower = keywordsStr.toLowerCase();
      const question = market.question_text.toLowerCase();
      
      // Prioritize mechanistic interpretability as a specific category
      if (keywordsLower.includes('mechanistic interpretability') || 
          keywordsLower.includes('mechanistic analysis')) {
        return 'Mechanistic Interpretability';
      }
      
      // Then check for general interpretability
      if (keywordsLower.includes('interpretability') || 
          keywordsLower.includes('explainability')) {
        return 'Interpretability & Explainability';
      }
      
      // Alignment includes oversight, value learning, etc.
      if (keywordsLower.includes('alignment') || 
          question.includes('alignment') ||
          question.includes('oversight') || 
          question.includes('value learning')) {
        return 'Alignment & Value Learning';
      }
      
      // Safety includes robustness, security, adversarial
      if (keywordsLower.includes('safety') || 
          question.includes('safety') ||
          question.includes('robustness') || 
          question.includes('adversarial') ||
          question.includes('security')) {
        return 'Safety & Robustness';
      }
      
      // Fallback for any remaining markets
      if (question.includes('neural') || question.includes('network') || question.includes('model')) {
        return 'Neural Network Analysis';
      }
      
      if (question.includes('language model') || question.includes('llm') || question.includes('transformer')) {
        return 'Language Models';
      }
      
      // Final fallback - should rarely be used
      return 'AI Research';
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
        popularity: Math.max(10, basePopularity - recencyBonus + complexityBonus),
        topic: getTopicFromMarket(market)
      };
    });

    // Group by topic and calculate cluster positions
    const clusters = marketsWithPopularity.reduce((acc, market) => {
      const topic = market.topic;
      if (!acc[topic]) {
        acc[topic] = [];
      }
      acc[topic].push(market);
      return acc;
    }, {} as Record<string, typeof marketsWithPopularity>);

    const maxPop = Math.max(...marketsWithPopularity.map(m => m.popularity));

    // Sort markets by popularity for ranking sidebar
    const ranked = [...marketsWithPopularity].sort((a, b) => b.popularity - a.popularity);

    return {
      topicClusters: clusters,
      maxPopularity: maxPop,
      rankedMarkets: ranked
    };
  }, [markets]);

  // Topic colors for grouped layout - unified blue/green/purple/maroon palette (more vibrant)
  const topicConfig = {
    'Mechanistic Interpretability': { color: '#5B6FED' },      // Purple-blue (more vibrant)
    'Interpretability & Explainability': { color: '#4A8FDB' }, // Sky blue (more vibrant)
    'Alignment & Value Learning': { color: '#8B4FD9' },        // Deep purple (more vibrant)
    'Safety & Robustness': { color: '#B63D6E' },               // Maroon (more vibrant)
    'Neural Network Analysis': { color: '#3BA89A' },           // Teal-green (more vibrant)
    'Language Models': { color: '#5A7DC7' },                   // Steel blue (more vibrant)
    'AI Research': { color: '#8A5BC2' }                        // Lavender purple (more vibrant)
  };

  if (isLoading) {
    return <div className="loading">Loading markets...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Prediction Market</h1>
          <p className="subtitle">AI Safety Research Clusters - Box size reflects popularity</p>
        </div>
        <div className="generate-market-section">
          <input
            type="text"
            className="keyword-input"
            placeholder="Enter keyword (e.g., alignment, safety)"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleGenerateMarket()}
            disabled={generateMarketMutation.isPending}
          />
          <button
            className="generate-market-btn"
            onClick={handleGenerateMarket}
            disabled={!keyword.trim() || generateMarketMutation.isPending}
          >
            {generateMarketMutation.isPending ? 'Generating...' : '+ Generate Market'}
          </button>
        </div>
      </div>

      {markets.length === 0 ? (
        <div className="empty-state">
          <p>No active markets yet. Run the scraper to generate markets from research papers.</p>
        </div>
      ) : (
        <div className="dashboard-content">
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
                      const isNewlyGenerated = newlyGeneratedIds.has(market.id);

                      return (
                        <Link
                          to={`/markets/${market.id}`}
                          key={market.id}
                          className={`market-card ${isNewlyGenerated ? 'newly-generated' : ''}`}
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
                            
                            <div className="market-outcomes-votes">
                              {market.outcomes.map((outcome) => {
                                const isYes = outcome.toLowerCase() === 'yes';
                                const isNo = outcome.toLowerCase() === 'no';
                                
                                // Get the actual percentage from current_odds (which represents probability)
                                let percentage = 50; // Default fallback
                                if (market.current_odds && market.current_odds[outcome] !== undefined) {
                                  percentage = market.current_odds[outcome] * 100;
                                }
                                
                                return (
                                  <div 
                                    key={outcome} 
                                    className={`outcome-vote-chip ${isYes ? 'outcome-yes' : isNo ? 'outcome-no' : ''}`}
                                  >
                                    <span className="outcome-label">{outcome}</span>
                                    <span className="outcome-percentage">{percentage.toFixed(0)}%</span>
                                  </div>
                                );
                              })}
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

          {/* Popularity ranking sidebar */}
          <div className="ranking-sidebar">
            <div className="ranking-header">
              <h3>🔥 Top Markets</h3>
              <p className="ranking-subtitle">By Popularity</p>
            </div>
            <div className="ranking-list">
              {rankedMarkets.map((market, index) => {
                const config = topicConfig[market.topic as keyof typeof topicConfig];
                return (
                  <Link
                    to={`/markets/${market.id}`}
                    key={market.id}
                    className="ranking-item"
                  >
                    <div className="ranking-number" style={{ backgroundColor: config?.color || '#ccc' }}>
                      {index + 1}
                    </div>
                    <div className="ranking-content">
                      <div className="ranking-question">{market.question_text}</div>
                      <div className="ranking-meta">
                        <span className="ranking-topic" style={{ color: config?.color || '#666' }}>
                          {market.topic}
                        </span>
                        <span className="ranking-score">
                          {Math.round(market.popularity)} pts
                        </span>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

