# Multi-Agent System - Project Status

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Date**: October 21, 2025  
**Platform**: Raspberry Pi / Linux  
**Architecture**: Multi-Agent AI System with Router Pattern

---

## 📋 Project Overview

This is a **multi-agent AI system** that orchestrates specialized AI agents to handle different tasks intelligently. The system uses a **router agent** to analyze user requests and delegate them to the appropriate specialized agent (document processing, web search, or general chat).

### Key Capabilities

- 🤖 **Intelligent Agent Routing** - Automatically directs queries to the right agent
- 📄 **Document Processing** - OCR, table extraction, and content analysis
- 🔍 **Web Search** - Privacy-focused search with AI-powered synthesis
- 💬 **General Chat** - Conversational AI for general queries
- 📱 **Mobile-Optimized** - Responsive design for phones and tablets
- 🔌 **MCP Integration** - Extensible via Model Context Protocol

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Port 9051)                 │
│  • HTML/CSS/JavaScript                                   │
│  • Mobile-responsive UI with hamburger menu              │
│  • Real-time chat interface                              │
│  • File upload support                                   │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────────────────────┐
│              Backend API (Port 9050)                     │
│  • FastAPI / Uvicorn                                     │
│  • Agent Router (qwen3:0.6b)                            │
│  • Session Management                                    │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴───────┬─────────────┐
         ↓               ↓             ↓
    ┌────────┐    ┌──────────┐   ┌────────────┐
    │Docling │    │ Web      │   │  General   │
    │ Agent  │    │ Search   │   │  Chat      │
    │        │    │ Agent    │   │  Agent     │
    └────┬───┘    └────┬─────┘   └────────────┘
         │             │
         ↓             ↓
    ┌────────┐    ┌─────────┐
    │Granite │    │SearXNG  │
    │Docling │    │+ Brave  │
    │258M    │    │API      │
    └────────┘    └─────────┘
```

---

## 🤖 Agent System

### 1. **Agent Router** (Control Layer)
**Model**: `qwen3:0.6b` via Ollama  
**Purpose**: Intelligent request routing and orchestration

**Functions**:
- Analyzes user messages and context
- Routes to appropriate specialized agent
- Handles general conversation
- Explains system capabilities

**Routing Logic**:
```python
- Has file uploaded → DoclingAgent
- Keywords: "search", "find", "latest", "news" → WebSearchAgent
- Keywords: "analyze", "extract", "ocr" → DoclingAgent
- Keywords: "what can you do" → Capabilities explanation
- Default → General chat
```

### 2. **Docling Agent** (Document Processing)
**Model**: `gabegoodhart/granite-docling:258M` via Ollama  
**Purpose**: Document OCR, analysis, and structured data extraction

**Technologies**:
- **Granite-Docling Model**: Specialized vision-language model for document understanding
- **DocTags Format**: XML-like markup for structured document representation
- **docling-core**: Python library for parsing DocTags output

**DocTags Format Example**:
```xml
<doctag>
  <title>Document Title</title>
  <section_header_level_1>Section Name</section_header_level_1>
  <text>Paragraph content...</text>
  <otsl>
    <ched>Column 1<ched>Column 2<nl>
    <fcel>Cell 1<fcel>Cell 2<nl>
    <fcel>Cell 3<fcel>Cell 4<nl>
  </otsl>
