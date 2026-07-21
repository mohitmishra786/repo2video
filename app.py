"""repo2video — Turn any GitHub repository into a narrated code walkthrough video."""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(page_title="repo2video", page_icon="🎬", layout="centered")

theme = st.get_option("theme.base") if hasattr(st, "get_option") else "light"

st.title("repo2video")
st.caption("Paste a GitHub URL → Get a 1080p narrated code walkthrough video in minutes.")

with st.form("main_form"):
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/psf/requests",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        video_length = st.selectbox("Video length", ["short", "medium", "long"], index=1)
    with col2:
        language = st.selectbox("Narration language", ["en", "es", "fr", "de", "ja"], index=0)
    with col3:
        resolution = st.selectbox("Resolution", ["720p", "1080p"], index=1)
    submitted = st.form_submit_button("Generate Video", type="primary", use_container_width=True)

if submitted and repo_url:
    output_dir = Path(tempfile.mkdtemp(prefix="repo2video_"))
    repo_dir = Path(tempfile.mkdtemp(prefix="repo_clone_"))
    video_path = None

    with st.status("Processing repository...", expanded=True) as status:
        try:
            st.write("**1/5** Cloning repository...")
            url = repo_url.strip().rstrip("/")
            if not url.startswith("https://github.com/"):
                st.error("Please enter a valid GitHub URL, e.g. https://github.com/user/repo")
                st.stop()

            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(repo_dir)],
                check=True, capture_output=True, text=True, timeout=120,
            )
            st.write(f"✓ Cloned `{url.split('/')[-1]}`")

            st.write("**2/5** Analyzing code...")
            from code_analysis import EnhancedCodeAnalyzer

            analyzer = EnhancedCodeAnalyzer(str(repo_dir))
            code_analysis = analyzer.analyze_project()
            file_count = len(code_analysis.get("files", {}))
            st.write(f"✓ Analyzed {file_count} files")

            st.write("**3/5** Generating storyboard...")
            from advanced_animation import AdvancedAnimationSystem

            system = AdvancedAnimationSystem(output_dir=str(output_dir))
            storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
            scene_count = len(storyboard.scenes)
            st.write(f"✓ Generated {scene_count} scenes ({storyboard.total_duration:.0f}s)")

            st.write(f"**4/5** Rendering {scene_count} scenes with audio...")
            st.write("  This may take a few minutes — gTTS narration will be used if no ElevenLabs key is set.")
            video_path = system.create_animation_from_code(code_analysis)
            st.write("✓ Rendering complete")

            st.write("**5/5** Finalizing video...")
            if video_path and Path(video_path).exists():
                status.update(label="Video ready!", state="complete", expanded=False)
            else:
                status.update(label="Warning: No video output", state="error")
                st.error("Rendering completed but no video file was produced. Check the logs for details.")

        except subprocess.CalledProcessError as e:
            status.update(label="Clone failed", state="error")
            st.error(
                "Failed to clone the repository. Make sure:\n"
                "- The URL is correct\n"
                "- The repo is public (private repos not supported yet)\n"
                "- Git is installed and accessible\n\n"
                f"Error: `{e.stderr}`"
            )
        except ValueError as e:
            status.update(label="Invalid input", state="error")
            st.error(str(e))
        except ImportError as e:
            status.update(label="Missing dependency", state="error")
            st.error(
                f"Missing dependency: `{e}`\n\n"
                "Run `pip install -r requirements.txt` to install all dependencies.\n"
                "Also ensure FFmpeg is installed on your system."
            )
        except RuntimeError as e:
            if "ffmpeg" in str(e).lower():
                status.update(label="FFmpeg missing", state="error")
                st.error(
                    "FFmpeg is required for video encoding but was not found.\n\n"
                    "**macOS**: `brew install ffmpeg`\n"
                    "**Ubuntu**: `sudo apt install ffmpeg`\n"
                    "**Windows**: Download from https://ffmpeg.org"
                )
            else:
                status.update(label="Error", state="error")
                st.error(f"`{type(e).__name__}`: {e}")
        except Exception as e:
            status.update(label="Error", state="error")
            st.error(f"`{type(e).__name__}`: {e}")
        finally:
            shutil.rmtree(repo_dir, ignore_errors=True)

    if video_path and Path(video_path).exists():
        st.success(f"Generated: `{Path(video_path).name}`")
        col1, col2 = st.columns(2)
        with col1:
            with open(video_path, "rb") as f:
                st.download_button(
                    "Download Video",
                    f,
                    file_name=f"{repo_url.split('/')[-1]}_walkthrough.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )
        with col2:
            st.code(
                f"# Replay this generation\n"
                f"python test_real_repository.py {repo_url} "
                f"--length {video_length} --language {language} --quality {resolution}",
                language="bash",
            )

    shutil.rmtree(output_dir, ignore_errors=True)

elif submitted and not repo_url:
    st.warning("Please enter a GitHub repository URL.")

st.divider()
st.caption(
    "repo2video is free and open source. "
    "[Star on GitHub](https://github.com/mohitmishra786/repo2video) | "
    "[Report an issue](https://github.com/mohitmishra786/repo2video/issues)"
)
