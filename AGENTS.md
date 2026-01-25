# AGENTS.md - RepoToVideo Development Guide

This document provides guidelines for agentic coding tools working in the RepoToVideo codebase.

## 🔧 Build/Lint/Test Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py
```

### Testing
```bash
# Run the main test suite
python test_real_repository.py <github_repo_url>

# Example test with specific repository
python test_real_repository.py https://github.com/TheAlgorithms/Python

# Run tests with custom output directory
python test_real_repository.py https://github.com/user/repo --output my_animations
```

### Running Single Tests
The project uses a single comprehensive test file. To test specific functionality:

```bash
# Test repository fetching
python -c "from repo_fetcher import RepoFetcher; fetcher = RepoFetcher(); print('RepoFetcher imported successfully')"

# Test code analysis
python -c "from code_analysis import EnhancedCodeAnalyzer; print('CodeAnalyzer imported successfully')"

# Test animation system
python -c "from advanced_animation import AdvancedAnimationSystem; print('AnimationSystem imported successfully')"
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run app.py

# Access at http://localhost:8501
```

## 🎨 Code Style Guidelines

### Python Style
- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use descriptive variable and function names
- Add type hints for all functions and methods
- Include docstrings for all classes and public methods

### Imports
```python
# Standard library imports first
import os
import sys
from typing import Dict, List, Any, Optional

# Third-party imports
import numpy as np
import pandas as pd
from pydantic import BaseModel

# Local imports
from .data_structures import Storyboard, StoryboardScene
from ..utils.helpers import format_code
```

### Formatting
- Use snake_case for variables and functions
- Use CamelCase for class names
- Use UPPER_CASE for constants
- Use f-strings for string formatting
- Add spaces around operators and after commas
- Use consistent quotation marks (prefer double quotes for strings)

### Types
- Add type hints to all function parameters and return values
- Use Optional[T] for nullable values
- Use Union types when appropriate
- Use typing.Dict, typing.List, etc. for complex types
- Use Pydantic models for data validation

### Naming Conventions
- **Variables**: `snake_case` (e.g., `file_path`, `code_analysis`)
- **Functions**: `snake_case` with verb prefix (e.g., `generate_storyboard()`, `create_animation()`)
- **Classes**: `PascalCase` (e.g., `StoryboardGenerator`, `AdvancedAnimationSystem`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`, `MAX_RETRIES`)
- **Private methods**: `_prefix` (e.g., `_generate_fallback_storyboard()`)
- **Boolean variables**: `is_` or `has_` prefix (e.g., `is_valid`, `has_error`)

### Error Handling
```python
# Good error handling pattern
def fetch_repository(repo_url: str) -> str:
    """Fetch repository with proper error handling."""
    try:
        # Main logic
        result = subprocess.run(["git", "clone", repo_url], check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e}")
        raise ValueError(f"Repository clone failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("Important operational messages")
logger.warning("Potential issues or warnings")
logger.error("Errors that don't stop execution")
logger.critical("Critical failures")
```

## 📁 Project Structure

```
RepoToVideo/
├── app.py                     # Main Streamlit application
├── repo_fetcher.py            # GitHub repository fetching
├── code_analysis.py           # Enhanced code analysis
├── test_real_repository.py    # Main test suite
├── advanced_animation/        # Advanced animation system
│   ├── core/                  # Core functionality
│   │   ├── data_structures.py # Data classes
│   │   ├── storyboard_generator.py # AI storyboard generation
│   │   └── execution_capture.py # Runtime tracing
│   ├── visualizations/        # Visual components
│   │   └── visual_metaphors.py # Visual metaphor library
│   ├── rendering/             # Rendering components
│   │   └── manim_scene.py     # ManimGL rendering
│   └── audio/                 # Audio generation
│       └── audio_generator.py # Audio processing
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## 🤖 Agent-Specific Rules

### From .never/config.yaml
```yaml
version: 1
rules:
  - core
  - hygiene
  - python
  - security
  - ai-guidelines
  - code-quality
targets:
  cursor: false
  claude: false
  copilot: false
  agents: true
