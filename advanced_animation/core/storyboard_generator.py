"""
AI-Powered Storyboard Generator

This module converts code analysis into 3Blue1Brown-style visual storyboards
using GPT-4 for concept abstraction and visual metaphor generation.
"""

import os
import json
import logging
import openai
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .data_structures import (
    Storyboard, StoryboardScene, VisualElement,
    AnimationStep, CameraMovement, DataStructureManager
)

logger = logging.getLogger(__name__)

# Advanced AI integration imports
try:
    from langchain_openai import OpenAI
    OPENAI_LLM_AVAILABLE = True
except ImportError as exc:
    logger.info("LangChain OpenAI not available: %s", exc)
    OPENAI_LLM_AVAILABLE = False

try:
    from langchain_groq import ChatGroq as Groq
    GROQ_LLM_AVAILABLE = True
except ImportError as exc:
    logger.info("LangChain Groq not available: %s", exc)
    GROQ_LLM_AVAILABLE = False

class StoryboardGenerator:
    """AI-powered storyboard generator using Groq as primary and OpenAI as fallback."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the storyboard generator.

        Args:
            openai_api_key: OpenAI API key for GPT-4 access (fallback)
        """
        # Initialize Groq client as primary
        self.groq_client = None
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq API initialized as primary AI provider")
            except ImportError:
                logger.warning("Groq library not available. Falling back to OpenAI.")
                self.groq_client = None
        else:
            logger.warning("Groq API key not provided. Falling back to OpenAI.")
            self.groq_client = None

        # Initialize OpenAI client as fallback
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            logger.warning("OpenAI API key not provided. Using fallback storyboard generation.")
            self.openai_client = None

        # Determine which client to use
        self.client = self.groq_client if self.groq_client else self.openai_client

        # Visual metaphor library
        self.visual_metaphors = {
            "array": {
                "type": "rectangle_array",
                "default_color": "#ff7f0e",
                "animation": "sequential_highlight"
            },
            "tree": {
                "type": "hierarchical_tree",
                "default_color": "#2ca02c",
                "animation": "depth_first_traversal"
            },
            "graph": {
                "type": "network_graph",
                "default_color": "#d62728",
                "animation": "path_highlight"
            },
            "stack": {
                "type": "vertical_stack",
                "default_color": "#9467bd",
                "animation": "push_pop_animation"
            },
            "queue": {
                "type": "horizontal_queue",
                "default_color": "#8c564b",
                "animation": "enqueue_dequeue"
            },
            "sorting": {
                "type": "array_with_pivot",
                "default_color": "#e377c2",
                "animation": "partition_animation"
            },
            "searching": {
                "type": "array_with_pointer",
                "default_color": "#7f7f7f",
                "animation": "binary_search_animation"
            }
        }

        logger.info("StoryboardGenerator initialized with visual metaphor library")

    def generate_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """
        Convert code analysis into visual storyboard using GPT-4.

        Args:
            code_analysis: Dictionary containing code analysis results

        Returns:
            Storyboard object with scenes and animations
        """
        logger.info(f"Generating storyboard for code analysis with {len(code_analysis.get('files', []))} files")

        if self.client:
            return self._generate_ai_storyboard(code_analysis)
        else:
            return self._generate_fallback_storyboard(code_analysis)

    def _generate_ai_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """Generate storyboard using Groq (primary) or OpenAI (fallback) with retry logic."""
        import time
        import random

        max_retries = 3
        base_delay = 2  # Base delay in seconds

        # Determine which client and models to use
        clients_and_models = []

        # Add Groq models first (primary)
        if self.groq_client:
            clients_and_models.extend([
                (self.groq_client, "llama-3.3-70b-versatile", "Groq"),  # Best free model
                (self.groq_client, "llama-3.3-8b-instant", "Groq"),     # Faster alternative
                (self.groq_client, "mixtral-8x7b-32768", "Groq")         # Another good option
            ])

        # Add OpenAI models as fallback
        if self.openai_client:
            clients_and_models.extend([
                (self.openai_client, "gpt-4o-mini", "OpenAI"),      # More reliable
                (self.openai_client, "gpt-4-turbo", "OpenAI"),      # Alternative
                (self.openai_client, "gpt-3.5-turbo", "OpenAI")      # Most reliable fallback
            ])

        if not clients_and_models:
            logger.error("No AI clients available. Falling back to rule-based generation.")
            return self._generate_fallback_storyboard(code_analysis)

        for attempt in range(max_retries):
            try:
                client, model, provider = clients_and_models[attempt % len(clients_and_models)]
                logger.info(f"Using {provider} {model} for AI-powered storyboard generation (attempt {attempt + 1}/{max_retries})")

                 # Check if we need to chunk the request for Groq to avoid token limits
                if provider == "Groq":
                    # Estimate token size and chunk if too large
                    prompt_size = self._estimate_prompt_size(code_analysis)
                    logger.info(f"Estimated prompt size: {prompt_size} tokens")
                    if prompt_size > 60000:  # Further reduced threshold to force chunking for this repo
                        logger.info(f"Prompt too large ({prompt_size} tokens), using chunked approach")
                        storyboard_data = self._generate_chunked_storyboard(client, model, code_analysis)
                    else:
                        # Prepare the full prompt
                        logger.info(f"Prompt size acceptable ({prompt_size} tokens), using full approach")
                        prompt = self._create_storyboard_prompt(code_analysis)
                        storyboard_data = self._call_ai_api(client, model, provider, prompt)
                else:
                    # For OpenAI, use the full prompt (higher token limits)
                    prompt = self._create_storyboard_prompt(code_analysis)
                    storyboard_data = self._call_ai_api(client, model, provider, prompt)

                # Parse the response
                if storyboard_data:
                    logger.info(f"Successfully generated AI storyboard with {len(storyboard_data.get('scenes', []))} scenes using {provider} {model}")
                    return self._parse_storyboard_response(storyboard_data, code_analysis)
                else:
                    raise ValueError("Empty response from AI provider")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")

                # Check if it's a rate limit error
                if "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Rate limited. Waiting {delay:.1f} seconds before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error("Max retries reached for rate limit. Falling back to rule-based generation.")
                        break
                else:
                    # For other errors, don't retry
                    logger.error(f"Non-retryable error: {error_msg}")
                    break

        logger.info("Falling back to rule-based storyboard generation")
        return self._generate_fallback_storyboard(code_analysis)

    def _call_ai_api(self, client, model: str, provider: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Call the AI API and return the response."""
        try:
            if provider == "Groq":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in creating 3Blue1Brown-style educational animations. Convert code analysis into visual storyboards with clear visual metaphors and smooth animations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=4000
                )
                response_content = response.choices[0].message.content
            else:  # OpenAI
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in creating 3Blue1Brown-style educational animations. Convert code analysis into visual storyboards with clear visual metaphors and smooth animations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=4000
                )
                response_content = response.choices[0].message.content

            # Parse the response
            if response_content:
                return json.loads(response_content)
            else:
                logger.error("Empty response from AI provider")
                return None

        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            raise

    def _generate_chunked_storyboard(self, client, model: str, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate storyboard by processing files in chunks to avoid token limits."""
        try:
            files = list(code_analysis.get('files', {}).items())
            chunk_size = 2  # Further reduced chunk size to ensure we stay well under token limits
            all_scenes = []

            # Process files in chunks
            for i in range(0, len(files), chunk_size):
                chunk = files[i:i + chunk_size]
                chunk_data = {
                    'files': {k: v for k, v in chunk},
                    'algorithms': code_analysis.get('algorithms', []),
                    'data_structures': code_analysis.get('data_structures', []),
                    'complexity_analysis': code_analysis.get('complexity_analysis', {})
                }

                # Create prompt for this chunk
                chunk_prompt = self._create_chunked_storyboard_prompt(chunk_data, i//chunk_size + 1, len(files))

                # Call AI API for this chunk
                chunk_response = self._call_ai_api(client, model, "Groq", chunk_prompt)

                if chunk_response:
                    all_scenes.extend(chunk_response.get('scenes', []))
                else:
                    logger.warning(f"Failed to get response for chunk {i//chunk_size + 1}")

            # Combine all scenes into final storyboard
            final_storyboard = {
                'title': 'Comprehensive Code Repository Analysis',
                'description': 'Detailed educational animation with code execution flow, AST analysis, and algorithm visualization',
                'scenes': all_scenes
            }

            return final_storyboard

        except Exception as e:
            logger.error(f"Error generating chunked storyboard: {e}")
            raise

    def _create_chunked_storyboard_prompt(self, chunk_data: Dict[str, Any], chunk_num: int, total_chunks: int) -> str:
        """Create a prompt for a chunk of files."""
        files = chunk_data.get('files', [])
        algorithms = chunk_data.get('algorithms', [])
        data_structures = chunk_data.get('data_structures', [])
        complexity = chunk_data.get('complexity_analysis', {})

        # Create a summary of the chunk
        file_summaries = []
        for file_path, file_data in files.items():
            summary = {
                'path': str(file_path),
                'language': file_data.get('language', 'unknown'),
                'lines': file_data.get('lines', 0),
                'functions': len(file_data.get('functions', [])),
                'classes': len(file_data.get('classes', [])),
                'complexity': file_data.get('complexity', 0)
            }
            file_summaries.append(summary)

        prompt = f"""
        Create scenes for a 3Blue1Brown-style storyboard for this code analysis (chunk {chunk_num}/{total_chunks}):

        Files in this chunk: {len(files)} files
        Algorithms: {algorithms}
        Data Structures: {data_structures}
        Complexity: {complexity}

        File Summaries:
        {json.dumps(file_summaries, indent=2)}

        Output JSON format with scenes for this chunk:
        {{
          "scenes": [
            {{
              "id": 1,
              "concept": "Analysis of chunk {chunk_num}",
              "visual_elements": [
                {{
                  "type": "text",
                  "properties": {{"text": "Analyzing code files"}},
                  "position": {{"x": 0, "y": 0, "z": 0}},
                  "color": "#ffffff",
                  "size": 1.0
                }}
              ],
              "animation_sequence": [],
              "narration": "Analyzing the next set of files...",
              "duration": 5.0,
              "camera_movement": {{"phi": 75.0, "theta": -45.0, "distance": 5.0}}
            }}
          ]
        }}
        """

        return prompt

    def _estimate_prompt_size(self, code_analysis: Dict[str, Any]) -> int:
        """Estimate the token size of the prompt."""
        try:
            # More realistic estimate: the actual prompt includes much more than just file analysis
            # It includes scene descriptions, visual elements, animation sequences, etc.
            files = code_analysis.get('files', {})
            total_chars = 0

            # Count characters in file summaries
            for file_data in files.values():
                total_chars += len(str(file_data.get('functions', [])))
                total_chars += len(str(file_data.get('classes', [])))
                total_chars += len(str(file_data.get('imports', [])))
                # Add more realistic overhead for file structure, complexity, etc.
                total_chars += 5000  # Increased per-file overhead

            # Add base prompt size - this is much larger than initially estimated
            total_chars += 20000  # Much larger base prompt

            # Account for the full storyboard structure that gets generated
            # Each scene adds significant overhead
            num_files = len(files)
            total_chars += num_files * 10000  # Per-file scene generation overhead

            # More realistic token estimate
            return total_chars // 3  # Convert to token estimate
        except Exception as e:
            logger.error(f"Error estimating prompt size: {e}")
            return 65000  # Further reduced threshold to trigger chunking more aggressively

    def _create_storyboard_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Create the prompt for GPT-4 storyboard generation."""

        # Extract key information from code analysis
        files = code_analysis.get('files', [])
        algorithms = code_analysis.get('algorithms', [])
        data_structures = code_analysis.get('data_structures', [])
        complexity = code_analysis.get('complexity_analysis', {})

        prompt = f"""
        Create a 3Blue1Brown-style storyboard for this code analysis:

        Files: {len(files)} files analyzed
        Algorithms: {algorithms}
        Data Structures: {data_structures}
        Complexity: {complexity}

        Code Analysis Details:
        {json.dumps(code_analysis, indent=2)}

        Output JSON format:
        {{
          "title": "Algorithm Visualization",
          "description": "Educational animation explaining the code",
          "scenes": [
            {{
              "id": 1,
              "concept": "Introduction to the algorithm",
              "visual_elements": [
                {{
                  "type": "array",
                  "properties": {{"size": 5, "values": [3, 1, 4, 1, 5]}},
                  "position": {{"x": 0, "y": 0, "z": 0}},
                  "color": "#ff7f0e",
                  "size": 1.0
                }}
              ],
              "animation_sequence": [
                {{
                  "action": "FadeIn",
                  "target": "array",
                  "duration": 2.0,
                  "easing": "ease_in_out",
                  "parameters": {{"scale": 1.2}}
                }}
              ],
              "narration": "We start by examining our array of numbers...",
              "duration": 8.0,
              "camera_movement": {{
                "phi": 75.0,
                "theta": -45.0,
                "zoom": 1.2,
                "duration": 2.0
              }}
            }}
          ],
          "total_duration": 45.0,
          "metadata": {{
            "style": "3blue1brown",
            "theme": "educational",
            "target_audience": "programmers"
          }}
        }}

        Guidelines:
        1. Use clear visual metaphors (arrays as rectangles, trees as hierarchical structures)
        2. Include smooth camera movements and transitions
        3. Break complex algorithms into digestible steps
        4. Use color coding for different concepts
        5. Include runtime execution visualization where possible
        6. Keep each scene focused on one concept
        7. Use 3D positioning for depth and visual interest
        """

        return prompt

    def _parse_storyboard_response(self, storyboard_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> Storyboard:
        """Parse GPT-4 response into Storyboard object."""

        scenes = []
        for scene_data in storyboard_data.get('scenes', []):
            # Parse visual elements
            visual_elements = []
            for elem_data in scene_data.get('visual_elements', []):
                visual_elements.append(VisualElement(**elem_data))

            # Parse animation sequence
            animation_sequence = []
            for anim_data in scene_data.get('animation_sequence', []):
                animation_sequence.append(AnimationStep(**anim_data))

            # Parse camera movement
            camera_data = scene_data.get('camera_movement', {})
            camera_movement = CameraMovement(**camera_data)

            # Create scene
            scene = StoryboardScene(
                id=scene_data['id'],
                concept=scene_data['concept'],
                visual_elements=visual_elements,
                animation_sequence=animation_sequence,
                narration=scene_data['narration'],
                duration=scene_data['duration'],
                camera_movement=camera_movement,
                code_snippet=scene_data.get('code_snippet'),
                execution_state=scene_data.get('execution_state')
            )
            scenes.append(scene)

        return Storyboard(
            title=storyboard_data.get('title', 'Code Visualization'),
            description=storyboard_data.get('description', 'Educational animation'),
            scenes=scenes,
            total_duration=storyboard_data.get('total_duration', 60.0),
            metadata=storyboard_data.get('metadata', {})
        )

    def _get_file_structure(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file structure information from code analysis."""
        files = code_analysis.get('files', {})

        # Analyze file structure
        file_types = {}
        directories = set()

        for file_path in files.keys():
            if isinstance(file_path, str):
                # Extract directory structure
                parts = file_path.split('/')
                if len(parts) > 1:
                    main_dir = parts[-2] if len(parts) > 2 else parts[0]
                    directories.add(main_dir)

                # Extract file extension
                ext = file_path.split('.')[-1] if '.' in file_path else 'unknown'
                file_types[ext] = file_types.get(ext, 0) + 1

        return {
            'directories': list(directories),
            'file_types': file_types,
            'total_directories': len(directories),
            'total_file_types': len(file_types)
        }

    def _get_complexity_metrics(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract complexity metrics from code analysis."""
        files = code_analysis.get('files', {})

        total_lines = 0
        total_functions = 0
        total_classes = 0

        for file_info in files.values():
            total_lines += file_info.get('lines', 0)
            total_functions += len(file_info.get('functions', []))
            total_classes += len(file_info.get('classes', []))

        avg_function_length = total_lines / total_functions if total_functions > 0 else 0

        return {
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_function_length': round(avg_function_length, 1),
            'avg_lines_per_file': round(total_lines / len(files), 1) if files else 0
        }

    def _get_functions_list(self, code_analysis: Dict[str, Any]) -> List[str]:
        """Extract list of function names from code analysis."""
        files = code_analysis.get('files', {})
        functions = []

        for file_info in files.values():
            for func in file_info.get('functions', []):
                if isinstance(func, dict) and 'name' in func:
                    functions.append(func['name'])
                elif isinstance(func, str):
                    functions.append(func)

        return functions[:10]  # Limit to 10 functions

    def _get_data_structures(self, code_analysis: Dict[str, Any]) -> List[str]:
        """Extract data structures information from code analysis."""
        # This is a simplified extraction - in a real implementation,
        # you would analyze the code for data structure usage
        return ['lists', 'dictionaries', 'sets', 'tuples']  # Default data structures

    def _get_scene_metadata(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get standardized metadata for all scenes."""
        files = code_analysis.get('files', {})

        # Calculate totals
        total_files = len(files)
        total_lines = sum(file_info.get('lines', 0) for file_info in files.values())
        total_functions = sum(len(file_info.get('functions', [])) for file_info in files.values())
        total_classes = sum(len(file_info.get('classes', [])) for file_info in files.values())
        languages = set(file_info.get('language', 'unknown') for file_info in files.values() if file_info.get('language') != 'unknown')

        # Get additional data
        file_structure = self._get_file_structure(code_analysis)
        complexity_metrics = self._get_complexity_metrics(code_analysis)
        functions_list = self._get_functions_list(code_analysis)
        data_structures = self._get_data_structures(code_analysis)

        return {
            'files': total_files,
            'languages': list(languages),
            'lines_of_code': total_lines,
            'functions': total_functions,
            'classes': total_classes,
            'file_structure': file_structure,
            'complexity': complexity_metrics,
            'functions_list': functions_list,
            'data_structures': data_structures
        }

    def _generate_fallback_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """Generate detailed storyboard using rule-based approach when AI is not available."""
        logger.info("Generating detailed fallback storyboard using rule-based approach")

        scenes = []
        scene_id = 1

        # 1. Repository Overview with detailed analysis
        intro_scene = self._create_detailed_intro_scene(scene_id, code_analysis)
        scenes.append(intro_scene)
        scene_id += 1

        # 2. File Structure Analysis
        structure_scene = self._create_file_structure_scene(scene_id, code_analysis)
        scenes.append(structure_scene)
        scene_id += 1

        # 3. Language Distribution Analysis
        language_scene = self._create_language_analysis_scene(scene_id, code_analysis)
        scenes.append(language_scene)
        scene_id += 1

        # 4. Code Complexity Analysis
        complexity_scene = self._create_detailed_complexity_scene(scene_id, code_analysis)
        scenes.append(complexity_scene)
        scene_id += 1

        # 5. Function Call Graph Visualization
        call_graph_scene = self._create_call_graph_scene(scene_id, code_analysis)
        scenes.append(call_graph_scene)
        scene_id += 1

        # 6. AST (Abstract Syntax Tree) Visualization
        ast_scene = self._create_ast_visualization_scene(scene_id, code_analysis)
        scenes.append(ast_scene)
        scene_id += 1

        # 7. Algorithm Execution Flow
        execution_scene = self._create_execution_flow_scene(scene_id, code_analysis)
        scenes.append(execution_scene)
        scene_id += 1

        # 8. Data Structure Visualization
        data_structure_scene = self._create_detailed_data_structure_scene(scene_id, code_analysis)
        scenes.append(data_structure_scene)
        scene_id += 1

        # 9. Performance Analysis
        performance_scene = self._create_performance_analysis_scene(scene_id, code_analysis)
        scenes.append(performance_scene)
        scene_id += 1

        # 10. Repository Summary with Insights
        summary_scene = self._create_detailed_summary_scene(scene_id, code_analysis)
        scenes.append(summary_scene)

        total_duration = sum(scene.duration for scene in scenes)

        return Storyboard(
            title="Comprehensive Code Repository Analysis",
            description="Detailed educational animation with code execution flow, AST analysis, and algorithm visualization",
            scenes=scenes,
            total_duration=total_duration,
            metadata={
                "style": "3blue1brown",
                "theme": "educational",
                "generation_method": "rule_based"
            }
        )

    def _create_intro_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create introduction scene."""
        files = code_analysis.get('files', [])

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "Repository Analysis", "font_size": 48},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="text",
                properties={"text": f"{len(files)} files analyzed", "font_size": 24},
                position={"x": 0, "y": 0, "z": 0},
                color="#cccccc"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 2.0),
            AnimationStep("Scale", "text", 1.0, parameters={"scale": 1.1})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Repository Overview",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="Welcome to our code repository analysis. We'll explore the algorithms and data structures used in this codebase.",
            duration=5.0,
            camera_movement=CameraMovement()
        )

    def _create_algorithm_scene(self, scene_id: int, algorithm: str, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for algorithm visualization."""

        # Determine visual metaphor based on algorithm type
        if "sort" in algorithm.lower():
            visual_type = "sorting"
            metaphor = self.visual_metaphors["sorting"]
        elif "search" in algorithm.lower():
            visual_type = "searching"
            metaphor = self.visual_metaphors["searching"]
        else:
            visual_type = "array"
            metaphor = self.visual_metaphors["array"]

        visual_elements = [
            VisualElement(
                type=metaphor["type"],
                properties={"size": 6, "values": [3, 1, 4, 1, 5, 9]},
                position={"x": 0, "y": 0, "z": 0},
                color=metaphor["default_color"]
            ),
            VisualElement(
                type="text",
                properties={"text": algorithm.title(), "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", visual_type, 2.0),
            AnimationStep(metaphor["animation"], visual_type, 4.0)
        ]

        return StoryboardScene(
            id=scene_id,
            concept=f"{algorithm.title()} Algorithm",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"Let's examine the {algorithm} algorithm. This is a fundamental algorithm that...",
            duration=8.0,
            camera_movement=CameraMovement(zoom=1.5)
        )

    def _create_data_structure_scene(self, scene_id: int, data_structure: str, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for data structure visualization."""

        # Map data structure to visual metaphor
        ds_lower = data_structure.lower()
        if "tree" in ds_lower:
            visual_type = "tree"
            metaphor = self.visual_metaphors["tree"]
        elif "graph" in ds_lower:
            visual_type = "graph"
            metaphor = self.visual_metaphors["graph"]
        elif "stack" in ds_lower:
            visual_type = "stack"
            metaphor = self.visual_metaphors["stack"]
        elif "queue" in ds_lower:
            visual_type = "queue"
            metaphor = self.visual_metaphors["queue"]
        else:
            visual_type = "array"
            metaphor = self.visual_metaphors["array"]

        visual_elements = [
            VisualElement(
                type=metaphor["type"],
                properties={"size": 5, "values": [1, 2, 3, 4, 5]},
                position={"x": 0, "y": 0, "z": 0},
                color=metaphor["default_color"]
            ),
            VisualElement(
                type="text",
                properties={"text": data_structure.title(), "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", visual_type, 2.0),
            AnimationStep(metaphor["animation"], visual_type, 4.0)
        ]

        return StoryboardScene(
            id=scene_id,
            concept=f"{data_structure.title()} Data Structure",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The {data_structure} data structure is used to organize and store data efficiently...",
            duration=8.0,
            camera_movement=CameraMovement(phi=60, theta=-30)
        )

    def _create_complexity_scene(self, scene_id: int, complexity: Dict[str, Any], code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for complexity analysis visualization."""

        visual_elements = [
            VisualElement(
                type="complexity_graph",
                properties={"time_complexity": complexity.get("time", "O(n)"), "space_complexity": complexity.get("space", "O(1)")},
                position={"x": 0, "y": 0, "z": 0},
                color="#e377c2"
            ),
            VisualElement(
                type="text",
                properties={"text": "Complexity Analysis", "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", "complexity_graph", 2.0),
            AnimationStep("AnimateGrowth", "complexity_graph", 4.0)
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Algorithm Complexity",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="Let's analyze the time and space complexity of our algorithms...",
            duration=8.0,
            camera_movement=CameraMovement(zoom=1.3)
        )

    def _create_summary_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create summary scene."""

        algorithms = code_analysis.get('algorithms', [])
        data_structures = code_analysis.get('data_structures', [])

        visual_elements = [
            VisualElement(
                type="summary_dashboard",
                properties={"algorithms": algorithms, "data_structures": data_structures},
                position={"x": 0, "y": 0, "z": 0},
                color="#1f77b4"
            ),
            VisualElement(
                type="text",
                properties={"text": "Summary", "font_size": 48},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", "summary_dashboard", 3.0),
            AnimationStep("Highlight", "summary_dashboard", 2.0)
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Repository Summary",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="In summary, we've explored the key algorithms and data structures in this repository...",
            duration=6.0,
            camera_movement=CameraMovement(zoom=1.0)
        )

    def save_storyboard(self, storyboard: Storyboard, output_path: str) -> str:
        """Save storyboard to JSON file."""
        return DataStructureManager.save_storyboard(storyboard, output_path)

    def load_storyboard(self, file_path: str) -> Storyboard:
        """Load storyboard from JSON file."""
        return DataStructureManager.load_storyboard(file_path)

    # ===== DETAILED SCENE CREATION METHODS =====

    def _create_detailed_intro_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create detailed introduction scene with repository analysis."""
        files = code_analysis.get('files', {})
        total_files = len(files)

        logger.info(f"Creating intro scene with {total_files} files")

        # Extract key metrics with detailed logging
        languages = set()
        total_lines = 0
        functions = 0
        classes = 0

        for file_path, file_info in files.items():
            lang = file_info.get('language', 'unknown')
            if lang != 'unknown':
                languages.add(lang)
                logger.info(f"Found language '{lang}' in file: {file_path}")

            lines = file_info.get('lines', 0)
            total_lines += lines

            funcs = len(file_info.get('functions', []))
            functions += funcs

            cls = len(file_info.get('classes', []))
            classes += cls

            logger.debug(f"File {file_path}: {lang}, {lines} lines, {funcs} functions, {cls} classes")

        logger.info(f"Total metrics: {len(languages)} languages ({list(languages)}), {total_lines} lines, {functions} functions, {classes} classes")

        # Get additional data for metadata
        file_structure = self._get_file_structure(code_analysis)
        complexity_metrics = self._get_complexity_metrics(code_analysis)
        functions_list = self._get_functions_list(code_analysis)
        data_structures = self._get_data_structures(code_analysis)

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "Comprehensive Repository Analysis", "font_size": 48},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="text",
                properties={"text": f"📁 {total_files} Files Analyzed", "font_size": 32},
                position={"x": -4, "y": 1, "z": 0},
                color="#4CAF50"
            ),
            VisualElement(
                type="text",
                properties={"text": f"💻 {len(languages)} Languages", "font_size": 32},
                position={"x": 0, "y": 1, "z": 0},
                color="#2196F3"
            ),
            VisualElement(
                type="text",
                properties={"text": f"📊 {total_lines:,} Lines of Code", "font_size": 32},
                position={"x": 4, "y": 1, "z": 0},
                color="#FF9800"
            ),
            VisualElement(
                type="text",
                properties={"text": f"🔧 {functions} Functions", "font_size": 28},
                position={"x": -4, "y": -1, "z": 0},
                color="#9C27B0"
            ),
            VisualElement(
                type="text",
                properties={"text": f"🏗️ {classes} Classes", "font_size": 28},
                position={"x": 0, "y": -1, "z": 0},
                color="#E91E63"
            ),
            VisualElement(
                type="text",
                properties={"text": "🎬 Generating Detailed Animation...", "font_size": 24},
                position={"x": 4, "y": -1, "z": 0},
                color="#607D8B"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "Comprehensive Repository Analysis"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "📁 Files"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "💻 Languages"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "📊 Lines"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🔧 Functions"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🏗️ Classes"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🎬 Generating"}),
            AnimationStep("Scale", "text", 2.0, parameters={"scale": 1.1, "target": "Comprehensive Repository Analysis"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Repository Overview & Analysis",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"Welcome to our comprehensive analysis of this code repository. We've analyzed {total_files} files across {len(languages)} programming languages, containing {total_lines:,} lines of code with {functions} functions and {classes} classes. Let's dive deep into the codebase structure, algorithms, and execution flow.",
            duration=12.0,
            camera_movement=CameraMovement(phi=75.0, theta=-45.0, zoom=1.3, duration=3.0),
            metadata={
                'files': total_files,
                'languages': list(languages),
                'lines_of_code': total_lines,
                'functions': functions,
                'classes': classes,
                'file_structure': self._get_file_structure(code_analysis),
                'complexity': self._get_complexity_metrics(code_analysis),
                'functions_list': self._get_functions_list(code_analysis),
                'data_structures': self._get_data_structures(code_analysis)
            }
        )

    def _create_file_structure_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene showing file structure and organization."""
        files = code_analysis.get('files', {})

        logger.info(f"Creating file structure scene with {len(files)} files")

        # Analyze file structure with detailed logging
        file_types = {}
        directories = set()

        for file_path in files.keys():
            if isinstance(file_path, str):
                # Extract directory structure
                parts = file_path.split('/')
                if len(parts) > 1:
                    # Get the main directory (second to last part for nested structures)
                    main_dir = parts[-2] if len(parts) > 2 else parts[0]
                    directories.add(main_dir)
                    logger.debug(f"Found directory: {main_dir} from path: {file_path}")

                # Extract file extension
                ext = file_path.split('.')[-1] if '.' in file_path else 'unknown'
                file_types[ext] = file_types.get(ext, 0) + 1
                logger.debug(f"Found file type: .{ext} from path: {file_path}")

        logger.info(f"File structure analysis: {len(directories)} directories ({list(directories)}), {len(file_types)} file types ({list(file_types.keys())})")

        # Create visual elements for file structure
        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "📂 File Structure Analysis", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            )
        ]

        # Add directory structure
        y_pos = 1.5
        for i, directory in enumerate(list(directories)[:6]):  # Show first 6 directories
            visual_elements.append(VisualElement(
                type="text",
                properties={"text": f"📁 {directory}/", "font_size": 24},
                position={"x": -3, "y": y_pos - i*0.8, "z": 0},
                color="#4CAF50"
            ))

        # Add file type distribution
        y_pos = 1.5
        for i, (ext, count) in enumerate(list(file_types.items())[:6]):  # Show first 6 file types
            visual_elements.append(VisualElement(
                type="text",
                properties={"text": f"📄 .{ext}: {count} files", "font_size": 20},
                position={"x": 3, "y": y_pos - i*0.6, "z": 0},
                color="#2196F3"
            ))

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "📂 File Structure Analysis"}),
            AnimationStep("FadeIn", "text", 0.3, parameters={"target": "📁"}),
            AnimationStep("FadeIn", "text", 0.3, parameters={"target": "📄"}),
            AnimationStep("Scale", "text", 2.0, parameters={"scale": 1.05, "target": "📂 File Structure Analysis"})
        ]

        # Get metadata for this scene
        file_structure = self._get_file_structure(code_analysis)
        complexity_metrics = self._get_complexity_metrics(code_analysis)
        functions_list = self._get_functions_list(code_analysis)
        data_structures = self._get_data_structures(code_analysis)

        # Calculate totals for metadata
        total_files = len(files)
        total_lines = sum(file_info.get('lines', 0) for file_info in files.values())
        total_functions = sum(len(file_info.get('functions', [])) for file_info in files.values())
        total_classes = sum(len(file_info.get('classes', [])) for file_info in files.values())
        languages = set(file_info.get('language', 'unknown') for file_info in files.values() if file_info.get('language') != 'unknown')

        return StoryboardScene(
            id=scene_id,
            concept="File Structure & Organization",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The repository contains {len(directories)} main directories and {len(file_types)} different file types. The codebase is well-organized with clear separation of concerns across different modules and components.",
            duration=10.0,
            camera_movement=CameraMovement(phi=60.0, theta=-30.0, zoom=1.4, duration=2.0),
            metadata={
                'files': total_files,
                'languages': list(languages),
                'lines_of_code': total_lines,
                'functions': total_functions,
                'classes': total_classes,
                'file_structure': file_structure,
                'complexity': complexity_metrics,
                'functions_list': functions_list,
                'data_structures': data_structures
            }
        )

    def _create_language_analysis_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene showing programming language distribution."""
        files = code_analysis.get('files', {})

        logger.info(f"Creating language analysis scene with {len(files)} files")

        # Count languages with detailed logging
        language_counts = {}
        for file_path, file_info in files.items():
            lang = file_info.get('language', 'unknown')
            if lang != 'unknown':
                language_counts[lang] = language_counts.get(lang, 0) + 1
                logger.debug(f"Found language '{lang}' in file: {file_path}")
            else:
                logger.warning(f"Unknown language for file: {file_path}")

        logger.info(f"Language distribution: {language_counts}")

        # Create pie chart visualization
        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "🌐 Programming Language Distribution", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="pie_chart",
                properties={"data": language_counts, "radius": 2.0},
                position={"x": 0, "y": 0, "z": 0},
                color="#FF6B6B"
            )
        ]

        # Add language labels
        y_pos = -2.5
        for i, (lang, count) in enumerate(language_counts.items()):
            visual_elements.append(VisualElement(
                type="text",
                properties={"text": f"🔸 {lang.title()}: {count} files", "font_size": 20},
                position={"x": -4, "y": y_pos - i*0.5, "z": 0},
                color="#FFD93D"
            ))

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "🌐 Programming Language Distribution"}),
            AnimationStep("Create", "pie_chart", 3.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🔸"}),
            AnimationStep("Rotate", "pie_chart", 2.0, parameters={"angle": 360})
        ]

        # Get metadata for this scene
        file_structure = self._get_file_structure(code_analysis)
        complexity_metrics = self._get_complexity_metrics(code_analysis)
        functions_list = self._get_functions_list(code_analysis)
        data_structures = self._get_data_structures(code_analysis)

        # Calculate totals for metadata
        total_files = len(files)
        total_lines = sum(file_info.get('lines', 0) for file_info in files.values())
        total_functions = sum(len(file_info.get('functions', [])) for file_info in files.values())
        total_classes = sum(len(file_info.get('classes', [])) for file_info in files.values())
        languages = set(file_info.get('language', 'unknown') for file_info in files.values() if file_info.get('language') != 'unknown')

        return StoryboardScene(
            id=scene_id,
            concept="Language Distribution Analysis",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The codebase uses {len(language_counts)} different programming languages. This multi-language approach allows for optimal performance and functionality across different components of the system.",
            duration=12.0,
            camera_movement=CameraMovement(phi=45.0, theta=0.0, zoom=1.5, duration=2.0),
            metadata={
                'files': total_files,
                'languages': list(languages),
                'lines_of_code': total_lines,
                'functions': total_functions,
                'classes': total_classes,
                'file_structure': file_structure,
                'complexity': complexity_metrics,
                'functions_list': functions_list,
                'data_structures': data_structures
            }
        )

    def _create_detailed_complexity_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create detailed code complexity analysis scene."""
        files = code_analysis.get('files', {})

        # Calculate complexity metrics
        total_complexity = 0
        max_complexity = 0
        complex_functions = 0

        for file_info in files.values():
            for func in file_info.get('functions', []):
                complexity = func.get('complexity', 1)
                total_complexity += complexity
                max_complexity = max(max_complexity, complexity)
                if complexity > 5:
                    complex_functions += 1

        avg_complexity = total_complexity / max(1, sum(len(file_info.get('functions', [])) for file_info in files.values()))

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "📊 Code Complexity Analysis", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="bar_chart",
                properties={"data": {"Average": avg_complexity, "Maximum": max_complexity}, "height": 2.0},
                position={"x": 0, "y": 0, "z": 0},
                color="#FF6B6B"
            ),
            VisualElement(
                type="text",
                properties={"text": f"🔍 Average Complexity: {avg_complexity:.1f}", "font_size": 24},
                position={"x": -4, "y": -1.5, "z": 0},
                color="#4CAF50"
            ),
            VisualElement(
                type="text",
                properties={"text": f"⚠️ Complex Functions: {complex_functions}", "font_size": 24},
                position={"x": 4, "y": -1.5, "z": 0},
                color="#FF9800"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "📊 Code Complexity Analysis"}),
            AnimationStep("Create", "bar_chart", 3.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🔍 Average"}),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "⚠️ Complex"}),
            AnimationStep("Scale", "bar_chart", 2.0, parameters={"scale": 1.1})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Code Complexity & Maintainability",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The codebase has an average cyclomatic complexity of {avg_complexity:.1f}, with {complex_functions} functions exceeding the recommended complexity threshold. This indicates areas that may benefit from refactoring for better maintainability.",
            duration=12.0,
            camera_movement=CameraMovement(phi=60.0, theta=-45.0, zoom=1.3, duration=2.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_call_graph_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create function call graph visualization scene."""
        files = code_analysis.get('files', {})

        # Build call graph
        call_graph = {}
        function_nodes = []

        for file_path, file_info in files.items():
            for func in file_info.get('functions', []):
                func_name = f"{file_path.split('/')[-1]}.{func.get('name', 'unknown')}"
                calls = func.get('calls', [])
                call_graph[func_name] = calls
                function_nodes.append(func_name)

        # Create visual elements
        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "🕸️ Function Call Graph", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="graph",
                properties={"nodes": function_nodes[:10], "edges": call_graph, "layout": "force_directed"},
                position={"x": 0, "y": 0, "z": 0},
                color="#9C27B0"
            ),
            VisualElement(
                type="text",
                properties={"text": f"🔗 {len(function_nodes)} Functions Connected", "font_size": 24},
                position={"x": 0, "y": -2.5, "z": 0},
                color="#2196F3"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "🕸️ Function Call Graph"}),
            AnimationStep("Create", "graph", 4.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🔗 Functions"}),
            AnimationStep("Animate", "graph", 3.0, parameters={"animation": "pulse"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Function Call Relationships",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The function call graph shows the relationships between {len(function_nodes)} functions across the codebase. This visualization helps understand the dependencies and coupling between different components of the system.",
            duration=12.0,
            camera_movement=CameraMovement(phi=75.0, theta=0.0, zoom=1.2, duration=3.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_ast_visualization_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create AST (Abstract Syntax Tree) visualization scene."""
        files = code_analysis.get('files', {})

        # Find a Python file for AST visualization
        python_file = None
        for file_path, file_info in files.items():
            if file_info.get('language') == 'python' and file_info.get('functions'):
                python_file = file_path
                break

        if not python_file:
            python_file = list(files.keys())[0] if files else "unknown"

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "🌳 Abstract Syntax Tree (AST)", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="tree",
                properties={"root": "Module", "children": ["FunctionDef", "ClassDef", "Import"], "depth": 4},
                position={"x": 0, "y": 0, "z": 0},
                color="#4CAF50"
            ),
            VisualElement(
                type="text",
                properties={"text": f"📄 Analyzing: {python_file.split('/')[-1]}", "font_size": 20},
                position={"x": 0, "y": -2.5, "z": 0},
                color="#FF9800"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "🌳 Abstract Syntax Tree (AST)"}),
            AnimationStep("Create", "tree", 4.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "📄 Analyzing"}),
            AnimationStep("Traverse", "tree", 3.0, parameters={"direction": "depth_first"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Code Structure Analysis",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="The Abstract Syntax Tree shows the hierarchical structure of the code. Each node represents a different syntactic element, from modules and classes down to individual statements and expressions. This tree structure is fundamental to understanding how the code is parsed and executed.",
            duration=12.0,
            camera_movement=CameraMovement(phi=60.0, theta=-30.0, zoom=1.4, duration=2.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_execution_flow_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create algorithm execution flow visualization scene."""
        files = code_analysis.get('files', {})

        # Find algorithms in the codebase
        algorithms = []
        for file_info in files.values():
            for func in file_info.get('functions', []):
                func_name = func.get('name', '').lower()
                if any(algo in func_name for algo in ['sort', 'search', 'traverse', 'compute', 'calculate']):
                    algorithms.append(func.get('name', 'unknown'))

        if not algorithms:
            algorithms = ['main', 'process', 'execute']

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "⚡ Algorithm Execution Flow", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="flowchart",
                properties={"steps": algorithms[:6], "connections": "sequential"},
                position={"x": 0, "y": 0, "z": 0},
                color="#E91E63"
            ),
            VisualElement(
                type="text",
                properties={"text": "🔄 Step-by-step execution visualization", "font_size": 20},
                position={"x": 0, "y": -2.5, "z": 0},
                color="#607D8B"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "⚡ Algorithm Execution Flow"}),
            AnimationStep("Create", "flowchart", 4.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🔄 Step-by-step"}),
            AnimationStep("Animate", "flowchart", 4.0, parameters={"animation": "flow"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Algorithm Execution Visualization",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="This execution flow shows how algorithms in the codebase process data step by step. Each node represents a function or operation, and the arrows show the control flow between different parts of the system.",
            duration=12.0,
            camera_movement=CameraMovement(phi=45.0, theta=-45.0, zoom=1.3, duration=2.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_detailed_data_structure_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create detailed data structure visualization scene."""
        files = code_analysis.get('files', {})

        # Analyze data structures used
        data_structures = set()
        for file_info in files.values():
            for func in file_info.get('functions', []):
                # Look for data structure patterns in function names and calls
                func_name = func.get('name', '').lower()
                if any(ds in func_name for ds in ['array', 'list', 'tree', 'graph', 'stack', 'queue', 'hash', 'map']):
                    data_structures.add(func_name.split('_')[0])

        if not data_structures:
            data_structures = {'array', 'list', 'tree'}

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "🏗️ Data Structure Visualization", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            )
        ]

        # Add different data structure visualizations
        x_positions = [-3, 0, 3]
        for i, ds in enumerate(list(data_structures)[:3]):
            visual_elements.append(VisualElement(
                type=ds,
                properties={"size": 1.5, "values": [1, 2, 3, 4, 5]},
                position={"x": x_positions[i], "y": 0, "z": 0},
                color="#FF6B6B" if i == 0 else "#4CAF50" if i == 1 else "#2196F3"
            ))

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "🏗️ Data Structure Visualization"}),
            AnimationStep("Create", "array", 2.0),
            AnimationStep("Create", "tree", 2.0),
            AnimationStep("Create", "graph", 2.0),
            AnimationStep("Animate", "array", 2.0, parameters={"animation": "sort"}),
            AnimationStep("Animate", "tree", 2.0, parameters={"animation": "traverse"}),
            AnimationStep("Animate", "graph", 2.0, parameters={"animation": "pathfinding"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Data Structure Analysis",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The codebase utilizes various data structures including {', '.join(data_structures)}. Each data structure is optimized for specific operations and use cases within the system.",
            duration=15.0,
            camera_movement=CameraMovement(phi=60.0, theta=0.0, zoom=1.5, duration=3.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_performance_analysis_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create performance analysis scene."""
        files = code_analysis.get('files', {})

        # Calculate performance metrics
        total_functions = sum(len(file_info.get('functions', [])) for file_info in files.values())
        avg_function_length = sum(
            func.get('line_end', 0) - func.get('line_start', 0)
            for file_info in files.values()
            for func in file_info.get('functions', [])
        ) / max(1, total_functions)

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "📈 Performance Analysis", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="performance_chart",
                properties={"metrics": {"Functions": total_functions, "Avg Length": avg_function_length}},
                position={"x": 0, "y": 0, "z": 0},
                color="#FF9800"
            ),
            VisualElement(
                type="text",
                properties={"text": "⚡ Performance optimization insights", "font_size": 20},
                position={"x": 0, "y": -2.5, "z": 0},
                color="#607D8B"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "📈 Performance Analysis"}),
            AnimationStep("Create", "performance_chart", 3.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "⚡ Performance"}),
            AnimationStep("Animate", "performance_chart", 3.0, parameters={"animation": "grow"})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Performance & Optimization",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"Performance analysis reveals {total_functions} functions with an average length of {avg_function_length:.1f} lines. These metrics help identify opportunities for optimization and refactoring.",
            duration=10.0,
            camera_movement=CameraMovement(phi=45.0, theta=-30.0, zoom=1.4, duration=2.0),
            metadata=self._get_scene_metadata(code_analysis)
        )

    def _create_detailed_summary_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create detailed summary scene with insights."""
        files = code_analysis.get('files', {})
        total_files = len(files)

        # Calculate insights
        languages = set()
        total_lines = 0
        functions = 0
        classes = 0

        for file_info in files.values():
            languages.add(file_info.get('language', 'unknown'))
            total_lines += file_info.get('lines', 0)
            functions += len(file_info.get('functions', []))
            classes += len(file_info.get('classes', []))

        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": "🎯 Repository Analysis Summary", "font_size": 42},
                position={"x": 0, "y": 3, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="summary_dashboard",
                properties={
                    "files": total_files,
                    "languages": len(languages),
                    "lines": total_lines,
                    "functions": functions,
                    "classes": classes
                },
                position={"x": 0, "y": 0, "z": 0},
                color="#1f77b4"
            ),
            VisualElement(
                type="text",
                properties={"text": "🚀 Ready for Production", "font_size": 28},
                position={"x": 0, "y": -2.5, "z": 0},
                color="#4CAF50"
            )
        ]

        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.0, parameters={"target": "🎯 Repository Analysis Summary"}),
            AnimationStep("Create", "summary_dashboard", 4.0),
            AnimationStep("FadeIn", "text", 0.5, parameters={"target": "🚀 Ready"}),
            AnimationStep("Scale", "summary_dashboard", 2.0, parameters={"scale": 1.1})
        ]

        return StoryboardScene(
            id=scene_id,
            concept="Comprehensive Analysis Summary",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"This comprehensive analysis has revealed a well-structured codebase with {total_files} files across {len(languages)} languages, containing {total_lines:,} lines of code. The system demonstrates good architectural patterns with {functions} functions and {classes} classes, making it maintainable and scalable for future development.",
            duration=15.0,
            camera_movement=CameraMovement(phi=75.0, theta=-45.0, zoom=1.2, duration=3.0),
            metadata=self._get_scene_metadata(code_analysis)
        )
