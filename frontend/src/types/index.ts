export interface Idea {
  id: number;
  source_id: number;
  title: string;
  abstract: string;
  keywords: string[];
  extracted_claim: string;
  confidence_score: number;
  created_at: string;
}

export interface Market {
  id: number;
  idea_id: number;
  question_text: string;
  outcomes: string[];
  resolution_rule: any;
  status: 'draft' | 'active' | 'closed' | 'resolved';
  created_at: string;
  close_date?: string;
  resolved_at?: string;
  resolution_outcome?: string;
  current_odds?: { [key: string]: number };
  bets?: Bet[];
  idea?: Idea;
}

export interface Bet {
  id: number;
  market_id: number;
  user_id?: number;
  agent_id?: number;
  outcome: string;
  stake: number;
  odds: number;
  rationale?: string;
  created_at: string;
  is_agent_bet: boolean;
}

export interface Agent {
  id: number;
  name: string;
  agent_type: 'bettor' | 'researcher';
  meta: any;
  created_at: string;
  is_active: boolean;
}

export interface Experiment {
  id: number;
  market_id: number;
  agent_id: number;
  config: any;
  result?: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  logs?: string;
  started_at?: string;
  finished_at?: string;
  created_at: string;
  market?: Market;
}