```

### Key Agent Rules
1. **Agents are enabled**: `agents: true`
2. **Follow all core Python rules**: PEP 8, security, code quality
3. **Maintain high hygiene standards**: Clean, readable, maintainable code
4. **Prioritize security**: Never expose secrets or sensitive data
5. **Follow AI guidelines**: Ethical AI usage and data handling

## 🔄 Common Workflows

### Adding New Features
1. Create a new branch: `git checkout -b feature-name`
2. Add tests for the new functionality
3. Implement the feature following existing patterns
4. Run tests to verify: `python test_real_repository.py`
5. Update documentation if needed

### Fixing Bugs
1. Identify the issue through testing or error logs
2. Create a minimal reproduction case
3. Fix the issue with proper error handling
4. Add tests to prevent regression
5. Verify the fix works

### Code Review
1. Check for proper type hints
2. Verify error handling is comprehensive
3. Ensure logging is appropriate
4. Confirm naming conventions are followed
5. Validate imports are organized correctly

## 🚫 Prohibited Practices

- **Never commit API keys or secrets**
- **Don't use `*` imports** (always import explicitly)
- **Avoid global variables** (use class attributes or config)
- **Don't suppress exceptions silently** (always log or handle)
- **Avoid complex nested functions** (keep functions focused)
- **Don't use magic numbers** (define as constants)
- **Avoid long functions** (break into smaller, focused functions)

## 📚 Documentation Standards

### Docstrings
```python
"""
Module-level docstring explaining the purpose and main functionality.

This should be a complete sentence describing what the module does.
"""

class ExampleClass:
    """
    Class docstring explaining purpose and usage.
    
    Attributes:
        attribute1 (type): Description of attribute1
        attribute2 (type): Description of attribute2
    """
    
    def example_method(self, param1: str, param2: int) -> bool:
        """
        Method docstring explaining purpose, parameters, and return value.
        
        Args:
            param1 (str): Description of param1
            param2 (int): Description of param2
            
        Returns:
            bool: Description of return value
            
        Raises:
            ValueError: If param2 is negative
        """
        # Method implementation
```

### Comments
- Use inline comments sparingly (code should be self-documenting)
- Use comments to explain "why" not "what"
- Keep comments up-to-date with code changes
- Use TODO comments for future improvements

## 🎯 Best Practices

### Performance
- Use list comprehensions instead of loops when possible
- Cache expensive operations
- Use generators for large datasets
- Profile before optimizing

### Security
- Validate all external inputs
- Use environment variables for secrets
- Implement proper error handling
- Follow principle of least privilege

### Testing
- Write tests for new functionality
- Test edge cases and error conditions
- Keep tests focused and fast
- Use descriptive test names

### Collaboration
- Use feature branches for development
- Write clear commit messages
- Review code before merging
- Update documentation with changes

## 🔧 Tool Configuration

### Recommended VSCode Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.pylint",
    "ms-python.debugpy",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### Recommended Settings
```json
{
  "python.formatting.provider": "black",
  "python.linting.pylintEnabled": true,
  "python.linting.enabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "python.analysis.typeCheckingMode": "basic"
}
```

## 📋 Checklist for New Code

- [ ] Follows PEP 8 style guidelines
- [ ] Includes proper type hints
- [ ] Has comprehensive docstrings
- [ ] Includes appropriate error handling
- [ ] Uses proper logging
- [ ] Follows naming conventions
- [ ] Has tests for new functionality
- [ ] Doesn't expose secrets
- [ ] Maintains security best practices
- [ ] Is properly documented

## 🔍 Current Status

### Video Rendering
- ⚠️ MoviePy imports fixed, ready for testing
- ⚠️ Manim Rendering: Still needs proper ManimGL setup

## 🧪 Testing Instructions

To verify the current state of the project:

```bash
# Test MoviePy video rendering
python -c "from moviepy.editor import VideoClip; print('MoviePy imports working')"

# Test ManimGL rendering (may fail if not properly configured)
python -c "from manim import Scene; print('ManimGL imports working')"

# Run full test suite
python test_real_repository.py https://github.com/TheAlgorithms/Python
```

This guide ensures consistency and quality across the RepoToVideo codebase for all contributors, including agentic coding tools.