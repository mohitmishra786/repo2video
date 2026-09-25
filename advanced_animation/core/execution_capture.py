"""
Runtime Execution Capture

This module captures code execution states using E2B sandbox for dynamic
visualization of algorithm execution traces.
"""

import os
import sys
import logging
import json
import time
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import ast
import inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .data_structures import ExecutionState, ExecutionTrace

# E2B imports
try:
    from e2b import Sandbox
    E2B_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("E2B successfully imported")
except ImportError as e:
    E2B_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"E2B not available: {e}")

logger = logging.getLogger(__name__)

class RuntimeStateCapture:
    """Captures runtime execution states using E2B sandbox."""
    
    def __init__(self, max_execution_time: int = 30):
        """
        Initialize the runtime state capture.
        
        Args:
            max_execution_time: Maximum execution time in seconds
        """
        self.max_execution_time = max_execution_time
        self.state_history = []
        self.debug_mode = True
        
        logger.info(f"RuntimeStateCapture initialized with max execution time: {max_execution_time}s")
    
    def capture_execution(self, code_content: str, language: str = "python") -> ExecutionTrace:
        """
        Capture execution trace of code.
        
        Args:
            code_content: Source code to execute
            language: Programming language of the code
            
        Returns:
            ExecutionTrace object with complete execution history
        """
        try:
            logger.info(f"Starting execution capture for {language} code")
            
            if not E2B_AVAILABLE:
                logger.warning("E2B not available, using simulation")
                return self._simulate_execution_trace(code_content, language)
            
            if language.lower() == "python":
                return self._capture_python_execution(code_content)
            elif language.lower() == "javascript":
                return self._capture_javascript_execution(code_content)
            elif language.lower() == "java":
                return self._capture_java_execution(code_content)
            else:
                logger.warning(f"Language {language} not supported, using simulation")
                return self._simulate_execution_trace(code_content, language)
                
        except Exception as e:
            logger.error(f"Error capturing execution: {e}")
            return self._simulate_execution_trace(code_content, language)
    
    def _capture_python_execution(self, code_content: str) -> ExecutionTrace:
        """Capture Python code execution using E2B."""
        try:
            logger.info("Capturing Python execution with E2B")
            
            # Create instrumented code
            instrumented_code = self._instrument_python_code(code_content)
            
            with Sandbox(template="base") as sandbox:
                # Write the instrumented code
                sandbox.filesystem.write("/main.py", instrumented_code)
                
                # Start execution
                proc = sandbox.process.start("python /main.py")
                
                states = []
                start_time = time.time()
                
                while proc.is_running and (time.time() - start_time) < self.max_execution_time:
                    try:
                        # Read output
                        stdout = proc.stdout.read()
                        stderr = proc.stderr.read()
                        
                        # Get variable states
                        variables = self._get_python_variables(sandbox)
                        
                        # Get call stack
                        call_stack = self._get_python_call_stack(sandbox)
                        
                        # Create state
                        state = ExecutionState(
                            timestamp=time.time() - start_time,
                            line_number=self._get_current_line(sandbox),
                            variables=variables,
                            call_stack=call_stack,
                            stdout=stdout,
                            stderr=stderr
                        )
                        
                        states.append(state)
                        
                        if self.debug_mode:
                            logger.debug(f"Captured state at {state.timestamp}s: {len(variables)} variables")
                        
                        time.sleep(0.1)  # Capture every 100ms
                        
                    except Exception as e:
                        logger.error(f"Error capturing state: {e}")
                        break
                
                # Final state
                if proc.is_running:
                    proc.kill()
                
                total_duration = time.time() - start_time
                
                logger.info(f"Execution capture completed: {len(states)} states, {total_duration:.2f}s")
                
                return ExecutionTrace(
                    code_content=code_content,
                    language="python",
                    states=states,
                    total_duration=total_duration,
                    metadata={
                        "capture_method": "e2b_sandbox",
                        "debug_mode": self.debug_mode
                    }
                )
                
        except Exception as e:
            logger.error(f"Error in Python execution capture: {e}")
            raise
    
    def _instrument_python_code(self, code_content: str) -> str:
        """Add instrumentation to Python code for state capture."""
        try:
            # Parse the code
            tree = ast.parse(code_content)
            
            # Add imports for instrumentation
            imports = [
                "import sys",
                "import time",
                "import json",
                "import traceback",
                "import os"
            ]
            
            # Create instrumentation code
            instrumented_code = "\n".join(imports) + "\n\n"
            instrumented_code += """
# State capture setup
def capture_state():
    state = {
        'timestamp': time.time(),
        'line_number': sys._getframe().f_lineno,
        'variables': {},
        'call_stack': [frame.f_code.co_name for frame in traceback.extract_stack()],
        'stdout': '',
        'stderr': ''
    }
    
    # Capture local variables
    frame = sys._getframe(1)
    if frame:
        state['variables'] = {
            k: str(v) if not isinstance(v, (int, float, str, bool, list, dict)) else v
            for k, v in frame.f_locals.items()
            if not k.startswith('_')
        }
    
    # Write state to file
    with open('/tmp/execution_state.json', 'w') as f:
        json.dump(state, f)
    
    return state

# Original code follows:
"""
            instrumented_code += code_content
            
            # Add state capture calls at key points
            lines = instrumented_code.split('\n')
            instrumented_lines = []
            
            for i, line in enumerate(lines):
                instrumented_lines.append(line)
                
                # Add state capture after function definitions and loops
                if line.strip().startswith('def ') or line.strip().startswith('for ') or line.strip().startswith('while '):
                    instrumented_lines.append("    capture_state()")
            
            return '\n'.join(instrumented_lines)
            
        except Exception as e:
            logger.error(f"Error instrumenting Python code: {e}")
            return code_content
    
    def _get_python_variables(self, sandbox) -> Dict[str, Any]:
        """Get variable states from Python execution."""
        try:
            # Try to read state file
            try:
                state_file = sandbox.filesystem.read("/tmp/execution_state.json")
                state_data = json.loads(state_file)
                return state_data.get('variables', {})
            except:
                # Fallback: try to get variables from debugger
                return self._get_variables_from_debugger(sandbox)
                
        except Exception as e:
            logger.error(f"Error getting Python variables: {e}")
            return {}
    
    def _get_variables_from_debugger(self, sandbox) -> Dict[str, Any]:
        """Get variables using Python debugger."""
        try:
            # This is a simplified approach - in practice, you'd need more sophisticated debugging
            return {
                "debug_info": "Variables captured via debugger",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error getting variables from debugger: {e}")
            return {}
    
    def _get_python_call_stack(self, sandbox) -> List[str]:
        """Get call stack from Python execution."""
        try:
            try:
                state_file = sandbox.filesystem.read("/tmp/execution_state.json")
                state_data = json.loads(state_file)
                return state_data.get('call_stack', [])
            except:
                return ["main()"]
                
        except Exception as e:
            logger.error(f"Error getting Python call stack: {e}")
            return ["main()"]
    
    def _get_current_line(self, sandbox) -> int:
        """Get current execution line number."""
        try:
            try:
                state_file = sandbox.filesystem.read("/tmp/execution_state.json")
                state_data = json.loads(state_file)
                return state_data.get('line_number', 0)
            except:
                return 0
                
        except Exception as e:
            logger.error(f"Error getting current line: {e}")
            return 0
    
    def _capture_javascript_execution(self, code_content: str) -> ExecutionTrace:
        """Capture JavaScript code execution."""
        try:
            logger.info("Capturing JavaScript execution")
            
            # For now, use simulation for JavaScript
            # In a full implementation, you'd use Node.js in E2B
            return self._simulate_execution_trace(code_content, "javascript")
            
        except Exception as e:
            logger.error(f"Error capturing JavaScript execution: {e}")
            return self._simulate_execution_trace(code_content, "javascript")
    
    def _capture_java_execution(self, code_content: str) -> ExecutionTrace:
        """Capture Java code execution."""
        try:
            logger.info("Capturing Java execution")
            
            # For now, use simulation for Java
            # In a full implementation, you'd use Java in E2B
            return self._simulate_execution_trace(code_content, "java")
            
        except Exception as e:
            logger.error(f"Error capturing Java execution: {e}")
            return self._simulate_execution_trace(code_content, "java")
    
    def _simulate_execution_trace(self, code_content: str, language: str) -> ExecutionTrace:
        """Simulate execution trace when E2B is not available."""
        try:
            logger.info(f"Simulating execution trace for {language}")
            
            states = []
            start_time = time.time()
            
            # Parse code to understand structure
            if language.lower() == "python":
                states = self._simulate_python_execution(code_content)
            elif language.lower() == "javascript":
                states = self._simulate_javascript_execution(code_content)
            elif language.lower() == "java":
                states = self._simulate_java_execution(code_content)
            else:
                states = self._simulate_generic_execution(code_content)
            
            total_duration = time.time() - start_time
            
            logger.info(f"Simulated execution trace: {len(states)} states")
            
            return ExecutionTrace(
                code_content=code_content,
                language=language,
                states=states,
                total_duration=total_duration,
                metadata={
                    "capture_method": "simulation",
                    "debug_mode": self.debug_mode
                }
            )
            
        except Exception as e:
            logger.error(f"Error simulating execution trace: {e}")
            raise
    
    def _simulate_python_execution(self, code_content: str) -> List[ExecutionState]:
        """Simulate Python execution trace."""
        try:
            states = []
            
            # Parse the code
            tree = ast.parse(code_content)
            
            # Extract functions and classes
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # Simulate execution steps
            step = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.For, ast.While, ast.If)):
                    state = ExecutionState(
                        timestamp=step * 0.5,
                        line_number=getattr(node, 'lineno', step),
                        variables={
                            "step": step,
                            "node_type": type(node).__name__,
                            "name": getattr(node, 'name', 'unknown')
                        },
                        call_stack=["main()"],
                        stdout=f"Executing {type(node).__name__}",
                        stderr=""
                    )
                    states.append(state)
                    step += 1
            
            # Add final state
            if states:
                final_state = ExecutionState(
                    timestamp=step * 0.5,
                    line_number=len(code_content.split('\n')),
                    variables={"completed": True},
                    call_stack=["main()"],
                    stdout="Execution completed",
                    stderr=""
                )
                states.append(final_state)
            
            return states
            
        except Exception as e:
            logger.error(f"Error simulating Python execution: {e}")
            return []
    
    def _simulate_javascript_execution(self, code_content: str) -> List[ExecutionState]:
        """Simulate JavaScript execution trace."""
        try:
            states = []
            
            # Simple simulation based on code structure
            lines = code_content.split('\n')
            
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ['function', 'for', 'while', 'if', 'const', 'let', 'var']):
                    state = ExecutionState(
                        timestamp=i * 0.3,
                        line_number=i + 1,
                        variables={
                            "line": i + 1,
                            "content": line.strip()
                        },
                        call_stack=["main()"],
                        stdout=f"Executing line {i + 1}",
                        stderr=""
                    )
                    states.append(state)
            
            return states
            
        except Exception as e:
            logger.error(f"Error simulating JavaScript execution: {e}")
            return []
    
    def _simulate_java_execution(self, code_content: str) -> List[ExecutionState]:
        """Simulate Java execution trace."""
        try:
            states = []
            
            # Simple simulation based on code structure
            lines = code_content.split('\n')
            
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ['public', 'private', 'class', 'method', 'for', 'while', 'if']):
                    state = ExecutionState(
                        timestamp=i * 0.4,
                        line_number=i + 1,
                        variables={
                            "line": i + 1,
                            "content": line.strip()
                        },
                        call_stack=["main()"],
                        stdout=f"Executing line {i + 1}",
                        stderr=""
                    )
                    states.append(state)
            
            return states
            
        except Exception as e:
            logger.error(f"Error simulating Java execution: {e}")
            return []
    
    def _simulate_generic_execution(self, code_content: str) -> List[ExecutionState]:
        """Simulate generic execution trace."""
        try:
            states = []
            
            lines = code_content.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip():  # Non-empty lines
                    state = ExecutionState(
                        timestamp=i * 0.2,
                        line_number=i + 1,
                        variables={
                            "line": i + 1,
                            "content": line.strip()
                        },
                        call_stack=["main()"],
                        stdout=f"Processing line {i + 1}",
                        stderr=""
                    )
                    states.append(state)
            
            return states
            
        except Exception as e:
            logger.error(f"Error simulating generic execution: {e}")
            return [] 