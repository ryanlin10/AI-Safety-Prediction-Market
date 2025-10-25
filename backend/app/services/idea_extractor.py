import openai
import re
from sentence_transformers import SentenceTransformer

class IdeaExtractor:
    """Extract testable claims from research ideas"""
    
    def __init__(self, config):
        self.config = config
        openai.api_key = config.get('OPENAI_API_KEY')
        self.embedding_model = None
    
    def extract(self, idea):
        """Extract claim, confidence, and embedding from an idea"""
        # Extract claim using LLM
        claim, confidence = self._extract_claim(idea.title, idea.abstract)
        
        # Generate embedding
        embedding = self._generate_embedding(f"{idea.title} {idea.abstract}")
        
        return {
            'claim': claim,
            'confidence': confidence,
            'embedding': embedding
        }
    
    def _extract_claim(self, title, abstract):
        """Use LLM to extract a testable claim"""
        prompt = f"""
Extract a specific, testable claim from this research paper.

Title: {title}
Abstract: {abstract}

The claim should be:
1. Specific and measurable
2. Testable with an experiment
3. Related to AI safety or machine learning
4. Phrased as a clear statement

Also provide a confidence score (0.0-1.0) for how testable this claim is.

Format your response as:
CLAIM: [the extracted claim]
CONFIDENCE: [0.0-1.0]
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting testable claims from research papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            claim_match = re.search(r'CLAIM:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            confidence_match = re.search(r'CONFIDENCE:\s*([\d.]+)', content, re.IGNORECASE)
            
            claim = claim_match.group(1).strip() if claim_match else None
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            return claim, confidence
            
        except Exception as e:
            print(f"Failed to extract claim: {str(e)}")
            # Fallback: use simple heuristics
            return self._extract_claim_heuristic(title, abstract)
    
    def _extract_claim_heuristic(self, title, abstract):
        """Fallback heuristic-based claim extraction"""
        # Look for key phrases
        claim_indicators = [
            'improves', 'reduces', 'achieves', 'outperforms',
            'increases', 'decreases', 'demonstrates', 'shows'
        ]
        
        # Search abstract for sentences with claim indicators
        sentences = abstract.split('.')
        for sentence in sentences:
            for indicator in claim_indicators:
                if indicator in sentence.lower():
                    return sentence.strip(), 0.4
        
        # Fallback to title
        return f"Research explores: {title}", 0.2
    
    def _generate_embedding(self, text):
        """Generate embedding for semantic search"""
        try:
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            
            # Convert to list for JSON serialization
            return embedding.tolist()
            
        except Exception as e:
            print(f"Failed to generate embedding: {str(e)}")
            # Return None if embedding fails
            return None

