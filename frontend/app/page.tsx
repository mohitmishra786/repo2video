'use client';

import { useState, useCallback, useRef } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StoryboardScene {
  id: number;
  concept: string;
  narration: string;
  duration: number;
  code_snippet: string | null;
}

interface JobState {
  job_id: string | null;
  status: 'idle' | 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  video_url: string | null;
  storyboard: StoryboardScene[] | null;
  error: string | null;
}

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('');
  const [length, setLength] = useState('medium');
  const [language, setLanguage] = useState('en');
  const [resolution, setResolution] = useState('1080p');
  const [format, setFormat] = useState('mp4');
  const [job, setJob] = useState<JobState>({
    job_id: null, status: 'idle', progress: 0, message: '',
    video_url: null, storyboard: null, error: null,
  });
  const [editingScene, setEditingScene] = useState<number | null>(null);
  const [editText, setEditText] = useState('');
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback((jobId: string) => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status/${jobId}`);
        const data = await res.json();
        setJob({
          job_id: data.job_id,
          status: data.status,
          progress: data.progress,
          message: data.message,
          video_url: data.video_path ? `${API_BASE}/api/download/${jobId}` : null,
          storyboard: data.storyboard || null,
          error: data.error || null,
        });
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, 1000);
  }, [stopPolling]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl) return;

    setJob({
      job_id: null, status: 'queued', progress: 0, message: 'Starting...',
      video_url: null, storyboard: null, error: null,
    });

    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, length, language, resolution, format }),
      });
      const data = await res.json();
      setJob(prev => ({ ...prev, job_id: data.job_id, status: 'running', message: 'Processing...' }));
      startPolling(data.job_id);
    } catch (err: any) {
      setJob(prev => ({
        ...prev, status: 'failed',
        error: `Cannot connect to backend at ${API_BASE}. Make sure the API server is running.`,
      }));
    }
  };

  const handleUpdateNarration = async (sceneId: number) => {
    if (!job.job_id || !job.storyboard) return;
    const updated = job.storyboard.map(s =>
      s.id === sceneId ? { ...s, narration: editText } : s
    );
    setJob(prev => ({ ...prev, storyboard: updated }));
    setEditingScene(null);
    try {
      await fetch(`${API_BASE}/api/storyboard/${job.job_id}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([{ id: sceneId, narration: editText }]),
      });
    } catch {}
  };

  const reset = () => {
    stopPolling();
    setJob({
      job_id: null, status: 'idle', progress: 0, message: '',
      video_url: null, storyboard: null, error: null,
    });
  };

  return (
    <main className="max-w-3xl mx-auto px-4 py-8 sm:py-16">
      <h1 className="text-3xl sm:text-4xl font-bold text-[#58a6ff] mb-2">repo2video</h1>
      <p className="text-[#8b949e] mb-8 text-sm sm:text-base">
        Paste a GitHub URL &mdash; Get a narrated code walkthrough video in minutes.
      </p>

      {job.status === 'idle' || job.status === 'failed' ? (
        <form onSubmit={handleGenerate} className="space-y-4">
          <input
            type="url"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            placeholder="https://github.com/psf/requests"
            className="w-full p-3 rounded-lg border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-sm focus:border-[#58a6ff] focus:outline-none"
            required
          />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <select value={length} onChange={e => setLength(e.target.value)}
              className="p-3 rounded-lg border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-sm">
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
            <select value={language} onChange={e => setLanguage(e.target.value)}
              className="p-3 rounded-lg border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-sm">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="ja">Japanese</option>
            </select>
            <select value={resolution} onChange={e => setResolution(e.target.value)}
              className="p-3 rounded-lg border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-sm">
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
            </select>
            <select value={format} onChange={e => setFormat(e.target.value)}
              className="p-3 rounded-lg border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-sm">
              <option value="mp4">MP4</option>
              <option value="webm">WebM</option>
              <option value="gif">GIF</option>
            </select>
          </div>
          <button type="submit" disabled={!repoUrl || job.status === 'running'}
            className="w-full p-4 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 disabled:cursor-not-allowed
                       text-white font-semibold rounded-lg transition-colors text-sm">
            Generate Video
          </button>
          {job.error && (
            <div className="p-4 bg-[#490202] border border-[#f85149] rounded-lg text-sm text-[#f85149]">
              {job.error}
            </div>
          )}
        </form>
      ) : (
        <div className="space-y-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">{job.message}</span>
              <span className="text-xs text-[#8b949e]">{job.progress}%</span>
            </div>
            <div className="w-full bg-[#0d1117] rounded-full h-2">
              <div className="bg-[#238636] h-2 rounded-full transition-all duration-500"
                   style={{ width: `${job.progress}%` }} />
            </div>
          </div>

          {job.storyboard && job.storyboard.length > 0 && job.status === 'running' && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-3">Storyboard Preview</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {job.storyboard.map(scene => (
                  <div key={scene.id} className="border border-[#30363d] rounded p-3">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs text-[#58a6ff] font-medium">Scene {scene.id}</span>
                      <span className="text-xs text-[#8b949e]">{scene.duration}s</span>
                    </div>
                    <p className="text-sm font-medium mb-1">{scene.concept}</p>
                    {editingScene === scene.id ? (
                      <div className="space-y-2">
                        <textarea value={editText} onChange={e => setEditText(e.target.value)}
                          className="w-full p-2 rounded border border-[#30363d] bg-[#0d1117] text-[#c9d1d9] text-xs"
                          rows={3} />
                        <div className="flex gap-2">
                          <button onClick={() => handleUpdateNarration(scene.id)}
                            className="px-3 py-1 bg-[#238636] text-white rounded text-xs">Save</button>
                          <button onClick={() => setEditingScene(null)}
                            className="px-3 py-1 bg-[#21262d] text-[#c9d1d9] rounded text-xs">Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-[#8b949e]">
                        {scene.narration?.substring(0, 100)}
                        {scene.narration?.length > 100 ? '...' : ''}
                      </p>
                    )}
                    {editingScene !== scene.id && (
                      <button onClick={() => {
                        setEditingScene(scene.id);
                        setEditText(scene.narration || '');
                      }} className="text-xs text-[#58a6ff] mt-1 hover:underline">
                        Edit narration
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {job.status === 'completed' && job.video_url && (
            <div className="space-y-3">
              <div className="bg-[#161b22] border border-[#2ea043] rounded-lg p-4 text-center">
                <p className="text-sm font-medium text-[#2ea043] mb-3">Video ready!</p>
                <a href={job.video_url} download
                  className="inline-block px-6 py-3 bg-[#238636] hover:bg-[#2ea043] text-white font-semibold
                             rounded-lg transition-colors text-sm">
                  Download Video
                </a>
              </div>
            </div>
          )}

          <button onClick={reset}
            className="w-full p-3 bg-[#21262d] hover:bg-[#30363d] border border-[#30363d]
                       text-[#c9d1d9] rounded-lg transition-colors text-sm">
            Generate Another
          </button>
        </div>
      )}

      <footer className="mt-12 pt-8 border-t border-[#21262d] text-center text-xs text-[#484f58]">
        <p>repo2video is free and open source.</p>
        <p className="mt-1">
          <a href="https://github.com/mohitmishra786/repo2video" className="text-[#58a6ff] hover:underline">GitHub</a>
          {' '}&middot;{' '}
          <a href="https://discord.com/invite/2QWN9y3B9M" className="text-[#58a6ff] hover:underline">Discord</a>
        </p>
      </footer>
    </main>
  );
}
