import React, { useState, useEffect, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { api } from '../api/client';
import './CodeIDE.css';

interface CodeIDEProps {
  workspaceId: number;
  onClose: () => void;
  onRunComplete?: (run: any) => void;
}

const CodeIDE: React.FC<CodeIDEProps> = ({ workspaceId, onClose, onRunComplete }) => {
  const [files, setFiles] = useState<{ [path: string]: string }>({ 'main.py': '# Loading...' });
  const [currentFile, setCurrentFile] = useState<string>('main.py');
  const [currentContent, setCurrentContent] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [runOutput, setRunOutput] = useState<string>('');
  const [runError, setRunError] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [showNewFileInput, setShowNewFileInput] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string>('');
  const [isAIGenerated, setIsAIGenerated] = useState(false);

  // Load workspace function with useCallback to prevent infinite loops
  const loadWorkspace = useCallback(async () => {
    setIsLoading(true);
    setLoadError('');
    try {
      console.log('Loading workspace:', workspaceId);
      const response = await api.getWorkspace(workspaceId);
      console.log('Workspace loaded:', response.data);
      // Backend returns { success: true, data: { files: {...} } }
      const workspaceData = response.data.data || response.data;
      const workspaceFiles = workspaceData.files || { 'main.py': '# Write your code here\n' };
      setFiles(workspaceFiles);
      
      // Check if this is AI-generated code
      const mainPy = workspaceFiles['main.py'] || '';
      if (mainPy.includes('AI') || mainPy.includes('generated') || mainPy.length > 500) {
        setIsAIGenerated(true);
      }
      
      // Load first file
      const firstFile = Object.keys(workspaceFiles)[0] || 'main.py';
      setCurrentFile(firstFile);
      setCurrentContent(workspaceFiles[firstFile] || '');
      setIsLoading(false);
    } catch (error: any) {
      console.error('Error loading workspace:', error);
      const errorMsg = error?.response?.data?.error || error?.message || 'Unknown error';
      setLoadError('Failed to load workspace: ' + errorMsg);
      setIsLoading(false);
    }
  }, [workspaceId]);

  // Load workspace files on mount
  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  // Load current file content when switching files
  useEffect(() => {
    if (files[currentFile]) {
      setCurrentContent(files[currentFile]);
    }
  }, [currentFile, files]);


  const saveFile = async () => {
    setIsSaving(true);
    try {
      await api.saveFile(workspaceId, currentFile, currentContent);
      setFiles(prev => ({ ...prev, [currentFile]: currentContent }));
      setRunOutput(prev => prev + `\n✅ Saved ${currentFile}`);
    } catch (error) {
      console.error('Error saving file:', error);
      setRunError('Failed to save file');
    } finally {
      setIsSaving(false);
    }
  };

  const createNewFile = async () => {
    if (!newFileName || !newFileName.endsWith('.py')) {
      alert('File name must end with .py');
      return;
    }

    if (files[newFileName]) {
      alert('File already exists');
      return;
    }

    const newContent = '# New file\n';
    setFiles(prev => ({ ...prev, [newFileName]: newContent }));
    setCurrentFile(newFileName);
    setCurrentContent(newContent);
    setShowNewFileInput(false);
    setNewFileName('');

    // Save to backend
    try {
      await api.saveFile(workspaceId, newFileName, newContent);
    } catch (error) {
      console.error('Error creating file:', error);
    }
  };

  const runCode = async () => {
    // Save current file first
    await saveFile();

    setIsRunning(true);
    setRunOutput('🚀 Starting execution...\n');
    setRunError('');

    try {
      const response = await api.runWorkspace(workspaceId);
      console.log('Run response:', response);
      // Response structure: { data: { success: true, data: { run_id: X, status: ... } } }
      const runId = response.data?.data?.run_id || response.data?.run_id;
      console.log('Extracted run ID:', runId);

      if (!runId) {
        throw new Error('No run ID returned from server');
      }

      // Poll for run status
      pollRunStatus(runId);
    } catch (error: any) {
      console.error('Error running code:', error);
      if (error.response?.data?.violations) {
        setRunError('Security check failed:\n' + error.response.data.violations.join('\n'));
      } else {
        setRunError('Failed to start execution: ' + (error.response?.data?.error || error.message));
      }
      setIsRunning(false);
    }
  };

  const pollRunStatus = async (runId: number) => {
    const maxAttempts = 60; // 60 seconds timeout
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await api.getRunStatus(runId);
        console.log('Run status response:', response);
        const run = response.data?.data || response.data;

        if (run.status === 'completed' || run.status === 'failed') {
          setIsRunning(false);
          
          if (run.stdout) {
            setRunOutput(prev => prev + '\n📤 OUTPUT:\n' + run.stdout);
          }
          
          if (run.stderr) {
            setRunError(run.stderr);
          }

          if (run.status === 'completed') {
            setRunOutput(prev => prev + '\n✅ Execution completed successfully');
          } else {
            setRunOutput(prev => prev + '\n❌ Execution failed');
          }

          if (onRunComplete) {
            onRunComplete(run);
          }
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 1000); // Poll every second
        } else {
          setIsRunning(false);
          setRunError('Execution timeout - check if process is stuck');
        }
      } catch (error) {
        console.error('Error polling run status:', error);
        setIsRunning(false);
        setRunError('Failed to get run status');
      }
    };

    poll();
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="code-ide">
        <div className="ide-header">
          <h2>🖥️ Code Workspace</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: 'calc(100vh - 60px)',
          color: '#cccccc',
          fontSize: '18px'
        }}>
          ⚙️ Loading workspace...
        </div>
      </div>
    );
  }

  // Show error state
  if (loadError) {
    return (
      <div className="code-ide">
        <div className="ide-header">
          <h2>🖥️ Code Workspace</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          height: 'calc(100vh - 60px)',
          color: '#f48771',
          padding: '40px'
        }}>
          <h3>❌ Error Loading Workspace</h3>
          <p>{loadError}</p>
          <button onClick={onClose} style={{ marginTop: '20px', padding: '10px 20px' }}>
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="code-ide">
      <div className="ide-header">
        <h2>
          {isAIGenerated ? '🤖 AI-Generated Test Code' : '🖥️ Code Workspace'}
          {' '}(ID: {workspaceId})
        </h2>
        <button onClick={onClose} className="close-btn">✕</button>
      </div>
      
      {isAIGenerated && (
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '12px 20px',
          fontSize: '14px',
          borderBottom: '1px solid #3e3e42'
        }}>
          ✨ This code was automatically generated by AI to test the hypothesis. Review, modify if needed, and click "Run" to execute.
        </div>
      )}

      <div className="ide-container">
        {/* File Tree */}
        <div className="file-tree">
          <div className="file-tree-header">
            <h3>Files</h3>
            <button 
              onClick={() => setShowNewFileInput(!showNewFileInput)}
              className="new-file-btn"
              title="New File"
            >
              +
            </button>
          </div>

          {showNewFileInput && (
            <div className="new-file-input">
              <input
                type="text"
                placeholder="filename.py"
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createNewFile()}
              />
              <button onClick={createNewFile}>Create</button>
            </div>
          )}

          <div className="file-list">
            {Object.keys(files).map((filePath) => (
              <div
                key={filePath}
                className={`file-item ${currentFile === filePath ? 'active' : ''}`}
                onClick={() => setCurrentFile(filePath)}
              >
                📄 {filePath}
              </div>
            ))}
          </div>
        </div>

        {/* Editor */}
        <div className="editor-panel">
          <div className="editor-toolbar">
            <span className="current-file-name">{currentFile}</span>
            <div className="editor-actions">
              <button 
                onClick={saveFile} 
                disabled={isSaving}
                className="save-btn"
              >
                {isSaving ? '⏳ Saving...' : '💾 Save'}
              </button>
              <button 
                onClick={runCode} 
                disabled={isRunning}
                className="run-btn"
              >
                {isRunning ? '⚙️ Running...' : '▶️ Run'}
              </button>
            </div>
          </div>

          <div className="editor-wrapper">
            <Editor
              height="100%"
              language="python"
              value={currentContent}
              onChange={(value) => setCurrentContent(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                automaticLayout: true,
              }}
            />
          </div>
        </div>

        {/* Output Console */}
        <div className="console-panel">
          <div className="console-header">
            <h3>Console</h3>
            <button 
              onClick={() => { setRunOutput(''); setRunError(''); }}
              className="clear-console-btn"
            >
              Clear
            </button>
          </div>
          <div className="console-content">
            {runOutput && (
              <pre className="console-output">{runOutput}</pre>
            )}
            {runError && (
              <pre className="console-error">{runError}</pre>
            )}
            {!runOutput && !runError && (
              <div className="console-placeholder">
                Click "Run" to execute your code. Output will appear here.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeIDE;

