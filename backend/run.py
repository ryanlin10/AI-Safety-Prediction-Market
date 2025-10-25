#!/usr/bin/env python3
"""
Main entry point for the Flask application
"""
from app import create_app, db
from app.models import User, Source, Idea, Market, Bet, Agent, Experiment

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Source': Source,
        'Idea': Idea,
        'Market': Market,
        'Bet': Bet,
        'Agent': Agent,
        'Experiment': Experiment
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

