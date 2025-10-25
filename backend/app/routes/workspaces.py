from flask import Blueprint, request, jsonify
from app import db
from app.models import Workspace, Investigation
import hashlib
from datetime import datetime
from app.services.code_generator import generate_test_code

bp = Blueprint('workspaces', __name__, url_prefix='/api/workspaces')

@bp.post('')
def create_workspace():
    """Create a new workspace with optional AI code generation"""
    data = request.get_json()
    
    # Check if AI code generation is requested
    generate_ai_code = data.get('generate_ai_code', False)
    files = data.get('files', {'main.py': '# Write your code here\n'})
    explanation = None
    
    if generate_ai_code and data.get('investigation_id'):
        # Get investigation details
        investigation_id = data.get('investigation_id')
        investigation = Investigation.query.get(investigation_id)
        
        if investigation and investigation.idea:
            try:
                # Generate AI code
                investigation_data = {
                    'hypothesis': investigation.idea.extracted_claim or investigation.idea.title,
                    'formalized_claim': investigation.formalized_claim or investigation.idea.extracted_claim,
                    'context': investigation.idea.abstract or ''
                }
                
                result = generate_test_code(investigation_data)
                files = {'main.py': result['main_py']}
                explanation = result['explanation']
                
            except Exception as e:
                # If AI generation fails, use template
                print(f"AI code generation failed: {e}")
                explanation = f"AI generation failed: {str(e)}. Using template."
    
    workspace = Workspace(
        investigation_id=data.get('investigation_id'),
        agent_id=data.get('agent_id'),
        name=data.get('name', 'Untitled Workspace'),
        description=data.get('description', ''),
        files=files
    )
    
    db.session.add(workspace)
    db.session.commit()
    
    response_data = workspace.to_dict()
    if explanation:
        response_data['explanation'] = explanation
    
    return jsonify({'success': True, 'data': response_data}), 201


@bp.get('/<int:workspace_id>')
def get_workspace(workspace_id):
    """Get workspace details"""
    workspace = Workspace.query.get_or_404(workspace_id)
    return jsonify({'success': True, 'data': workspace.to_dict()})


@bp.get('/<int:workspace_id>/files')
def list_files(workspace_id):
    """List all files in workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    files = workspace.files
    
    file_list = [
        {'path': path, 'size': len(content)}
        for path, content in files.items()
    ]
    
    return jsonify({'success': True, 'data': {'files': file_list}})


@bp.get('/<int:workspace_id>/file/<path:file_path>')
def get_file(workspace_id, file_path):
    """Get a specific file content"""
    workspace = Workspace.query.get_or_404(workspace_id)
    files = workspace.files
    
    if file_path not in files:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'path': file_path,
            'content': files[file_path]
        }
    })


@bp.post('/<int:workspace_id>/file/<path:file_path>')
def save_file(workspace_id, file_path):
    """Save or update a file"""
    workspace = Workspace.query.get_or_404(workspace_id)
    data = request.get_json()
    
    content = data.get('content', '')
    files = workspace.files
    files[file_path] = content
    workspace.files = files
    workspace.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'data': {'path': file_path}})


@bp.delete('/<int:workspace_id>/file/<path:file_path>')
def delete_file(workspace_id, file_path):
    """Delete a file"""
    workspace = Workspace.query.get_or_404(workspace_id)
    files = workspace.files
    
    if file_path not in files:
        return jsonify({'error': 'File not found'}), 404
    
    del files[file_path]
    workspace.files = files
    workspace.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})


@bp.get('/<int:workspace_id>/runs')
def get_runs(workspace_id):
    """Get all runs for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    runs = [run.to_dict() for run in workspace.runs]
    
    return jsonify({'success': True, 'data': {'runs': runs}})

