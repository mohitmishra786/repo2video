# repo2video

Paste any GitHub URL → Get a 1080p narrated code walkthrough video in minutes. Open source. Free.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-pink)](https://github.com/sponsors/mohitmishra786)
[![Landing](https://img.shields.io/badge/site-mohitmishra786.github.io%2Frepo2video-blue)](https://mohitmishra786.github.io/repo2video/)

## Demo

*A demo video is coming soon. In the meantime, you can generate one yourself by running the tool on its own repository.*

## Features

- **Repository Fetching** — Clone and process any public GitHub repository
- **Code Analysis** — AST-based Python analysis with multi-language support
- **AI Storyboard Generation** — Automatically plan video scenes from code structure
- **Scene Rendering** — MoviePy-based video scene generation with code display and narration
- **Text-to-Speech** — Automatic narration via ElevenLabs (or gTTS fallback)
- **Progress feedback** — Per-scene progress bar during rendering
- **WebM/GIF support** — Output in MP4, WebM, or GIF formats
- **Subtitle export** — Automatic SRT subtitle generation from narration

## How It Works

```
GitHub URL → Clone → Code Analysis → Storyboard Generation → Scene Rendering + Audio → Final Video
```

1. **Clone**: Fetches the repository contents
2. **Analyze**: Parses code structure, identifies key files, functions, and classes
3. **Storyboard**: AI or rule-based planning of animation scenes
4. **Render**: Each scene becomes a video clip with code display, titles, and narration
5. **Merge**: All scenes are combined into a single comprehensive video

## Installation

```bash
git clone https://github.com/mohitmishra786/repo2video.git
cd repo2video
pip install -r requirements.txt
```

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 and paste a GitHub URL.

### Command Line

```bash
python test_real_repository.py https://github.com/psf/requests
```

### Options

```bash
python test_real_repository.py https://github.com/user/repo \
  --output my_videos \
  --theme dark \
  --length medium \
  --language en \
  --quality 1080p
```

## Configuration

Set API keys via environment variables (optional — gTTS fallback works without keys):

```bash
export ELEVENLABS_API_KEY=your_key        # Premium TTS voices
export GROQ_API_KEY=your_key               # AI storyboard generation
```

Place these in a `.env` file to load automatically.

> **Security Note**: repo2video processes code from GitHub repositories. Only analyze repositories you trust. See [SECURITY.md](SECURITY.md) for details.

## Requirements

- Python 3.9+
- FFmpeg (for video encoding)
- Git (for repository cloning)
- ~500MB disk space for dependencies

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

repo2video is free and open source. If you find it useful, consider [sponsoring the project](https://github.com/sponsors/mohitmishra786) to support ongoing development.

[Join our Discord](https://discord.com/invite/2QWN9y3B9M) for questions, help, and community discussion.

## Status

repo2video is in active early development. Expect rapid changes and occasional bugs. I maintain this in my spare time — updates every 2-4 weeks.

---

**repo2video** — Turn code into video, automatically.