</doctag>
```

**Capabilities**:
- ✅ Optical Character Recognition (OCR)
- ✅ Table extraction and formatting
- ✅ Document structure analysis
- ✅ Multi-prompt strategy for robust extraction
- ✅ Automatic content cleaning and formatting
- ✅ Intelligent summarization

**Supported Tags**:
- `<title>` - Document title
- `<section_header_level_N>` - Section headers (levels 1-6)
- `<text>` - Paragraph text
- `<otsl>` - Table structure
- `<ched>` - Table column header
- `<fcel>` - Table cell (first/regular cell)
- `<lcel>` - Table cell (last cell)
- `<nl>` - New line in table
- `<unordered_list>`, `<ordered_list>` - Lists
- `<list_item>` - List items

**Process Flow**:
1. User uploads image/PDF
2. Image converted to base64
3. Sent to Granite-Docling with minimal prompt
4. Model outputs DocTags XML
5. Parser extracts structured content
6. Formatted as markdown tables and text
7. Optional AI summarization using router model

### 3. **Web Search Agent** (Information Retrieval)
**Primary**: SearXNG (MCP-based, port 8888)  
**Fallback**: Brave Search API  
**Synthesis**: qwen3:0.6b

**Purpose**: Real-time information retrieval from the web

**Technologies**:
- **SearXNG**: Privacy-respecting metasearch engine
  - Self-hosted in Docker
  - Aggregates results from multiple search engines
  - No tracking or data collection
  - JSON API enabled
- **Brave Search API**: Commercial search fallback
  - API key: `BSA3F8eYWARl7OmAVLYA3Zu2Tvg6oub`
  - Used when SearXNG unavailable
- **AI Synthesis**: Router model analyzes and summarizes results

**Process Flow**:
1. User query analyzed for search intent
2. SearXNG queried (primary)
3. If SearXNG fails → Brave API (fallback)
4. Results collected (top 5)
5. AI synthesizes comprehensive answer
6. Formatted response with sources

---

## 🛠️ Technologies Stack

### **Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | Latest | Web framework |
| **Uvicorn** | Latest | ASGI server |
| **httpx** | Latest | Async HTTP client |
| **python-dotenv** | Latest | Environment management |
| **docling-core** | Latest | DocTags parsing |
| **Pillow (PIL)** | Latest | Image processing |
| **PyYAML** | Latest | YAML configuration |

### **Frontend**
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling (mobile-first) |
| **JavaScript (ES6+)** | Interactivity |
| **Fetch API** | Backend communication |
| **localStorage** | Client-side storage |

### **AI Models (via Ollama)**
| Model | Size | Purpose | Provider |
|-------|------|---------|----------|
| **qwen3:0.6b** | 600MB | Router agent, chat, synthesis | Qwen Team |
| **granite-docling:258M** | 258MB | Document OCR, DocTags generation | IBM / Docling Project |

### **External Services**
| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **Ollama** | 11434 | LLM inference server | ✅ Running |
| **SearXNG** | 8888 | Metasearch engine | ✅ Running (Docker) |
| **Backend API** | 9050 | FastAPI application | ✅ Running |
| **Frontend** | 9051 | Web interface | ✅ Running |

---

## 🔌 MCP Integration (Model Context Protocol)

### **Current MCP Implementation**

#### **MCP-SearXNG**
The system currently uses SearXNG as an MCP-compatible search provider:

**Implementation**:
```python
class WebSearchAgent:
    def __init__(self):
        self.searxng_url = "http://localhost:8888"
        self.use_searxng = True
    
    async def _search_with_searxng(self, query: str):
        # Query SearXNG JSON API
        params = {
            'q': query,
            'format': 'json',
            'categories': 'general'
        }
        response = await client.get(f"{self.searxng_url}/search", params=params)
        # Process and synthesize results
```

**Benefits**:
- Privacy-focused (no tracking)
- Self-hosted control
- Multiple search engine aggregation
- No API rate limits
- Docker containerized

### **Future MCP Possibilities**

The architecture supports easy integration of new MCP servers:

#### **1. MCP-Database** (Planned)
- **Purpose**: Query local/remote databases
- **Use Cases**: Customer data, inventory, analytics
- **Implementation**: Add `DatabaseAgent` class
- **MCP Server**: PostgreSQL/MySQL/MongoDB connector

#### **2. MCP-Memory** (Planned)
- **Purpose**: Long-term conversation memory
- **Use Cases**: User preferences, context retention
- **Implementation**: Vector database (ChromaDB, Pinecone)
- **Benefits**: Personalized responses, context awareness

#### **3. MCP-Code-Execution** (Planned)
- **Purpose**: Execute Python/JavaScript code safely
- **Use Cases**: Data analysis, calculations, visualizations
- **Implementation**: Sandboxed execution environment
- **MCP Server**: Jupyter kernel or isolated container

#### **4. MCP-File-System** (Planned)
- **Purpose**: Read/write files on server
- **Use Cases**: Document management, file operations
- **Implementation**: `FileSystemAgent` with permissions
- **Security**: Sandboxed directory access

#### **5. MCP-API-Gateway** (Planned)
- **Purpose**: Connect to external APIs (weather, stocks, etc.)
- **Use Cases**: Real-time data, third-party integrations
- **Implementation**: Generic API calling agent
- **Examples**: OpenWeatherMap, Alpha Vantage, etc.

#### **6. MCP-Vision** (Planned)
- **Purpose**: Advanced image understanding beyond documents
- **Use Cases**: Object detection, image captioning, scene understanding
- **Models**: CLIP, LLaVA, or other vision-language models
- **Implementation**: Extend current Docling agent

### **Adding New MCP Agents**

**Step-by-step process**:

1. **Create Agent Class** in `backend/main.py`:
```python
class NewAgent:
    def __init__(self):
        self.mcp_server_url = "http://localhost:PORT"
    
    async def process(self, user_input: str) -> str:
        # Agent logic here
        pass
```

2. **Initialize Agent**:
```python
new_agent = NewAgent()
```

3. **Update Router**:
```python
def route_message(self, message, has_file):
    # Add routing logic for new agent
    if "new_agent_keyword" in message:
        return {"agent": "new_agent", "action": "process"}
