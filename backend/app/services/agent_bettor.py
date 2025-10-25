import openai
from app.models import Idea, Market, Bet
from app import db

class AgentBettor:
    """LLM-based agent that places bets on markets"""
    
    def __init__(self, agent, config):
        self.agent = agent
        self.config = config
        openai.api_key = config.get('OPENAI_API_KEY')
    
    def generate_bet(self, market):
        """Generate a bet recommendation for a market"""
        # Get the idea associated with the market
        idea = Idea.query.get(market.idea_id)
        
        # Get similar historical bets (simplified for demo)
        historical_context = self._get_historical_context(idea)
        
        # Build prompt for LLM
        prompt = self._build_prompt(market, idea, historical_context)
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI safety researcher evaluating the likelihood of research claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            result = self._parse_llm_response(response.choices[0].message.content, market)
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate bet: {str(e)}")
    
    def _build_prompt(self, market, idea, historical_context):
        """Build the prompt for the LLM"""
        prompt = f"""
You are evaluating a prediction market about an AI safety research claim.

Market Question: {market.question_text}

Idea Details:
- Title: {idea.title}
- Abstract: {idea.abstract}
- Extracted Claim: {idea.extracted_claim}

Possible Outcomes: {', '.join(market.outcomes)}

Resolution Rule:
{market.resolution_rule}

Historical Context:
{historical_context}

Please provide:
1. Your probability estimate for each outcome (must sum to 1.0)
2. Top 3 pieces of evidence supporting your estimate
3. Recommended stake (as a percentage, max 100)
4. Brief rationale (2-3 sentences)

Format your response as JSON:
{{
    "probabilities": {{"outcome1": 0.X, "outcome2": 0.Y}},
    "evidence": ["point 1", "point 2", "point 3"],
    "stake_percentage": X,
    "rationale": "Your reasoning here"
}}
"""
        return prompt
    
    def _parse_llm_response(self, response_text, market):
        """Parse the LLM response into a bet recommendation"""
        import json
        
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Determine outcome with highest probability
            probabilities = parsed.get('probabilities', {})
            best_outcome = max(probabilities.items(), key=lambda x: x[1])[0]
            probability = probabilities[best_outcome]
            
            # Convert probability to odds
            odds = probability / (1 - probability) if probability < 1 else 10.0
            
            # Calculate stake
            stake_percentage = parsed.get('stake_percentage', 10)
            stake = min(
                (stake_percentage / 100) * self.config['AGENT_MAX_STAKE'],
                self.config['AGENT_MAX_STAKE']
            )
            
            # Build rationale
            evidence = parsed.get('evidence', [])
            rationale_text = parsed.get('rationale', '')
            rationale = f"{rationale_text}\n\nEvidence:\n" + "\n".join(f"- {e}" for e in evidence)
            
            return {
                'outcome': best_outcome,
                'probability': probability,
                'odds': odds,
                'stake': stake,
                'rationale': rationale
            }
            
        except Exception as e:
            # Fallback to simple bet
            return {
                'outcome': market.outcomes[0],
                'probability': 0.5,
                'odds': 1.0,
                'stake': self.config['AGENT_MAX_STAKE'] * 0.1,
                'rationale': f"Automated bet (parsing failed: {str(e)})"
            }
    
    def _get_historical_context(self, idea):
        """Get historical context from similar ideas/markets"""
        # Simplified for demo - in production, use embedding similarity
        context = "Limited historical data available for this type of claim."
        
        if idea.keywords:
            # Find similar ideas by keywords
            similar_ideas = Idea.query.filter(
                Idea.keywords.overlap(idea.keywords)
            ).limit(3).all()
            
            if similar_ideas:
                context = "Similar research areas:\n"
                for similar in similar_ideas:
                    context += f"- {similar.title}\n"
        
        return context

