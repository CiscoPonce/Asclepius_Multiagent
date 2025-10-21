# Multi-Agent System - Complete Backup Inventory

**Backup Date**: October 21, 2025, 23:18 UTC  
**Source**: `user@raspberry-pi:/home/user/multiagent/`  
**Destination**: `/home/cisco/Documents/AWS/multiagent_backup/`  
**Total Size**: 244 MB (including Python virtual environment)

---

## 📁 Directory Structure

```
multiagent_backup/
├── agent_env/              # Python virtual environment (244 MB)
│   ├── bin/
│   ├── lib/
│   └── pyvenv.cfg
├── agents/                 # Future agent modules (empty)
├── backend/                # FastAPI backend (104 KB)
│   ├── main.py            # Main backend application (43 KB)
│   └── __pycache__/
├── frontend/               # Web interface (48 KB)
│   └── index.html         # Mobile-optimized frontend (41 KB)
├── tools/                  # Future tools directory (empty)
├── backend.log            # Backend logs
├── README.md              # Project documentation
├── PROJECT_STATUS.md      # Detailed project status (12 KB)
├── DOCLING_INTEGRATION_STATUS.md  # DocTags integration notes (8 KB)
├── SEARXNG_SETUP_STATUS.md        # SearXNG setup guide (4 KB)
├── setup_multiagent.sh    # Initial setup script
├── start_backend.sh       # Backend startup script
├── start_frontend.sh      # Frontend startup script
└── start_multiagent.sh    # Master control script (8 KB)
```

---

## 🔑 Key Files

### Backend (`backend/main.py`)
- **Size**: 43 KB
- **Lines**: ~1,025 lines of Python
- **Features**:
  - `AgentRouter`: Routes messages to appropriate agents
  - `DoclingAgent`: Document processing with DocTags parsing
  - `WebSearchAgent`: SearXNG + Brave Search API integration
  - FastAPI endpoints: `/upload`, `/chat`, `/health`, `/stats`, `/debug/last-doctags`
  - CORS middleware enabled
  - Session management with file uploads

### Frontend (`frontend/index.html`)
- **Size**: 41 KB  
- **Lines**: ~1,270 lines (HTML + CSS + JavaScript)
- **Features**:
  - Mobile-responsive design with hamburger menu
  - Dark theme UI
  - Chat history sidebar
  - File upload support
  - Auto-scrolling messages
  - Markdown rendering
  - Conversation deletion
  - Touch-optimized for mobile

### Control Scripts

#### `start_multiagent.sh` (Master Script)
- **Commands**: `start`, `stop`, `restart`, `status`
- **Manages**: Both backend and frontend services
- **Features**: Port checking, process management, colored output

#### `start_backend.sh`
- Activates virtual environment
- Starts FastAPI on port 9050

#### `start_frontend.sh`
- Starts Python HTTP server on port 9051

---

## 🐍 Python Dependencies (in `agent_env/`)

### Core Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variables
- `docling-core` - DocTags parsing
- `pillow` - Image processing
- `pyyaml` - YAML support

### Total Size
- Virtual environment: 244 MB
- Includes all dependencies and their sub-dependencies

---

## 🚀 Deployment Information

### Running Services on Raspberry Pi
| Service | Port | Status |
|---------|------|--------|
| Backend (FastAPI) | 9050 | ✅ Running |
| Frontend (HTTP) | 9051 | ✅ Running |
| Ollama | 11434 | ✅ Running |
| SearXNG | 8888 | ✅ Running |

### Models Used
- **Router**: `qwen3:0.6b` (Ollama)
- **Document Processing**: `gabegoodhart/granite-docling:258M` (Ollama)
- **Search**: SearXNG (primary), Brave Search API (fallback)

### Environment Variables (`.env` - not backed up)
- `BRAVE_API_KEY`: BSA3F8eYWARl7OmAVLYA3Zu2Tvg6oub

---

## 📱 Mobile Optimization Features

### Responsive Design
- **Breakpoints**: 768px (mobile), 1024px (tablet)
- **Hamburger Menu**: Slide-out sidebar navigation
- **Touch Optimized**: Larger tap targets, smooth scrolling
- **iOS Compatible**: No zoom on input focus

### Key CSS Classes
- `.mobile-menu-btn` - Hamburger button
- `.mobile-overlay` - Dark overlay for open menu
- `.sidebar.mobile-open` - Active sidebar state
- Media queries for responsive behavior

---

## 🔧 How to Restore

### On Another Raspberry Pi or Linux System:

1. **Copy the backup**:
   ```bash
   scp -r multiagent_backup/ user@newhost:/home/user/multiagent/
   ```

2. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv docker.io
   ```

3. **Set up environment**:
   ```bash
   cd /home/user/multiagent
   echo "BRAVE_API_KEY=BSA3F8eYWARl7OmAVLYA3Zu2Tvg6oub" > .env
   ```

4. **Install Ollama and pull models**:
   ```bash
   # Install Ollama (or run in Docker)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull models
   ollama pull qwen3:0.6b
   ollama pull gabegoodhart/granite-docling:258M
   ```

5. **Set up SearXNG** (optional):
   ```bash
   # Follow SEARXNG_SETUP_STATUS.md for Docker setup
   ```

6. **Start services**:
   ```bash
   chmod +x start_multiagent.sh
   ./start_multiagent.sh start
   ```

7. **Access**:
   - Frontend: `http://your-ip:9051`
   - Backend API: `http://your-ip:9050`

---

## 📊 Statistics

- **Total Files**: 10,988
- **Transfer Size**: 60 MB (compressed)
- **Total Size**: 244 MB (uncompressed)
- **Backup Time**: ~3.5 seconds
- **Python Packages**: 100+ packages in virtual environment

---

## ✅ Verification

All critical files backed up:
- ✅ Backend application code
- ✅ Frontend HTML/CSS/JS
- ✅ Python virtual environment
- ✅ Startup scripts
- ✅ Documentation
- ✅ Configuration files

**Note**: The `.env` file was NOT backed up for security reasons. You'll need to recreate it with your API keys.

---

**Backup Status**: ✅ Complete and Verified  
**Backup Location**: `/home/cisco/Documents/AWS/multiagent_backup/`
