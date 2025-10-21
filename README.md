# 📚 Asclepius Multi-Agent System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

**Created by:** [CiscoPonce](https://github.com/CiscoPonce)

> An intelligent multi-agent AI system with specialized agents for document processing, web search, and conversational AI.

---

## 📋 Overview

Asclepius is a multi-agent AI system that orchestrates specialized agents to handle different tasks intelligently. Named after the Greek god of medicine and healing, this system provides accurate, structured responses through intelligent agent routing.

### ✨ Key Features

- 🤖 **Intelligent Agent Routing** - Automatically directs queries to the right specialized agent
- 📄 **Document Processing** - OCR with Granite-Docling for table extraction and content analysis
- 🔍 **Web Search** - Privacy-focused SearXNG integration with Brave Search API fallback
- 💬 **Conversational AI** - Natural language understanding with qwen3:0.6b
- 📱 **Mobile-Optimized** - Responsive design for seamless mobile experience
- 🔌 **MCP Integration** - Extensible via Model Context Protocol

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Frontend (9051)   │  HTML/CSS/JavaScript
└──────────┬──────────┘
           │ HTTP/REST
           ↓
┌─────────────────────┐
│   Backend (9050)    │  FastAPI + Uvicorn
│   Agent Router      │  qwen3:0.6b
└──────────┬──────────┘
           │
    ┌──────┴──────┬─────────┐
    ↓             ↓         ↓
┌────────┐  ┌──────────┐  ┌────────┐
│Docling │  │Web Search│  │General │
│ Agent  │  │  Agent   │  │ Chat   │
└───┬────┘  └────┬─────┘  └────────┘
    │            │
    ↓            ↓
┌────────┐  ┌─────────┐
│Granite │  │SearXNG +│
│Docling │  │ Brave   │
└────────┘  └─────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **OS**: Linux (Raspberry Pi OS, Ubuntu, Debian)
- **Python**: 3.11+
- **Docker**: For Ollama and SearXNG
- **RAM**: 2GB minimum (4GB+ recommended)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/CiscoPonce/Asclepius_Multiagent.git
cd Asclepius_Multiagent
```

2. **Set up Python environment**:
```bash
python3 -m venv agent_env
source agent_env/bin/activate
pip install fastapi uvicorn httpx python-dotenv docling-core pillow pyyaml
```

3. **Install Ollama and models**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull qwen3:0.6b
ollama pull gabegoodhart/granite-docling:258M
```

4. **Set up SearXNG (optional)**:
```bash
# SearXNG provides privacy-focused web search
docker run -d \
  -p 8888:8080 \
  -e SEARXNG_BASE_URL=http://localhost:8888/ \
  searxng/searxng:latest
```

5. **Configure environment**:
```bash
# Copy and edit .env file
cp .env .env.local
# Add your Brave Search API key (optional)
echo "BRAVE_API_KEY=your_key_here" >> .env.local
```

6. **Start the system**:
```bash
chmod +x start_multiagent.sh
./start_multiagent.sh start
```

7. **Access the interface**:
- Frontend: http://localhost:9051
- Backend API: http://localhost:9050

---

## 🎯 Usage

### Master Control Script

```bash
# Start all services
./start_multiagent.sh start

# Stop all services
./start_multiagent.sh stop

# Restart services
./start_multiagent.sh restart

# Check status
./start_multiagent.sh status
```

### Document Processing

1. Upload an image or PDF document
2. Ask questions about the content
3. Get structured extraction with tables and text

**Example**:
- Upload invoice image
- Ask "What items are in this invoice?"
- Receive formatted table with extracted data

### Web Search

Ask questions requiring real-time information:
- "What's the current weather in Tokyo?"
- "Latest news about AI developments"
- "Stock price of Tesla"

### General Chat

Conversational queries are handled by the router agent:
- "Explain quantum computing"
- "Help me understand Docker"
- "What can you do?"

---

## 🤖 Agents

### 1. Agent Router
**Model**: qwen3:0.6b  
**Purpose**: Intelligent request routing and orchestration

Routes requests based on:
- File uploads → Docling Agent
- Search keywords → Web Search Agent
- Document keywords → Docling Agent  
- General queries → General Chat

### 2. Docling Agent
**Model**: granite-docling:258M  
**Purpose**: Document OCR and structured extraction

Features:
- DocTags parsing for structured content
- Table extraction and formatting
- Multi-format support (images, PDFs)
- Intelligent summarization

### 3. Web Search Agent
**Primary**: SearXNG (self-hosted)  
**Fallback**: Brave Search API  
**Purpose**: Real-time information retrieval

Features:
- Privacy-focused search
- AI-powered result synthesis
- Automatic fallback handling
- Source attribution

---

## 📡 API Endpoints

### POST `/upload`
Upload a document for processing.

### POST `/chat`
Send a message to the AI system.
```json
{
  "message": "What's in this document?",
  "session_id": "uuid",
  "file_id": "uuid"
}
```

### GET `/health`
Health check endpoint.

### GET `/stats`
System statistics and available agents.

---

## 🔌 MCP Integration

Asclepius supports the **Model Context Protocol (MCP)** for extensibility.

### Current Implementation
- **MCP-SearXNG**: Privacy-focused web search

### Future Possibilities
- **MCP-Database**: Query databases
- **MCP-Memory**: Long-term conversation memory
- **MCP-Code-Execution**: Safe code execution
- **MCP-File-System**: File operations
- **MCP-API-Gateway**: External API integrations

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for details on adding new MCP agents.

---

## 📱 Mobile Support

Fully responsive design with:
- Hamburger menu for sidebar access
- Touch-optimized controls
- iOS-safe inputs (no zoom)
- Smooth scrolling animations

Access from your phone on the same network!

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **AI Models** | qwen3:0.6b, granite-docling:258M |
| **Document Parsing** | docling-core, Pillow |
| **Web Search** | SearXNG, Brave Search API |
| **Inference** | Ollama (Docker) |

---

## 📊 Performance

### Tested on Raspberry Pi 5 (16GB RAM)

Real-world performance metrics running on Raspberry Pi 5:

| Metric | Value | Notes |
|--------|-------|-------|
| **Backend Startup** | ~3 seconds | FastAPI initialization |
| **Document Processing** | 10-70 seconds | Depends on complexity and image size |
| **Web Search** | 2-5 seconds | SearXNG + AI synthesis |
| **General Chat** | 1-3 seconds | qwen3:0.6b response generation |
| **Memory Usage (Backend)** | ~200 MB | Python + FastAPI |
| **Memory Usage (Ollama)** | ~2.5 GB | With models loaded and inference |
| **Total System Used** | ~2.5 GB | All services running |
| **Total System Available** | 16 GB | Plenty of headroom |

### Hardware Specifications
- **Device**: Raspberry Pi 5 Model B Rev 1.1
- **RAM**: 16GB LPDDR4X
- **CPU**: Quad-core Cortex-A76 @ 2.4GHz (ARM v8.2)
- **Storage**: MicroSD / NVMe SSD support
- **OS**: Raspberry Pi OS (64-bit)

### Model Specifications
| Model | Size on Disk | Parameters | Quantization | Purpose |
|-------|--------------|------------|--------------|---------|
| **qwen3:0.6b** | ~522 MB | 751.63M | Q4_K_M | Router & chat |
| **granite-docling:258M** | ~522 MB | 164.01M | F16 | Document OCR |

> 💡 **Note**: The Raspberry Pi 5 with 16GB RAM provides excellent performance for this multi-agent system. Document processing time varies based on image resolution and content complexity. The system can handle multiple concurrent requests thanks to the generous RAM allocation.

---

## 🔒 Security

- API keys stored in `.env` (not tracked)
- CORS configured for local network
- UUID-based file uploads
- No external data exposure

---

## 📚 Documentation

- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Comprehensive project documentation
- [CLEAN_BACKUP_SUMMARY.md](CLEAN_BACKUP_SUMMARY.md) - System overview
- [BACKUP_INVENTORY.md](BACKUP_INVENTORY.md) - File inventory

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**CiscoPonce**
- GitHub: [@CiscoPonce](https://github.com/CiscoPonce)

---

## 🙏 Acknowledgments

This project is built on the shoulders of giants. Special thanks to:

### AI Models (via Ollama)
- **[Qwen Team](https://huggingface.co/Qwen)** - For the incredible [qwen3:0.6b model](https://ollama.com/library/qwen3:0.6b) with 752M parameters, excellent reasoning capabilities, and multilingual support (100+ languages)
- **[IBM Research / Docling Project](https://huggingface.co/ibm-granite/granite-docling-258M)** - For the [Granite-Docling 258M model](https://ollama.com/gabegoodhart/granite-docling) with enhanced document understanding, DocTags generation, and equation recognition
- **[Gabe Goodhart](https://ollama.com/gabegoodhart)** - For packaging and sharing the Granite-Docling model on Ollama

### Infrastructure & Frameworks
- **[Ollama](https://ollama.com/)** - For making local LLM inference accessible and easy to deploy
- **[SearXNG](https://github.com/searxng/searxng)** - For the privacy-respecting metasearch engine
- **[FastAPI](https://fastapi.tiangolo.com/)** - For the modern, high-performance web framework
- **[Docling Core](https://github.com/DS4SD/docling-core)** - For DocTags parsing and document structure understanding

### Model Details
- **qwen3:0.6b**: 752M parameters, Q4_K_M quantization, 523MB - [Ollama](https://ollama.com/library/qwen3:0.6b) | [Hugging Face](https://huggingface.co/Qwen)
- **granite-docling:258M**: 164M parameters, F16 quantization, 522MB - [Ollama](https://ollama.com/gabegoodhart/granite-docling) | [Hugging Face](https://huggingface.co/ibm-granite/granite-docling-258M)

All models are accessed via [Ollama](https://ollama.com/), which provides a unified API for local LLM inference.

---

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] User authentication
- [ ] Voice input
- [ ] Real-time streaming responses
- [ ] Batch document processing
- [ ] More MCP integrations

---

**⭐ If you find this project useful, please give it a star!**