```

4. **Add to Chat Endpoint**:
```python
elif routing_decision["agent"] == "new_agent":
    response = await new_agent.process(request.message)
```

5. **Update Stats Endpoint**:
```python
"agents_available": ["router", "docling", "web_search", "new_agent"]
```

---

## 📄 Document Processing Deep Dive

### **Granite-Docling Model**

**What is Granite-Docling?**
- Vision-language model fine-tuned for document understanding
- 258M parameters (lightweight, fast)
- Trained on synthetic document datasets:
  - SynthCodeNet (code documents)
  - SynthFormulaNet (mathematical formulas)
  - SynthChartNet (charts and graphs)
  - DoclingMatix (general documents)

**Why Granite-Docling?**
- ✅ Specialized for documents (better than general OCR)
- ✅ Outputs structured DocTags (not just plain text)
- ✅ Understands layout (tables, headers, lists)
- ✅ Small enough to run on Raspberry Pi
- ✅ Fast inference (~10-70 seconds per document)

**DocTags Advantages**:
- Preserves document structure
- Enables accurate table extraction
- Semantic understanding (not just text)
- Machine-readable format
- Easy to parse and transform

### **Processing Pipeline**

```
┌──────────────┐
│ User uploads │
│  image/PDF   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Convert to   │
│  base64      │
└──────┬───────┘
       │
       ↓
┌──────────────────┐
│ Send to Granite- │
│ Docling (Ollama) │
│ Prompt: ""       │  ← Empty or minimal prompt
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Receives DocTags │
│ XML markup       │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Parse with       │
│ docling-core     │
│ or regex         │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Extract:         │
│ • Titles         │
│ • Headers        │
│ • Tables         │
│ • Text           │
│ • Lists          │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Format as        │
│ Markdown         │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Optional: AI     │
│ Summarization    │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Return to user   │
└──────────────────┘
```

---

## 🚀 Running the System

### **Master Control Script**

The system uses `start_multiagent.sh` for complete lifecycle management:

```bash
./start_multiagent.sh [command]
```

**Available Commands**:

#### **1. Start All Services**
```bash
./start_multiagent.sh start
```
**What it does**:
- Checks if ports 9050 (backend) and 9051 (frontend) are free
- Activates Python virtual environment
- Starts FastAPI backend on port 9050
- Starts Python HTTP server for frontend on port 9051
- Runs both in background
- Waits for services to be ready
- Displays access URLs

**Output**:
```
🚀 Multi-Agent System Startup Script
====================================
🔧 Starting Backend Service...
✅ Port 9050 is free
📡 Starting FastAPI backend on port 9050...
✅ Backend started (PID: 12345)
💻 Starting Frontend Service...
✅ Port 9051 is free
🌐 Starting frontend on port 9051...
✅ Frontend started (PID: 12346)
🎉 Multi-Agent System Started Successfully!
📍 Backend API: http://localhost:9050
📍 Frontend:    http://localhost:9051
💡 Access from other devices: http://your-raspberry-pi-ip:9051
```

#### **2. Stop All Services**
```bash
./start_multiagent.sh stop
```
**What it does**:
- Finds processes on ports 9050 and 9051
- Gracefully terminates backend
- Gracefully terminates frontend
- Cleans up background processes

#### **3. Restart All Services**
```bash
./start_multiagent.sh restart
```
**What it does**:
- Stops all services
- Waits for cleanup
- Starts all services fresh
- Useful after code changes

#### **4. Check Status**
```bash
./start_multiagent.sh status
```
**What it does**:
- Checks if backend is running (port 9050)
- Checks if frontend is running (port 9051)
- Shows process IDs
- Tests backend health endpoint
- Displays system stats

**Output**:
```
📊 Multi-Agent System Status
============================
Backend (Port 9050):  ✅ Running (PID: 12345)
Frontend (Port 9051): ✅ Running (PID: 12346)

Backend Health:
{
  "status": "healthy",
  "service": "multi-agent-system",
  "timestamp": "2025-10-21T23:00:00"
}

System Stats:
{
  "agents_available": ["router", "docling", "web_search"],
  "models": {
    "router": "qwen3:0.6b",
    "docling": "gabegoodhart/granite-docling:258M"
  }
}
```

### **Individual Service Scripts**

#### **Backend Only**
```bash
./start_backend.sh
```
Activates venv and starts FastAPI on port 9050.

#### **Frontend Only**
```bash
./start_frontend.sh
```
Starts Python HTTP server on port 9051.

### **Manual Startup (Development)**

For debugging or development:

```bash
# Activate virtual environment
source agent_env/bin/activate

# Start backend (foreground)
python backend/main.py

