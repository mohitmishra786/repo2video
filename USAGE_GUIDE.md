# Enhanced RepoToVideo Usage Guide

This guide will help you set up and use all the enhanced features of RepoToVideo with detailed debugging information.

## 🚀 Quick Start

### 1. Environment Setup

First, make sure you have the API keys in your `.env` file:

```bash
# .env file
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
E2B_API_KEY=your_e2b_api_key_here
```

### 2. Test Your Setup

Run the quick setup test to verify everything is working:

```bash
python test_setup.py
```

This will check:
- ✅ Python version
- ✅ .env file and API keys
- ✅ All required dependencies
- ✅ Enhanced modules
- ✅ Optional dependencies

### 3. Comprehensive Testing

For detailed debugging, run the comprehensive test:

```bash
python debug_config.py
```

This will:
- 🔍 Verify environment setup
- 🔗 Test API connections
- 🧪 Test all components
- 📝 Generate detailed logs in `logs/` directory

## 📋 Usage Options

### Option 1: Web Interface (Recommended for Beginners)

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` and use the web interface.

### Option 2: Programmatic Usage (Advanced Users)

```python
from enhanced_example import EnhancedRepoToVideo

# Initialize the system
enhanced_system = EnhancedRepoToVideo("./your-project")

# Run comprehensive analysis
analysis = enhanced_system.analyze_project()

# Generate error simulations
error_simulations = enhanced_system.generate_error_simulations(code_content)

# Create dynamic visualizations
viz_path = enhanced_system.create_dynamic_visualization(code_content)

# Generate AI narration
narrated_content = enhanced_system.generate_narration(content, VoiceStyle.EDUCATIONAL)
```

### Option 3: Feature Demonstration

```bash
python enhanced_example.py
```

This runs a complete demonstration of all enhanced features.

## 🔧 Detailed Feature Usage

### 1. Enhanced Code Analysis

```python
from code_analysis import EnhancedCodeAnalyzer

# Initialize analyzer
analyzer = EnhancedCodeAnalyzer("./your-project")

# Comprehensive analysis
analysis = analyzer.analyze_project()

print(f"Files analyzed: {len(analysis['files'])}")
print(f"Languages found: {analysis['project_info']['languages']}")
print(f"Errors detected: {len(analysis['error_patterns'])}")
```

**Features:**
- Call graph generation (if pycallgraph2 is available)
- Dependency analysis (if pipdeptree is available)
- Error pattern detection
- Multi-language support (Python, JavaScript, Java)

### 2. Error Simulation Engine

```python
from error_simulation import ErrorSimulator

simulator = ErrorSimulator()

# Generate error simulations
code = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

result = calculate_average([1, 2, 3, 4, 5])
print(result)
"""

simulations = simulator.generate_error_simulations(code, num_errors=3)

for simulation in simulations:
    print(f"Error Type: {simulation.error_type.value}")
    print(f"Message: {simulation.error_message}")
    print(f"Explanation: {simulation.explanation}")
    print("---")
```

**Error Types Supported:**
- Undefined variables
- Type mismatches
- Missing imports
- Syntax errors
- Indentation errors
- Name errors
- Attribute errors
- Index errors
- Key errors
- Zero division errors

### 3. AI Narration System

```python
from narration import AINarrator, NarrationManager, VoiceStyle

# Initialize narrator
narrator = AINarrator(api_key=os.getenv('ELEVENLABS_API_KEY'))

# Create narration configuration
config = narrator.create_narration_config(
    style=VoiceStyle.EDUCATIONAL,
    language=Language.ENGLISH
)

# Generate narration
content = {
    'type': 'code_analysis',
    'title': 'Python Function Analysis',
    'content': {
        'language': 'Python',
        'functions': [{'name': 'calculate_average', 'parameters': ['numbers']}]
    }
}

manager = NarrationManager(narrator)
narrated_content = manager.generate_video_narration([content], config)
```

**Voice Styles Available:**
- `VoiceStyle.PROFESSIONAL` - Formal, business-like
- `VoiceStyle.EDUCATIONAL` - Clear, teaching-focused
- `VoiceStyle.TECHNICAL` - Technical, precise
- `VoiceStyle.FRIENDLY` - Warm, approachable
- `VoiceStyle.CASUAL` - Relaxed, conversational

### 4. Dynamic Execution Visualization

```python
from video_generator import VideoGenerator

generator = VideoGenerator()

# Trace code execution
code_content = """
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""

execution_trace = generator.trace_code_execution(code_content)

# Create visualization
video_path = generator.create_dynamic_execution_scene(code_content, execution_trace)
print(f"Visualization created: {video_path}")
```

**Features:**
- Real-time variable tracking
- Function call visualization
- Terminal simulation
- Call graph animation

### 5. Plugin Architecture

```python
from parsers import ParserManager

