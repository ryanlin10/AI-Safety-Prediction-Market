#!/usr/bin/env python3
"""
Celery worker entry point
"""
from app import create_app, celery

app = create_app()
app.app_context().push()