# In another terminal, start frontend
python3 -m http.server 9051 --directory frontend
```

---

## 📊 API Endpoints

### **Backend API (Port 9050)**

#### **POST /upload**
Upload a file for processing.

**Request**:
```json
{
  "file": "multipart/form-data"
}
```

**Response**:
```json
{
  "file_id": "uuid-string",
  "filename": "document.jpg",
  "message": "File uploaded successfully"
}
```

#### **POST /chat**
Send a message to the AI system.

**Request**:
```json
{
  "message": "What's in this document?",
  "session_id": "uuid-string",
  "file_id": "uuid-string"  // Optional
}
```

**Response**:
```json
{
  "response": "AI response text...",
  "session_id": "uuid-string",
  "agent_used": "docling",
  "timestamp": "2025-10-21T23:00:00"
}
```

#### **GET /health**
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "multi-agent-system",
  "timestamp": "2025-10-21T23:00:00"
}
```

#### **GET /stats**
System statistics and available agents.

**Response**:
```json
{
  "agents_available": ["router", "docling", "web_search"],
  "models": {
    "router": "qwen3:0.6b",
    "docling": "gabegoodhart/granite-docling:258M",
    "web_search": "Brave Search API + SearXNG"
  }
}
```

#### **GET /debug/last-doctags**
View last DocTags output (debugging).

**Response**:
```json
{
  "last_doctags": "<doctag>...</doctag>",
  "timestamp": "2025-10-21T23:00:00"
}
```

---

## 📱 Mobile Features

### **Responsive Design**
- **Breakpoints**: 768px (mobile), 1024px (tablet)
- **Hamburger Menu**: ☰ button for sidebar access
- **Touch Optimized**: Larger buttons (48px min)
- **iOS Safe**: No zoom on input (16px font)
- **Smooth Scrolling**: Hardware-accelerated

### **Mobile-Specific CSS**
```css
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -100%;
    transition: left 0.3s ease;
  }
  
  .sidebar.mobile-open {
    left: 0;
  }
  
  .message-input {
    font-size: 16px; /* Prevents iOS zoom */
  }
}
```

---

## 🔒 Security

- **API Keys**: Stored in `.env` file (not in code)
- **CORS**: Configured for local network access
- **File Upload**: UUIDs prevent path traversal
- **Temp Files**: Stored in `/tmp` with unique names
- **No External Exposure**: Services run on local network only

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| **Backend Startup** | ~3 seconds |
| **Frontend Load** | < 1 second |
| **Document Processing** | 10-70 seconds (depends on complexity) |
| **Web Search** | 2-5 seconds |
| **General Chat** | 1-3 seconds |
| **Memory Usage (Backend)** | ~200 MB |
| **Memory Usage (Ollama)** | ~1.5 GB (with models loaded) |

---

## 🎯 Future Enhancements

### **Planned Features**
- [ ] Multi-language support (i18n)
- [ ] User authentication system
- [ ] Conversation export (PDF, Markdown)
- [ ] Voice input support
- [ ] Dark/light theme toggle
- [ ] More MCP integrations (database, calendar, etc.)
- [ ] Model selection in UI
- [ ] Real-time streaming responses
- [ ] Document comparison tool
- [ ] Batch document processing

### **Under Consideration**
- [ ] Docker containerization (full stack)
- [ ] Cloud deployment option
- [ ] API rate limiting
- [ ] Analytics dashboard
- [ ] Plugin system for custom agents

---

## 📝 Development

### **Project Structure**
```
multiagent/
├── backend/
│   └── main.py                  # FastAPI app, all agents
├── frontend/
│   └── index.html               # Web interface
├── agent_env/                   # Python virtual environment
├── .env                         # Environment variables
├── start_multiagent.sh          # Master control script
├── start_backend.sh             # Backend startup
├── start_frontend.sh            # Frontend startup
└── README_BACKUP.md             # Documentation
```

### **Adding New Features**
1. Update `backend/main.py` for backend changes
2. Update `frontend/index.html` for UI changes
3. Test locally
4. Restart services: `./start_multiagent.sh restart`
5. Verify functionality

---

## 🤝 Contributing

This is a personal project, but open to improvements:
- Document any issues or bugs
- Suggest new agents or features
- Optimize performance
- Improve mobile experience
- Add new MCP integrations

---

## 📄 License

Private project - All rights reserved.

---

## 📞 Support

For questions or issues:
- Check documentation files in this directory
- Review backend logs: `/tmp/backend.log`
- Test health endpoint: `curl http://localhost:9050/health`
- Verify Ollama: `curl http://localhost:11434/api/tags`

---

**Project Status**: ✅ Production Ready  
**Last Updated**: October 21, 2025  
**Version**: 1.0
