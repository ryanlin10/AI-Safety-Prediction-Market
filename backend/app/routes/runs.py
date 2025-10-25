from flask import Blueprint, request, jsonify
from app import db
from app.models import Run, Workspace
from app.security.scanner import validate_workspace, get_code_hash
from datetime import datetime

# Blueprint for workspace-related run operations
bp = Blueprint('runs', __name__, url_prefix='/api/workspaces')

# Separate blueprint for standalone run operations
runs_bp = Blueprint('runs_standalone', __name__, url_prefix='/api/runs')


@bp.post('/<int:workspace_id>/run')
def start_run(workspace_id):
    """
    Start a new run for the workspace
    Validates security, creates run record, and enqueues execution
    """
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Security check: validate workspace files
    is_safe, violations = validate_workspace(workspace.files)
    
    if not is_safe:
        return jsonify({
            'error': 'Security check failed',
            'violations': violations
        }), 400
    
    # Create code snapshot hash
    main_code = workspace.files.get('main.py', '')
    code_hash = get_code_hash(main_code)
    
    # Create run record
    run = Run(
        workspace_id=workspace_id,
        code_hash=code_hash,
        status='queued'
    )
    
    db.session.add(run)
    db.session.commit()
    
    # TODO: Enqueue Celery task for execution
    # For now, we'll import and call directly (will add Celery later)
    try:
        from app.tasks.runner import execute_run_sync
        execute_run_sync(run.id)
    except Exception as e:
        run.status = 'failed'
        run.stderr = str(e)
        run.finished_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {
            'run_id': run.id,
            'status': run.status
        }
    }), 202


@bp.get('/<int:workspace_id>/run/<int:run_id>')
def get_run_status(workspace_id, run_id):
    """Get the status and output of a run"""
    run = Run.query.get_or_404(run_id)
    
    if run.workspace_id != workspace_id:
        return jsonify({'error': 'Run does not belong to this workspace'}), 404
    
    return jsonify({
        'success': True,
        'data': run.to_dict()
    })


@runs_bp.get('/<int:run_id>')
def get_run(run_id):
    """Get a specific run by ID"""
    run = Run.query.get_or_404(run_id)
    return jsonify({
        'success': True,
        'data': run.to_dict()
    })

