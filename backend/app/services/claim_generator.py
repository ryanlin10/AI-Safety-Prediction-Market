"""
Research Claim Generator Service
Generates testable research claims for AI safety and alignment research using OpenAI
"""
import json
from typing import List, Dict
from openai import OpenAI
from flask import current_app

class ClaimGenerator:
    """Generate testable research claims using OpenAI"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
        return self.client
    
    CATEGORIES = [
        "scalability",
        "alignment", 
        "interpretability",
        "safety",
        "capabilities"
    ]
    
    def generate_claim(self, category: str = None) -> Dict:
        """Generate a single research claim using OpenAI"""
        if category is None or category not in self.CATEGORIES:
            import random
            category = random.choice(self.CATEGORIES)
        
        client = self._get_client()
        
        prompt = f"""Generate a realistic, testable research claim in the AI safety and alignment field, specifically in the category: {category}.

Create a complete research paper summary including:
1. A title (10-15 words)
2. An abstract (100-150 words) 
3. A list of 4-6 relevant keywords
4. A specific, testable claim extracted from the research (one clear sentence)
5. A confidence score (0.65-0.95) indicating how plausible/testable this claim is

The claim should be:
- Specific and measurable
- Grounded in current AI safety research trends
- Neither obviously true nor obviously false
- Testable through empirical methods or theoretical analysis

Category definitions:
- scalability: Scaling laws, efficiency, compute optimization
- alignment: Value alignment, RLHF, constitutional AI
- interpretability: Mechanistic interpretability, causal tracing, circuit analysis
- safety: Risk detection, adversarial robustness, red teaming
- capabilities: Emergent abilities, reasoning, chain-of-thought

Return your response in JSON format:
{{
    "title": "Paper title",
    "abstract": "Paper abstract...",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
    "claim": "The specific testable claim",
    "confidence_score": 0.85,
    "category": "{category}"
}}"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI safety researcher who generates realistic research paper summaries and testable claims. 
Your claims should be based on current trends in AI safety research but should be novel and interesting.
Always respond with valid JSON."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher temperature for more creative/diverse claims
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields are present
            required_fields = ['title', 'abstract', 'keywords', 'claim', 'confidence_score']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            result['category'] = category
            
            return result
            
        except Exception as e:
            print(f"Error generating claim with OpenAI: {e}")
            # Fallback to a template-based claim
            return self._generate_fallback_claim(category)
    
    def _generate_fallback_claim(self, category: str) -> Dict:
        """Fallback claim generation if OpenAI fails"""
        import random
        
        fallback_claims = {
            "scalability": {
                "title": "Scaling Laws for Transformer Models in Few-Shot Learning",
                "abstract": "We investigate the scaling behavior of transformer models across different model sizes and dataset scales in few-shot learning. Our analysis reveals power-law behavior that suggests predictable performance at larger scales.",
                "keywords": ["scaling laws", "few-shot learning", "transformers", "empirical analysis"],
                "claim": "Transformer performance scales predictably with compute budget in few-shot learning",
                "confidence_score": 0.78
            },
            "alignment": {
                "title": "Constitutional AI for Improved AI Alignment",
                "abstract": "We introduce Constitutional AI, a technique for aligning AI systems with human values through self-critique. Experiments show improved safety scores across multiple domains.",
                "keywords": ["AI alignment", "Constitutional AI", "safety", "human values"],
                "claim": "Constitutional AI improves alignment metrics by 25% over baseline approaches",
                "confidence_score": 0.72
            },
            "interpretability": {
                "title": "Mechanistic Analysis of Attention Heads in GPT-style Transformers",
                "abstract": "Through systematic ablation and activation analysis, we identify 8-12 distinct functional roles of attention heads in GPT-style transformers. These findings reveal modular functional organization.",
                "keywords": ["interpretability", "mechanistic analysis", "attention heads", "transformers"],
                "claim": "Attention heads exhibit 8-12 functionally distinct behaviors in GPT-style transformers",
                "confidence_score": 0.81
            },
            "safety": {
                "title": "Detection and Mitigation of Reward Hacking in Reinforcement Learning Agents",
                "abstract": "We develop methods to detect and mitigate reward hacking in RL agents. Our approach achieves 85% detection rate and reduces reward hacking by 60%.",
                "keywords": ["AI safety", "reward hacking", "RL agents", "detection"],
                "claim": "Reward hacking can be detected with 85% accuracy in RL agents",
                "confidence_score": 0.76
            },
            "capabilities": {
                "title": "Emergent Analogical Reasoning in Large Language Models",
                "abstract": "We document the emergence of analogical reasoning in large language models at the 10B parameter scale. This capability manifests as spontaneous strategy formation and enables novel problem-solving.",
                "keywords": ["emergence", "analogical reasoning", "LLMs", "scaling"],
                "claim": "Analogical reasoning emerges in large language models above 10B parameters",
                "confidence_score": 0.73
            }
        }
        
        claim_data = fallback_claims.get(category, fallback_claims["alignment"])
        claim_data['category'] = category
        return claim_data
    
    def generate_batch(self, count: int = 5, categories: List[str] = None) -> List[Dict]:
        """Generate multiple research claims"""
        if categories is None:
            categories = self.CATEGORIES
        
        claims = []
        for i in range(count):
            category = categories[i % len(categories)]
            claim = self.generate_claim(category)
            claims.append(claim)
        
        return claims


def get_claim_generator() -> ClaimGenerator:
    """Factory function to get a claim generator instance"""
    return ClaimGenerator()
