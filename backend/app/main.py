"""repo2video FastAPI backend -- async video generation API."""

import os
import sys
import tempfile
import subprocess
import shutil
import uuid
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

app = FastAPI(title="repo2video", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOBS: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    repo_url: str
    length: str = "medium"
    language: str = "en"
    resolution: str = "1080p"
    format: str = "mp4"


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    video_path: Optional[str] = None
    storyboard: Optional[list] = None
    error: Optional[str] = None


def _run_pipeline(job_id: str, req: GenerateRequest):
    """Run the full video generation pipeline in background."""
    job = JOBS.get(job_id)
    if not job:
        return
    job["status"] = "running"

    output_dir = Path(tempfile.mkdtemp(prefix="repo2video_"))
    repo_dir = Path(tempfile.mkdtemp(prefix="repo_clone_"))
    video_path = None
    storyboard_data = None

    try:
        url = req.repo_url.strip().rstrip("/")
        if not url.startswith("https://github.com/"):
            raise ValueError("Invalid GitHub URL")

        job["message"] = "Cloning repository..."
        job["progress"] = 5
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_dir)],
            check=True, capture_output=True, text=True, timeout=120,
        )

        job["message"] = "Analyzing code..."
        job["progress"] = 15
        from code_analysis import EnhancedCodeAnalyzer  # noqa: E402
        analyzer = EnhancedCodeAnalyzer(str(repo_dir))
        code_analysis = analyzer.analyze_project()

        job["message"] = "Generating storyboard..."
        job["progress"] = 30
        from advanced_animation import AdvancedAnimationSystem  # noqa: E402
        system = AdvancedAnimationSystem(output_dir=str(output_dir))
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)

        storyboard_data = [
            {
                "id": s.id, "concept": s.concept,
                "narration": s.narration, "duration": s.duration,
                "code_snippet": s.code_snippet,
            }
            for s in storyboard.scenes
        ]
        job["storyboard"] = storyboard_data

        job["message"] = "Generating audio..."
        job["progress"] = 40
        system.audio_generator.generate_storyboard_audio(storyboard, str(output_dir))

        job["message"] = f"Rendering {len(storyboard.scenes)} scenes..."
        job["progress"] = 50
        rendered = []
        for idx, scene in enumerate(storyboard.scenes):
            pct = 50 + int(40 * (idx + 1) / len(storyboard.scenes))
            job["progress"] = pct
            job["message"] = f"Rendering scene {idx + 1}/{len(storyboard.scenes)}: {scene.concept[:60]}"
            try:
                sp = system.scene_renderer.render_scene(scene)
            except Exception:
                sp = system.scene_renderer.create_fallback_video(scene)
            rendered.append(sp)

        job["message"] = "Merging final video..."
        job["progress"] = 90
        video_path = system.video_merger.merge_scenes(rendered)
        if req.format == "webm":
            webm = str(Path(output_dir) / "output.webm")
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-c:v", "libvpx-vp9", "-b:v", "1M", "-c:a", "libopus", webm, "-y"],
                check=True, capture_output=True, timeout=300,
            )
            video_path = webm
        elif req.format == "gif":
            gif = str(Path(output_dir) / "output.gif")
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-vf", "fps=10,scale=640:-1:flags=lanczos", "-loop", "0", gif, "-y"],
                check=True, capture_output=True, timeout=300,
            )
            video_path = gif

        job["status"] = "completed"
        job["progress"] = 100
        job["message"] = "Video ready!"
        job["video_path"] = video_path

    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"{type(e).__name__}: {e}"
        job["message"] = str(e)
    finally:
        shutil.rmtree(repo_dir, ignore_errors=True)


@app.post("/api/generate", response_model=JobStatus)
async def generate_video(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Starting...",
        "video_path": None,
        "storyboard": None,
        "error": None,
        "created_at": time.time(),
    }
    background_tasks.add_task(_run_pipeline, job_id, req)
    return JobStatus(**JOBS[job_id])


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JobStatus(**job)


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    job = JOBS.get(job_id)
    if not job or not job.get("video_path"):
        raise HTTPException(404, "Video not ready or job not found")
    path = job["video_path"]
    if not Path(path).exists():
        raise HTTPException(404, "Video file missing")
    return FileResponse(path, media_type="video/mp4", filename=Path(path).name)


@app.get("/api/storyboard/{job_id}")
async def get_storyboard(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"storyboard": job.get("storyboard", [])}


@app.post("/api/storyboard/{job_id}/update")
async def update_storyboard(job_id: str, scenes: list[dict]):
    """Update narration text in storyboard scenes before rendering."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.get("storyboard"):
        for update in scenes:
            for s in job["storyboard"]:
                if s["id"] == update.get("id"):
                    s["narration"] = update.get("narration", s["narration"])
                    break
    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"status": "ok", "jobs": len(JOBS)}
