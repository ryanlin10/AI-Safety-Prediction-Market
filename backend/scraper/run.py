#!/usr/bin/env python3
"""
Scraper runner script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from scraper.arxiv_scraper import run_scraper
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run the arXiv scraper')
    parser.add_argument('--seed', action='store_true', help='Seed initial data')
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.seed:
            print("Seeding database with initial data...")
            seed_database()
        
        print("Running arXiv scraper...")
        result = run_scraper(app.config)
        print(f"Scraped {result['count']} new papers")
        
        for idea in result['ideas']:
            print(f"  - {idea['title'][:80]}...")

def seed_database():
    """Seed database with initial data"""
    from app.models import Agent
    
    # Create default bettor agent
    bettor = Agent.query.filter_by(name='Default Bettor').first()
    if not bettor:
        bettor = Agent(
            name='Default Bettor',
            type='bettor',
            meta={
                'model': 'gpt-4',
                'temperature': 0.7
            }
        )
        db.session.add(bettor)
        print("Created default bettor agent")
    
    # Create default researcher agent
    researcher = Agent.query.filter_by(name='Default Researcher').first()
    if not researcher:
        researcher = Agent(
            name='Default Researcher',
            type='researcher',
            meta={
                'max_epochs': 2,
                'timeout_minutes': 10
            }
        )
        db.session.add(researcher)
        print("Created default researcher agent")
    
    db.session.commit()

if __name__ == '__main__':
    main()

