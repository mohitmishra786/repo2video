"""repo2video -- Turn any GitHub repository into a narrated code walkthrough video."""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components


def _generate_subtitles(storyboard, output_dir: str) -> str:
    """Generate SRT subtitles from storyboard narration."""
    try:
        import pysrt

        subs = pysrt.SubRipFile()
        start_ms = 0
        for scene in storyboard.scenes:
            if not scene.narration:
                continue
            duration_ms = int(scene.duration * 1000)
            end_ms = start_ms + duration_ms
            sub = pysrt.SubRipItem(
                index=scene.id,
                start=pysrt.SubRipTime(milliseconds=start_ms),
                end=pysrt.SubRipTime(milliseconds=end_ms),
                text=scene.narration[:120],
            )
            subs.append(sub)
            start_ms = end_ms

        srt_path = os.path.join(output_dir, "subtitles.srt")
        subs.save(srt_path, encoding="utf-8")
        return srt_path
    except ImportError:
        return ""
    except Exception:
        return ""


def _convert_to_webm(mp4_path: str, output_dir: str) -> str:
    """Convert MP4 to WebM using ffmpeg."""
    webm_path = os.path.join(output_dir, "output.webm")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", mp4_path, "-c:v", "libvpx-vp9",
                "-b:v", "1M", "-c:a", "libopus", webm_path, "-y",
            ],
            check=True, capture_output=True, text=True, timeout=300,
        )
        return webm_path
    except Exception:
        return mp4_path


def _convert_to_gif(mp4_path: str, output_dir: str) -> str:
    """Convert MP4 to GIF using ffmpeg."""
    gif_path = os.path.join(output_dir, "output.gif")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", mp4_path, "-vf",
                "fps=10,scale=640:-1:flags=lanczos", "-loop", "0",
                gif_path, "-y",
            ],
            check=True, capture_output=True, text=True, timeout=300,
        )
        return gif_path
    except Exception:
        return mp4_path

st.set_page_config(page_title="repo2video", layout="centered")

# Dark mode toggle via theme config
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.title("repo2video")
st.caption("Paste a GitHub URL -- Get a narrated code walkthrough video in minutes.")

with st.form("main_form"):
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/psf/requests",
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        video_length = st.selectbox("Video length", ["short", "medium", "long"], index=1)
    with col2:
        language = st.selectbox("Language", ["en", "es", "fr", "de", "ja"], index=0)
    with col3:
        resolution = st.selectbox("Resolution", ["720p", "1080p"], index=1)
    with col4:
        output_format = st.selectbox("Format", ["mp4", "webm", "gif"], index=0)
    submitted = st.form_submit_button("Generate Video", type="primary", use_container_width=True)

if submitted and repo_url:
    output_dir = Path(tempfile.mkdtemp(prefix="repo2video_"))
    repo_dir = Path(tempfile.mkdtemp(prefix="repo_clone_"))
    video_path = None
    subtitle_path = None

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
            st.write(f"[OK] Cloned `{url.split('/')[-1]}`")

            st.write("**2/5** Analyzing code...")
            from code_analysis import EnhancedCodeAnalyzer  # noqa: E402

            analyzer = EnhancedCodeAnalyzer(str(repo_dir))
            code_analysis = analyzer.analyze_project()
            file_count = len(code_analysis.get("files", {}))
            st.write(f"[OK] Analyzed {file_count} files")

            st.write("**3/5** Generating storyboard...")
            from advanced_animation import AdvancedAnimationSystem  # noqa: E402

            system = AdvancedAnimationSystem(output_dir=str(output_dir))
            storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
            scene_count = len(storyboard.scenes)
            st.write(f"[OK] Generated {scene_count} scenes ({storyboard.total_duration:.0f}s)")

            st.write(f"**4/5** Rendering {scene_count} scenes with audio...")
            progress_bar = st.progress(0)
            st.write("  This may take a few minutes -- gTTS narration will be used if no ElevenLabs key is set.")

            # Generate audio with progress
            st.write("  - Generating audio narration...")
            progress_bar.progress(10)
            audio_files = system.audio_generator.generate_storyboard_audio(storyboard, str(output_dir))
            st.write(f"    [OK] Generated audio for {len(audio_files)} scenes")

            # Generate subtitles
            st.write("  - Generating subtitles...")
            progress_bar.progress(20)
            subtitle_path = _generate_subtitles(storyboard, str(output_dir))

            # Render scenes with progress
            rendered = []
            for idx, scene in enumerate(storyboard.scenes):
                pct = 20 + int(60 * (idx + 1) / scene_count)
                progress_bar.progress(pct)
                st.write(f"  - Rendering scene {idx + 1}/{scene_count}: {scene.concept[:60]}...")
                try:
                    scene_path = system.scene_renderer.render_scene(scene)
                    rendered.append(scene_path)
                except Exception:
                    scene_path = system.scene_renderer.create_fallback_video(scene)
                    rendered.append(scene_path)

            progress_bar.progress(85)

            # Merge and convert format
            if output_format == "mp4":
                video_path = system.video_merger.merge_scenes(rendered)
            elif output_format == "webm":
                mp4_path = system.video_merger.merge_scenes(rendered)
                video_path = _convert_to_webm(mp4_path, str(output_dir))
            elif output_format == "gif":
                mp4_path = system.video_merger.merge_scenes(rendered)
                video_path = _convert_to_gif(mp4_path, str(output_dir))

            progress_bar.progress(100)
            progress_bar.empty()

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
            mime_map = {"mp4": "video/mp4", "webm": "video/webm", "gif": "image/gif"}
            ext_map = {"mp4": "mp4", "webm": "webm", "gif": "gif"}
            with open(video_path, "rb") as f:
                st.download_button(
                    "Download Video",
                    f,
                    file_name=f"{repo_url.split('/')[-1]}_walkthrough.{ext_map.get(output_format, 'mp4')}",
                    mime=mime_map.get(output_format, "video/mp4"),
                    use_container_width=True,
                )
        with col2:
            replay_cmd = (
                f"python test_real_repository.py {repo_url} "
                f"--length {video_length} --language {language} --quality {resolution}"
            )
            st.code(replay_cmd, language="bash")
            # Copy-to-clipboard button via JS
            components.html(
                f"""<button onclick="navigator.clipboard.writeText('{replay_cmd}')"
                style="padding:6px 12px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;
                border-radius:6px;cursor:pointer;font-size:13px;width:100%;margin-top:4px">
                Copy command to clipboard</button>""",
                height=40,
            )

        if subtitle_path and Path(subtitle_path).exists():
            with open(subtitle_path, "r") as f:
                st.download_button(
                    "Download Subtitles (.srt)",
                    f,
                    file_name=f"{repo_url.split('/')[-1]}_subtitles.srt",
                    mime="text/plain",
                    use_container_width=True,
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