# Initialize parser manager
parser_manager = ParserManager()

# Parse a project
results = parser_manager.parse_project("./your-project")

print(f"Supported languages: {parser_manager.get_supported_languages()}")
print(f"Files parsed: {len(results['files'])}")

# Parse a specific file
file_path = Path("./your-project/main.py")
file_analysis = parser_manager.parse_file(file_path)
```

**Built-in Parsers:**
- Python (AST-based)
- JavaScript (regex-based)
- Java (regex-based)

**Adding Custom Parsers:**
```python
from parsers import BaseParser

class CustomParser(BaseParser):
    def __init__(self):
        self.supported_extensions = ['.custom']
        self.language_name = "Custom"
    
    def parse_file(self, file_path):
        # Your parsing logic here
        pass
    
    def get_supported_extensions(self):
        return self.supported_extensions
    
    def get_language_name(self):
        return self.language_name

# Register the parser
parser_manager.register_parser(CustomParser())
```

## 🐛 Debugging Guide

### 1. Check Logs

All operations generate detailed logs in the `logs/` directory:

```bash
# View latest log
ls -la logs/
tail -f logs/repotovideo_debug_*.log
```

### 2. Common Issues and Solutions

#### API Key Issues

**Problem:** "ELEVENLABS_API_KEY not found"
**Solution:** 
```bash
# Check if .env file exists
ls -la .env

# Verify API key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ELEVENLABS_API_KEY'))"
```

**Problem:** "E2B_API_KEY not found"
**Solution:** Same as above, but check E2B_API_KEY.

#### Dependency Issues

**Problem:** "ModuleNotFoundError: No module named 'manim'"
**Solution:**
```bash
pip install manim
```

**Problem:** "ModuleNotFoundError: No module named 'e2b'"
**Solution:**
```bash
pip install e2b
```

#### Permission Issues

**Problem:** "Permission denied" when creating files
**Solution:**
```bash
# Check directory permissions
ls -la

# Fix permissions if needed
chmod 755 .
mkdir -p logs
chmod 755 logs
```

### 3. Performance Optimization

#### Enable Hardware Acceleration

For faster video rendering, ensure FFmpeg is installed:

```bash
# On macOS
brew install ffmpeg

# On Ubuntu
sudo apt-get install ffmpeg

# On Windows
# Download from https://ffmpeg.org/download.html
```

#### Parallel Processing

The system automatically uses parallel processing where available. For manual control:

```python
import multiprocessing

# Set number of processes
multiprocessing.set_start_method('spawn', force=True)
```

### 4. Memory Management

For large projects, monitor memory usage:

```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
```

## 📊 Monitoring and Metrics

### 1. Performance Metrics

The system tracks various metrics:

```python
# Get analysis metrics
analysis = enhanced_system.analyze_project()
metrics = analysis['metrics']

print(f"Total lines of code: {metrics['total_lines']}")
print(f"Total functions: {metrics['total_functions']}")
print(f"Total classes: {metrics['total_classes']}")
print(f"Average complexity: {metrics['average_complexity']}")
```

### 2. API Usage Tracking

Monitor API usage:

```python
# ElevenLabs usage
voices = narrator.get_available_voices()
print(f"Available voices: {len(voices)}")

# E2B usage
# Check session limits and usage in E2B dashboard
```

## 🔒 Security Considerations

### 1. API Key Security

- Never commit API keys to version control
- Use environment variables or .env files
- Rotate keys regularly
- Monitor API usage for unusual activity

### 2. Code Execution Safety

- E2B sandbox provides isolated execution
- All code execution is sandboxed
- No network access from executed code
- Timeout limits prevent infinite loops

### 3. File System Safety

- All file operations are restricted to project directory
- Temporary files are automatically cleaned up
- No access to system files outside project

## 🎯 Best Practices

### 1. Project Organization

```
your-project/
├── .env                    # API keys (not in version control)
├── logs/                   # Debug logs
├── output/                 # Generated videos
├── temp/                   # Temporary files (auto-cleaned)
└── your-code/              # Your actual project
```

### 2. Error Handling

```python
try:
    enhanced_system = EnhancedRepoToVideo("./your-project")
    analysis = enhanced_system.analyze_project()
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    # Fallback to basic analysis
```

### 3. Resource Management

```python
# Always clean up resources
try:
    enhanced_system = EnhancedRepoToVideo("./your-project")
    # Your operations here
finally:
    enhanced_system.cleanup()
```

## 📞 Support

If you encounter issues:

1. **Check the logs** in `logs/` directory
2. **Run the test scripts** to identify problems
3. **Verify API keys** are correctly set
4. **Check dependencies** are installed
5. **Review error messages** for specific issues

For detailed debugging, run:
```bash
python debug_config.py
```

This will provide comprehensive information about your setup and help identify any issues. 