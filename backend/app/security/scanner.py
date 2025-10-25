"""
Security scanner for code execution
Performs static analysis to detect dangerous patterns before execution
"""
import re
from typing import Dict, List, Tuple

# Banned imports and patterns
BANNED_IMPORTS = [
    'os.system', 'subprocess', 'eval', 'exec', 'compile',
    '__import__', 'importlib', 'socket', 'requests', 'urllib',
    'http', 'ftplib', 'telnetlib', 'smtplib',
    'multiprocessing', 'threading', 'asyncio',
    'pickle', 'shelve', 'marshal', 'ctypes',
    'sys.exit', 'sys.setrecursionlimit',
    'open', 'file',  # File I/O (can allow limited read-only)
]

# Allowed imports (whitelist for ML/data science)
ALLOWED_IMPORTS = [
    'numpy', 'pandas', 'scipy', 'sklearn', 'scikit-learn',
    'matplotlib', 'seaborn', 'plotly',
    'torch', 'tensorflow', 'keras', 'jax',
    'transformers', 'datasets',
    'json', 'csv', 'math', 'statistics', 'random',
    'datetime', 'time', 'collections', 'itertools',
    'typing', 'dataclasses', 'enum',
]

# Safe dunder methods (commonly used in normal Python code)
SAFE_DUNDERS = [
    '__name__', '__main__', '__init__', '__str__', '__repr__',
    '__len__', '__iter__', '__next__', '__enter__', '__exit__',
    '__doc__', '__version__', '__author__', '__all__',
    '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__',
    '__add__', '__sub__', '__mul__', '__div__', '__mod__',
    '__getitem__', '__setitem__', '__delitem__', '__contains__',
    '__call__', '__hash__', '__bool__', '__format__',
]

# Dangerous dunder methods (used for introspection/code execution)
DANGEROUS_DUNDERS = [
    r'__import__', r'__builtins__', r'__globals__', r'__code__',
    r'__class__', r'__bases__', r'__subclasses__', r'__dict__',
    r'__loader__', r'__spec__', r'__package__', r'__cached__',
]

# Dangerous function patterns
DANGEROUS_PATTERNS = [
    r'globals\(\)',
    r'locals\(\)',
    r'vars\(\)',
    r'dir\(\)',
    r'getattr',
    r'setattr',
    r'delattr',
    r'\.read\(',
    r'\.write\(',
    r'\.seek\(',
]


def scan_code(code: str) -> Tuple[bool, List[str]]:
    """
    Scan code for security violations
    
    Returns:
        (is_safe, violations) - True if safe, list of violation messages
    """
    violations = []
    
    # Check for banned imports
    for banned in BANNED_IMPORTS:
        pattern = rf'(from\s+{banned.split(".")[0]}|import\s+{banned.split(".")[0]})'
        if re.search(pattern, code):
            violations.append(f"Banned import detected: {banned}")
    
    # Check for dangerous dunder methods
    for dangerous_dunder in DANGEROUS_DUNDERS:
        if re.search(dangerous_dunder, code):
            violations.append(f"Dangerous dunder method detected: {dangerous_dunder}")
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, code, re.MULTILINE)
        if matches:
            violations.append(f"Dangerous pattern detected: {pattern}")
    
    # Check for suspicious eval-like patterns
    if re.search(r'(eval|exec|compile)\s*\(', code):
        violations.append("Dynamic code execution detected (eval/exec/compile)")
    
    # Check for file operations
    if re.search(r'open\s*\(', code):
        violations.append("File I/O detected - this is restricted in sandbox")
    
    # Check for network operations
    network_patterns = ['socket', 'requests', 'urllib', 'http', 'fetch']
    for net_pattern in network_patterns:
        if net_pattern in code.lower():
            violations.append(f"Network operation detected: {net_pattern}")
    
    is_safe = len(violations) == 0
    return is_safe, violations


def get_code_hash(code: str) -> str:
    """Generate hash of code for versioning"""
    import hashlib
    return hashlib.sha256(code.encode()).hexdigest()


def validate_workspace(workspace_files: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate all files in a workspace
    
    Returns:
        (is_safe, violations) - True if all files are safe
    """
    all_violations = []
    
    for file_path, content in workspace_files.items():
        # Only scan Python files
        if file_path.endswith('.py'):
            is_safe, violations = scan_code(content)
            if not is_safe:
                for violation in violations:
                    all_violations.append(f"{file_path}: {violation}")
    
    return len(all_violations) == 0, all_violations

