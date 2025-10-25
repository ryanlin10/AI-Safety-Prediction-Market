"""
Research Claim Generator Service
Generates testable research claims for AI safety and alignment research
"""
import random
from typing import List, Dict

class ClaimGenerator:
    """Generate testable research claims"""
    
    # Templates for different research areas
    CLAIM_TEMPLATES = {
        "scalability": [
            {
                "title": "Scaling Laws for {model_type} in {domain}",
                "abstract": "We investigate the scaling behavior of {model_type} across different model sizes and dataset scales in {domain}. Our analysis reveals {finding} that suggests {implication}.",
                "claim": "{model_type} performance scales predictably with {metric} in {domain}",
                "keywords": ["scaling laws", "{domain}", "{model_type}", "empirical analysis"]
            },
            {
                "title": "Efficient {technique} for Large-Scale {application}",
                "abstract": "We propose a novel {technique} approach that reduces computational costs while maintaining performance in {application}. Our method achieves {improvement} compared to baseline approaches.",
                "claim": "{technique} can reduce computational costs by {percentage} in {application}",
                "keywords": ["efficiency", "{technique}", "{application}", "optimization"]
            }
        ],
        "alignment": [
            {
                "title": "{method} for Improved AI Alignment",
                "abstract": "We introduce {method}, a technique for aligning AI systems with human values through {mechanism}. Experiments show {result} across multiple domains.",
                "claim": "{method} improves alignment metrics by {improvement} over baseline approaches",
                "keywords": ["AI alignment", "{method}", "safety", "human values"]
            },
            {
                "title": "Robustness of {approach} Against {threat}",
                "abstract": "We evaluate the robustness of {approach} when faced with {threat}. Our findings indicate {vulnerability_level} and suggest {mitigation}.",
                "claim": "{approach} maintains {performance_metric} under {threat} conditions",
                "keywords": ["robustness", "{approach}", "{threat}", "adversarial"]
            }
        ],
        "interpretability": [
            {
                "title": "Mechanistic Analysis of {component} in {model}",
                "abstract": "Through systematic ablation and activation analysis, we identify {number} distinct functional roles of {component} in {model}. These findings reveal {insight}.",
                "claim": "{component} exhibits {number} functionally distinct behaviors in {model}",
                "keywords": ["interpretability", "mechanistic analysis", "{component}", "{model}"]
            },
            {
                "title": "Causal Tracing of {behavior} in Language Models",
                "abstract": "We apply causal intervention techniques to trace the computational pathway responsible for {behavior}. Results show {finding} concentrated in {location}.",
                "claim": "{behavior} emerges from computations in {location} of the model",
                "keywords": ["causal analysis", "interpretability", "{behavior}", "tracing"]
            }
        ],
        "safety": [
            {
                "title": "Detection and Mitigation of {risk} in {system}",
                "abstract": "We develop methods to detect and mitigate {risk} in {system}. Our approach achieves {accuracy} detection rate and reduces {risk} by {percentage}.",
                "claim": "{risk} can be detected with {accuracy} accuracy in {system}",
                "keywords": ["AI safety", "{risk}", "{system}", "detection"]
            },
            {
                "title": "Red Teaming {model} for {vulnerability}",
                "abstract": "Through systematic red teaming, we discover {finding} related to {vulnerability} in {model}. We propose {solution} to address these issues.",
                "claim": "{model} exhibits {vulnerability} under {condition} stress testing",
                "keywords": ["red teaming", "safety", "{vulnerability}", "{model}"]
            }
        ],
        "capabilities": [
            {
                "title": "Emergent {capability} in {model_class} Models",
                "abstract": "We document the emergence of {capability} in {model_class} models at the {scale} scale. This capability manifests as {description} and enables {application}.",
                "claim": "{capability} emerges in {model_class} models above {scale} parameters",
                "keywords": ["emergence", "{capability}", "{model_class}", "scaling"]
            },
            {
                "title": "Chain-of-Thought {task} with {model}",
                "abstract": "We evaluate {model}'s ability to perform {task} using chain-of-thought prompting. Results show {performance} compared to {baseline}.",
                "claim": "Chain-of-thought improves {task} performance by {improvement} in {model}",
                "keywords": ["chain-of-thought", "{task}", "{model}", "reasoning"]
            }
        ]
    }
    
    # Substitution options
    SUBSTITUTIONS = {
        "model_type": ["transformer", "diffusion model", "retrieval-augmented model", "multimodal model"],
        "domain": ["few-shot learning", "long-context processing", "multi-task learning", "zero-shot transfer"],
        "finding": ["power-law behavior", "phase transitions", "logarithmic improvements", "emergent capabilities"],
        "implication": ["predictable performance at larger scales", "optimal compute allocation strategies", "architectural improvements"],
        "technique": ["sparse attention", "mixture-of-experts", "knowledge distillation", "quantization"],
        "application": ["language modeling", "image generation", "code synthesis", "reasoning tasks"],
        "improvement": ["3x speedup", "40% reduction in parameters", "2x throughput", "50% memory savings"],
        "percentage": ["30%", "45%", "60%", "75%"],
        "method": ["Constitutional AI", "Recursive Reward Modeling", "Debate-based Oversight", "Value Learning"],
        "mechanism": ["self-critique", "human feedback", "multi-agent debate", "principle-following"],
        "result": ["improved safety scores", "better value alignment", "reduced harmful outputs", "increased coherence"],
        "approach": ["RLHF", "supervised fine-tuning", "adversarial training", "prompt engineering"],
        "threat": ["distribution shift", "adversarial attacks", "jailbreak attempts", "prompt injection"],
        "vulnerability_level": ["moderate robustness", "significant vulnerabilities", "strong resistance", "partial resilience"],
        "mitigation": ["defensive distillation", "input validation", "output filtering", "ensemble methods"],
        "performance_metric": ["75% accuracy", "reliable behavior", "consistent outputs", "safe responses"],
        "component": ["attention heads", "MLP layers", "residual streams", "layer norms"],
        "model": ["GPT-style transformers", "encoder-decoder models", "vision transformers", "multimodal models"],
        "number": ["8-12", "5-7", "10-15", "15-20"],
        "insight": ["modular functional organization", "hierarchical processing", "sparse activation patterns", "interpretable circuits"],
        "behavior": ["in-context learning", "factual recall", "logical reasoning", "arithmetic"],
        "finding": ["causal pathways", "information flow", "computational bottlenecks", "critical neurons"],
        "location": ["middle layers", "attention patterns", "specific heads", "residual connections"],
        "risk": ["reward hacking", "goal misgeneralization", "deceptive alignment", "capability overhang"],
        "system": ["reinforcement learning agents", "language models", "autonomous systems", "recommendation engines"],
        "accuracy": ["85%", "90%", "78%", "92%"],
        "vulnerability": ["prompt injection", "adversarial examples", "distributional shift", "backdoor triggers"],
        "condition": ["adversarial", "out-of-distribution", "high-stakes", "safety-critical"],
        "solution": ["detection mechanisms", "input sanitization", "robust training", "monitoring systems"],
        "capability": ["analogical reasoning", "tool use", "meta-learning", "abstract planning"],
        "model_class": ["large language", "vision-language", "code generation", "multimodal"],
        "scale": ["10B", "100B", "1T", "500B"],
        "description": ["spontaneous strategy formation", "novel problem-solving", "creative synthesis", "transfer learning"],
        "task": ["mathematical reasoning", "logical deduction", "causal inference", "multi-step planning"],
        "model": ["GPT-4", "Claude", "PaLM", "Gemini"],
        "performance": ["significant improvements", "mixed results", "strong performance", "modest gains"],
        "baseline": ["standard prompting", "few-shot learning", "fine-tuned models", "zero-shot approaches"],
        "metric": "compute budget"
    }
    
    def generate_claim(self, category: str = None) -> Dict:
        """Generate a single research claim"""
        if category is None or category not in self.CLAIM_TEMPLATES:
            category = random.choice(list(self.CLAIM_TEMPLATES.keys()))
        
        template = random.choice(self.CLAIM_TEMPLATES[category])
        
        # Fill in template placeholders
        filled = {}
        for key, value in template.items():
            if isinstance(value, str):
                filled_value = value
                # Find all {placeholder} patterns and substitute
                import re
                placeholders = re.findall(r'\{(\w+)\}', value)
                for placeholder in placeholders:
                    if placeholder in self.SUBSTITUTIONS:
                        replacement = random.choice(self.SUBSTITUTIONS[placeholder])
                        filled_value = filled_value.replace(f'{{{placeholder}}}', replacement)
                filled[key] = filled_value
            elif isinstance(value, list):
                # Handle keyword lists
                filled[key] = [
                    item.replace(f'{{{placeholder}}}', random.choice(self.SUBSTITUTIONS.get(placeholder, [placeholder])))
                    for item in value
                    for placeholder in [item[1:-1]] if item.startswith('{') and item.endswith('}')
                ] or value
        
        # Add metadata
        filled['category'] = category
        filled['confidence_score'] = round(random.uniform(0.65, 0.95), 2)
        
        return filled
    
    def generate_batch(self, count: int = 5, categories: List[str] = None) -> List[Dict]:
        """Generate multiple research claims"""
        if categories is None:
            categories = list(self.CLAIM_TEMPLATES.keys())
        
        claims = []
        for i in range(count):
            category = categories[i % len(categories)]
            claim = self.generate_claim(category)
            claims.append(claim)
        
        return claims


def get_claim_generator() -> ClaimGenerator:
    """Factory function to get a claim generator instance"""
    return ClaimGenerator()

