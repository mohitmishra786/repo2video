#!/usr/bin/env python3
"""
Test Real Repository Animation

This script tests our ManimGL system with real GitHub repositories
to generate animations from actual code.
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import logging utilities
from advanced_animation.utils.logging_config import setup_logging_for_run, get_logger

# Setup logging for this run
logging_manager = setup_logging_for_run("logs", logging.INFO)
logger = get_logger(__name__)

from advanced_animation import AdvancedAnimationSystem
from code_analysis import EnhancedCodeAnalyzer
from repo_fetcher import RepoFetcher
import tempfile
import subprocess

def fetch_repository(repo_url: str) -> str:
    """Wrapper function to fetch a repository."""
    # Create a temporary directory for the repository
    temp_dir = tempfile.mkdtemp(prefix="repo_")
    
    # Clone the repository using git
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to clone repository: {e}")

def analyze_repository(repo_path: str):
    """Wrapper function to analyze a repository."""
    analyzer = EnhancedCodeAnalyzer(repo_path)
    return analyzer.analyze_project()

def analyze_github_repo(repo_url: str, output_dir: str = "real_repo_output", theme: str = "light", 
                       length: str = "medium", focus: str = "all", language: str = "en", 
                       quality: str = "1080p", mobile: bool = False):
    """Analyze a GitHub repository and create animations."""
    print(f"Testing Real Repository: {repo_url}")
    print("=" * 60)
    
    # Log customization options
    print(f"Customization options:")
    print(f"  Theme: {theme}")
    print(f"  Length: {length}")
    print(f"  Focus: {focus}")
    print(f"  Language: {language}")
    print(f"  Quality: {quality}")
    print(f"  Mobile optimized: {mobile}")
    
    try:
        # Initialize the advanced animation system
        system = AdvancedAnimationSystem(output_dir=output_dir)
        
        # Fetch and analyze the repository
        print("📥 Fetching repository...")
        repo_path = fetch_repository(repo_url)
        print(f"✅ Repository fetched to: {repo_path}")
        
        print("\n🔍 Analyzing repository...")
        code_analysis = analyze_repository(repo_path)
        print(f"✅ Analysis complete: {len(code_analysis.get('files', []))} files analyzed")
        
        # Show analysis summary
        print("\n📊 Analysis Summary:")
        print(f"   Total files: {len(code_analysis.get('files', []))}")
        print(f"   Languages: {code_analysis.get('languages', [])}")
        print(f"   Total lines: {code_analysis.get('total_lines', 0)}")
        
        # Show detailed file analysis
        files = code_analysis.get('files', {})
        if files:
            print(f"\n📁 Detailed File Analysis ({len(files)} files):")
            
            successful_files = 0
            failed_files = 0
            
            for i, (file_path, file_info) in enumerate(files.items()):
                language = file_info.get('language', 'Unknown')
                lines = file_info.get('lines', 0)
                functions = len(file_info.get('functions', []))
                classes = len(file_info.get('classes', []))
                has_error = 'analysis_error' in file_info
                
                if has_error:
                    failed_files += 1
                    print(f"   ❌ {i+1}. {file_path} ({language}) - {lines} lines, {functions} functions, {classes} classes")
                    print(f"      Error: {file_info.get('analysis_error', 'Unknown error')}")
                else:
                    successful_files += 1
                    print(f"   ✅ {i+1}. {file_path} ({language}) - {lines} lines, {functions} functions, {classes} classes")
            
            print(f"\n📈 Analysis Results:")
            print(f"   ✅ Successfully analyzed: {successful_files} files")
            print(f"   ❌ Failed to analyze: {failed_files} files")
            print(f"   📊 Success rate: {(successful_files/len(files)*100):.1f}%")
        
        # Generate storyboard
        print("\n🎬 Generating storyboard...")
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        print(f"✅ Generated storyboard with {len(storyboard.scenes)} scenes")
        print(f"   Total duration: {storyboard.total_duration}s")
        
        # Show scene details
        print("\n🎭 Scenes:")
        for i, scene in enumerate(storyboard.scenes):
            print(f"   Scene {i+1}: {scene.concept} ({scene.duration}s)")
        
        # Save storyboard
        storyboard_path = system.save_storyboard(storyboard, f"{repo_url.split('/')[-1]}_storyboard.json")
        print(f"\n💾 Saved storyboard to: {storyboard_path}")
        
        # Create animations with audio generation
        print("\n🎥 Creating animations with audio...")
        print("   This may take several minutes...")
        
        try:
            # Use the full animation system which includes audio generation
            final_video_path = system.create_animation_from_code(code_analysis)
            print(f"   ✅ Complete animation created: {final_video_path}")
            return True
        except Exception as e:
            print(f"   ❌ Animation creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"\n🎉 Animation creation completed!")
        print(f"📁 Check the '{output_dir}' directory for:")
        print(f"   - {repo_url.split('/')[-1]}_storyboard.json (storyboard data)")
        print(f"   - Generated individual scene videos")
        print(f"   - final_video/ (merged comprehensive video)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing repository: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test ManimGL system with real repositories")
    parser.add_argument("repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--output", "-o", default="real_repo_output", 
                       help="Output directory (default: real_repo_output)")
    parser.add_argument("--theme", choices=["light", "dark", "system"], default="light", help="Theme for animations")
    parser.add_argument("--length", choices=["short", "medium", "long"], default="medium", help="Video length")
    parser.add_argument("--focus", choices=["all", "tests", "core", "docs"], default="all", help="Focus area")
    parser.add_argument("--language", default="en", help="Language for narration")
    parser.add_argument("--quality", choices=["720p", "1080p", "4k"], default="1080p", help="Video quality")
    parser.add_argument("--mobile", action="store_true", help="Optimize for mobile devices")
    
    args = parser.parse_args()
    
    # Validate repository URL
    if not args.repo_url.startswith("https://github.com/"):
        print("Please provide a valid GitHub repository URL")
        print("   Example: https://github.com/user/repo")
        return
    
    # Process the repository
    success = analyze_github_repo(
        args.repo_url, 
        args.output,
        theme=args.theme,
        length=args.length,
        focus=args.focus,
        language=args.language,
        quality=args.quality,
        mobile=args.mobile
    )
    
    if success:
        print("\nRepository animation test completed successfully!")
        print("\nNext steps:")
        print("- Check the output directory for generated videos")
        print("- Review the storyboard JSON file")
        print("- Try different repositories to see various animation styles")
    else:
        print("\nRepository animation test failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()