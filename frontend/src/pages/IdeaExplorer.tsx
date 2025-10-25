import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Idea } from '../types';
import './IdeaExplorer.css';

const IdeaExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: ideasData, isLoading } = useQuery({
    queryKey: ['ideas', searchQuery],
    queryFn: () => api.getIdeas({ query: searchQuery, limit: 50 }),
  });

  const ideas: Idea[] = ideasData?.data?.ideas || [];

  return (
    <div className="idea-explorer">
      <h1>Research Ideas</h1>
      
      <div className="search-section">
        <input
          type="text"
          placeholder="Search ideas by title, abstract, or claim..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {isLoading ? (
        <div className="loading">Loading ideas...</div>
      ) : (
        <div className="ideas-list">
          {ideas.length === 0 ? (
            <div className="empty-state">
              <p>No ideas found. Run the scraper to fetch research papers.</p>
            </div>
          ) : (
            ideas.map((idea) => (
              <div key={idea.id} className="idea-card">
                <div className="idea-header">
                  <h3>{idea.title}</h3>
                  <span className="confidence-score">
                    Confidence: {(idea.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
                
                <p className="idea-abstract">{idea.abstract}</p>
                
                {idea.extracted_claim && (
                  <div className="extracted-claim">
                    <strong>Testable Claim:</strong> {idea.extracted_claim}
                  </div>
                )}
                
                <div className="idea-keywords">
                  {idea.keywords.map((keyword) => (
                    <span key={keyword} className="keyword-tag">{keyword}</span>
                  ))}
                </div>
                
                <div className="idea-footer">
                  <span className="idea-date">
                    {new Date(idea.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default IdeaExplorer;

