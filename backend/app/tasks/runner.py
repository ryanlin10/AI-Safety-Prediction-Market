"""
Sandboxed code execution runner
Executes Python code in isolated Docker container with resource limits
"""
import subprocess
import tempfile
import os
import shutil
from datetime import datetime
from app import db
from app.models import Run
import time


def execute_run_sync(run_id: int):
    """
    Execute a run synchronously in a sandboxed environment
    This is a simplified version that runs Python directly with restrictions
    In production, this would use Docker containers
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        run = Run.query.get(run_id)
        if not run:
            return
        
        workspace = run.workspace
        
        try:
            run.status = 'running'
            run.started_at = datetime.utcnow()
            db.session.commit()
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write workspace files to temp directory
                for file_path, content in workspace.files.items():
                    full_path = os.path.join(temp_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                
                # Execute main.py with resource limits
                main_py = os.path.join(temp_dir, 'main.py')
                
                if not os.path.exists(main_py):
                    raise Exception("main.py not found in workspace")
                
                # Run with timeout and resource limits
                # Note: This is a simplified version. Production should use Docker.
                try:
                    result = subprocess.run(
                        ['python3', main_py],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,  # 30 second timeout
                        env={
                            'PYTHONPATH': temp_dir,
                            'HOME': temp_dir,
                            # Restrict environment
                        }
                    )
                    
                    run.stdout = result.stdout
                    run.stderr = result.stderr
                    run.exit_code = result.returncode
                    run.status = 'completed' if result.returncode == 0 else 'failed'
                    
                except subprocess.TimeoutExpired:
                    run.stdout = ''
                    run.stderr = 'Execution timeout (30 seconds exceeded)'
                    run.exit_code = -1
                    run.status = 'failed'
                
                except Exception as e:
                    run.stdout = ''
                    run.stderr = f'Execution error: {str(e)}'
                    run.exit_code = -1
                    run.status = 'failed'
        
        except Exception as e:
            run.status = 'failed'
            run.stderr = f'Runner error: {str(e)}'
            run.exit_code = -1
        
        finally:
            run.finished_at = datetime.utcnow()
            db.session.commit()


def execute_run_docker(run_id: int):
    """
    Execute a run in Docker container (production-ready version)
    This provides better isolation with --network=none and resource limits
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        run = Run.query.get(run_id)
        if not run:
            return
        
        workspace = run.workspace
        
        try:
            run.status = 'running'
            run.started_at = datetime.utcnow()
            db.session.commit()
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write workspace files
                for file_path, content in workspace.files.items():
                    full_path = os.path.join(temp_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                
                # Execute in Docker container
                docker_cmd = [
                    'docker', 'run',
                    '--rm',
                    '--network=none',  # No network access
                    '--memory=1g',      # 1GB memory limit
                    '--cpus=0.5',       # 0.5 CPU limit
                    '--read-only',      # Read-only filesystem
                    '--tmpfs', '/tmp:rw,noexec,nosuid,size=100m',  # Limited temp
                    '-v', f'{temp_dir}:/workspace:ro',  # Mount workspace read-only
                    '-w', '/workspace',
                    '--user', 'nobody',  # Run as unprivileged user
                    'python:3.11-slim',  # Python image
                    'python3', 'main.py'
                ]
                
                try:
                    result = subprocess.run(
                        docker_cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    run.stdout = result.stdout
                    run.stderr = result.stderr
                    run.exit_code = result.returncode
                    run.status = 'completed' if result.returncode == 0 else 'failed'
                    
                except subprocess.TimeoutExpired:
                    # Kill the container if it times out
                    run.stdout = ''
                    run.stderr = 'Execution timeout (30 seconds exceeded)'
                    run.exit_code = -1
                    run.status = 'failed'
                
                except Exception as e:
                    run.stdout = ''
                    run.stderr = f'Docker execution error: {str(e)}'
                    run.exit_code = -1
                    run.status = 'failed'
        
        except Exception as e:
            run.status = 'failed'
            run.stderr = f'Runner error: {str(e)}'
            run.exit_code = -1
        
        finally:
            run.finished_at = datetime.utcnow()
            db.session.commit()

