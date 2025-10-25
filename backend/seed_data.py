#!/usr/bin/env python3
"""
Seed the database with test markets and research problems
"""
import os
import sys
from datetime import datetime, timedelta
import json

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///prediction_market.db'

from app import create_app, db
from app.models import Source, Idea, Market, Agent, User

def init_db():
    """Initialize database and create tables"""
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate
        print("🔄 Dropping existing tables...")
        db.drop_all()
        
        print("📦 Creating new tables...")
        db.create_all()
        
        print("✅ Database initialized successfully!")
        return app

def seed_data():
    """Add test data to the database"""
    app = init_db()
    
    with app.app_context():
        print("\n🌱 Seeding test data...")
        
        # Create a default source
        source = Source(
            name="arXiv AI Safety",
            url="https://arxiv.org/list/cs.AI/recent",
            type="arxiv",
            last_scraped=datetime.utcnow()
        )
        db.session.add(source)
        db.session.commit()
        print(f"✓ Created source: {source.name}")
        
        # Create test research ideas/problems
        ideas_data = [
            {
                "title": "Scalable Oversight for Language Models via Debate",
                "abstract": "We propose using AI debate as a method for scalable oversight of language models. Two AI systems argue for competing answers, and a human judge determines the winner. This could help humans supervise AI systems that are smarter than they are.",
                "keywords": "alignment, debate, scalable oversight, language models",
                "extracted_claim": "AI debate can enable effective oversight of superhuman AI systems",
                "confidence_score": 0.75
            },
            {
                "title": "Mechanistic Interpretability of Transformer Attention Heads",
                "abstract": "We investigate the internal mechanisms of transformer attention heads through systematic ablation studies. Our findings reveal specialized attention patterns for different linguistic phenomena, suggesting modular structure in language models.",
                "keywords": "interpretability, transformers, attention, mechanistic analysis",
                "extracted_claim": "Transformer attention heads exhibit specialized, interpretable behavior",
                "confidence_score": 0.82
            },
            {
                "title": "Constitutional AI: Training Harmless Language Models",
                "abstract": "We present Constitutional AI (CAI), a method for training AI systems to be helpful, harmless, and honest through self-critique and revision according to a set of principles. This approach reduces harmful outputs without sacrificing model capabilities.",
                "keywords": "alignment, safety, RLHF, constitutional AI, harmlessness",
                "extracted_claim": "Constitutional AI can reduce harmful outputs while maintaining capabilities",
                "confidence_score": 0.88
            },
            {
                "title": "Emergent Abilities in Large Language Models",
                "abstract": "We document emergent abilities in large language models - capabilities that arise unpredictably at certain scales. These include few-shot learning, arithmetic, and logical reasoning that appear suddenly rather than gradually.",
                "keywords": "scaling, emergence, capabilities, large language models",
                "extracted_claim": "Large language models exhibit emergent abilities at sufficient scale",
                "confidence_score": 0.79
            },
            {
                "title": "Adversarial Training for Neural Network Robustness",
                "abstract": "We demonstrate that adversarial training significantly improves neural network robustness against adversarial examples. Networks trained on adversarial examples show 40% improvement in worst-case accuracy on standard benchmarks.",
                "keywords": "adversarial examples, robustness, adversarial training, security",
                "extracted_claim": "Adversarial training improves neural network robustness by 40%",
                "confidence_score": 0.91
            },
            {
                "title": "Reward Hacking in Reinforcement Learning Agents",
                "abstract": "We identify systematic reward hacking behaviors in RL agents when optimization pressure is high. Agents exploit specification bugs rather than achieving intended goals, highlighting challenges in reward specification.",
                "keywords": "reinforcement learning, reward hacking, alignment, goal misgeneralization",
                "extracted_claim": "RL agents systematically exploit reward specification bugs under optimization pressure",
                "confidence_score": 0.85
            }
        ]
        
        ideas = []
        for idea_data in ideas_data:
            idea = Idea(
                source_id=source.id,
                title=idea_data["title"],
                abstract=idea_data["abstract"],
                keywords=idea_data["keywords"],  # Store as string for SQLite
                extracted_claim=idea_data["extracted_claim"],
                confidence_score=idea_data["confidence_score"],
                created_at=datetime.utcnow()
            )
            db.session.add(idea)
            ideas.append(idea)
        
        db.session.commit()
        print(f"✓ Created {len(ideas)} research ideas")
        
        # Create prediction markets for these ideas
        markets_data = [
            {
                "idea_idx": 0,
                "question_text": "Will AI debate systems demonstrate scalable oversight capabilities in a benchmark evaluation by 2026?",
                "outcomes": ["Yes", "No"],
                "resolution_rule": {
                    "description": "This market will resolve YES if a peer-reviewed publication demonstrates that AI debate systems can effectively enable human oversight of AI systems performing tasks beyond human expert capability, as measured by blind evaluation.",
                    "criteria": [
                        "Publication in a top-tier AI/ML venue (NeurIPS, ICML, ICLR, Nature, Science)",
                        "Demonstrates debate enabling oversight on tasks humans cannot solve alone",
                        "Includes quantitative benchmarks showing improved accuracy",
                        "Results validated by independent reviewers"
                    ],
                    "source": "Academic publications and conference proceedings",
                    "deadline": "2026-12-31"
                },
                "status": "active"
            },
            {
                "idea_idx": 1,
                "question_text": "Will mechanistic interpretability reveal >10 distinct attention head types in GPT-style models?",
                "outcomes": ["Yes", "No"],
                "resolution_rule": {
                    "description": "This market resolves YES if researchers identify and document more than 10 functionally distinct attention head types in transformer language models through mechanistic analysis.",
                    "criteria": [
                        "Peer-reviewed paper with systematic categorization of attention heads",
                        "Clear functional distinctions between identified types",
                        "Analysis on models with >1B parameters",
                        "Reproducible methodology and results"
                    ],
                    "source": "Peer-reviewed ML interpretability research",
                    "deadline": "2025-12-31"
                },
                "status": "active"
            },
            {
                "idea_idx": 2,
                "question_text": "Will Constitutional AI methods be adopted by at least 3 major AI labs by end of 2025?",
                "outcomes": ["0-1 labs", "2 labs", "3+ labs"],
                "resolution_rule": {
                    "description": "Resolution based on public announcements, papers, or model cards from major AI labs (OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft Research) indicating use of Constitutional AI or similar principle-based training methods.",
                    "criteria": [
                        "Official announcement or publication from the lab",
                        "Clear description of Constitutional AI or analogous methodology",
                        "Used in production models or major research releases",
                        "Verification through model cards or technical reports"
                    ],
                    "source": "Official lab announcements and publications",
                    "deadline": "2025-12-31"
                },
                "status": "active"
            },
            {
                "idea_idx": 3,
                "question_text": "Will GPT-5 or equivalent (>10T params) show new emergent abilities not present in GPT-4?",
                "outcomes": ["Yes", "No", "Unclear"],
                "resolution_rule": {
                    "description": "Resolves YES if GPT-5 or a comparable model demonstrates qualitatively new capabilities not present in GPT-4, as documented in evaluation benchmarks or research papers.",
                    "criteria": [
                        "Model has >10 trillion parameters or equivalent compute",
                        "Demonstrates abilities not present in GPT-4 class models",
                        "Abilities emerge suddenly rather than scaling gradually",
                        "Verified through standardized benchmarks"
                    ],
                    "source": "OpenAI publications and third-party evaluations",
                    "deadline": "2026-06-30"
                },
                "status": "active"
            },
            {
                "idea_idx": 4,
                "question_text": "What improvement in adversarial robustness will state-of-the-art achieve by 2026?",
                "outcomes": ["<30%", "30-50%", "50-70%", ">70%"],
                "resolution_rule": {
                    "description": "Resolves based on the best published adversarial robustness accuracy on ImageNet under AutoAttack or equivalent strong attacks, compared to 2023 baseline.",
                    "criteria": [
                        "Published results on standard ImageNet-1k dataset",
                        "Evaluated using AutoAttack or comparably strong adversarial attacks",
                        "Peer-reviewed or on major preprint servers",
                        "Improvement measured against 2023 SOTA baseline"
                    ],
                    "source": "RobustBench leaderboard and peer-reviewed publications",
                    "deadline": "2026-12-31"
                },
                "status": "active"
            },
            {
                "idea_idx": 5,
                "question_text": "Will a major RL deployment experience reward hacking in production by end of 2025?",
                "outcomes": ["Yes", "No"],
                "resolution_rule": {
                    "description": "Resolves YES if a major production deployment of reinforcement learning experiences and publicly reports a significant reward hacking incident.",
                    "criteria": [
                        "Public incident report from a major tech company or AI lab",
                        "Academic case study documenting the incident",
                        "Clear evidence of reward specification exploitation",
                        "Impact on real-world deployment confirmed"
                    ],
                    "source": "Industry incident reports and academic case studies",
                    "deadline": "2025-12-31"
                },
                "status": "active"
            }
        ]
        
        for market_data in markets_data:
            market = Market(
                idea_id=ideas[market_data["idea_idx"]].id,
                question_text=market_data["question_text"],
                outcomes=json.dumps(market_data["outcomes"]),
                resolution_rule=json.dumps(market_data["resolution_rule"]),
                status=market_data["status"],
                created_at=datetime.utcnow(),
                close_date=datetime.utcnow() + timedelta(days=365)
            )
            db.session.add(market)
        
        db.session.commit()
        print(f"✓ Created {len(markets_data)} prediction markets")
        
        # Create test AI agents
        agents_data = [
            {
                "name": "Conservative Researcher",
                "agent_type": "researcher",
                "config": json.dumps({
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "strategy": "conservative",
                    "confidence_threshold": 0.8
                }),
                "description": "Cautious agent that only bets on high-confidence predictions"
            },
            {
                "name": "Aggressive Trader",
                "agent_type": "trader",
                "config": json.dumps({
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "strategy": "aggressive",
                    "confidence_threshold": 0.6
                }),
                "description": "Risk-taking agent that makes bold predictions"
            },
            {
                "name": "Balanced Analyst",
                "agent_type": "analyst",
                "config": json.dumps({
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "strategy": "balanced",
                    "confidence_threshold": 0.7
                }),
                "description": "Balanced agent that weighs multiple perspectives"
            }
        ]
        
        for agent_data in agents_data:
            agent = Agent(
                name=agent_data["name"],
                agent_type=agent_data["agent_type"],
                config=agent_data["config"],
                description=agent_data["description"],
                balance=1000.0,  # Starting balance
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(agent)
        
        db.session.commit()
        print(f"✓ Created {len(agents_data)} AI agents")
        
        print("\n✅ Database seeded successfully!")
        print("\n📊 Summary:")
        print(f"   - {len(ideas)} research ideas")
        print(f"   - {len(markets_data)} prediction markets")
        print(f"   - {len(agents_data)} AI agents")
        print("\n🌐 Visit http://localhost:3000 to see the markets!")

if __name__ == '__main__':
    try:
        seed_data()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

