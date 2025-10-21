#!/usr/bin/env python3
"""
Asclepius Multi-Agent System - Main Backend
FastAPI application with intelligent agent routing

Created by: CiscoPonce
GitHub: https://github.com/CiscoPonce/Asclepius_Multiagent
License: MIT

Features:
- Agent Router: Intelligent request routing (qwen3:0.6b)
- Docling Agent: Document processing with Granite-Docling (258M)
- Web Search Agent: SearXNG + Brave Search API integration
- DocTags parsing for structured document extraction
"""

import os
import uuid
import json
import base64
import asyncio
import tempfile
import aiofiles
import httpx
import time
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import docling-core for proper DocTags parsing
try:
    from docling_core.types.doc.document import DocTagsDocument, DoclingDocument
    from PIL import Image
    DOCLING_AVAILABLE = True
    print("✅ Docling-core imported successfully")
except ImportError as e:
    DOCLING_AVAILABLE = False
    print(f"⚠️ Docling-core not available: {e}")
    print("📝 Will use fallback document processing")

# Create FastAPI app
app = FastAPI(title="Multi-Agent System - Router")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
ROUTER_MODEL = "qwen3:0.6b"  # Agent Router Model
DOCLING_MODEL = "gabegoodhart/granite-docling:258M"  # Document Processing Model

# File storage setup
UPLOAD_DIR = Path(tempfile.gettempdir()) / "multiagent_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
print(f"File upload directory: {UPLOAD_DIR}")

# In-memory storage
uploaded_files = {}
chat_history = []
agent_conversations = {}

# HTTP client for Ollama
ollama_client = httpx.AsyncClient(timeout=120.0)

# Data models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    file_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    processing_time: float
    session_id: str

class AgentRouter:
    """Main agent router that handles conversation and routes to specialized agents"""
    
    def __init__(self):
        self.model = ROUTER_MODEL
        self.conversation_memory = {}
    
    async def route_message(self, message: str, session_id: str, has_file: bool = False) -> Dict[str, Any]:
        """Route message to appropriate agent based on content and context"""
        
        message_lower = message.lower()
        
        # Document processing keywords (expanded list)
        docling_keywords = [
            'document', 'pdf', 'image', 'parse', 'extract', 'analyze', 'process',
            'ocr', 'text', 'table', 'chart', 'graph', 'scan', 'read', 'understand',
            'content', 'data', 'information', 'structure', 'layout', 'form',
            'invoice', 'receipt', 'contract', 'report', 'paper', 'file',
            'what does this say', 'what is in this', 'explain this document',
            'summarize', 'key points', 'main ideas'
        ]
        
        # Web search keywords
        web_search_keywords = [
            'search', 'find', 'look up', 'google', 'web search', 'internet search',
            'current', 'latest', 'recent', 'news', 'today', 'now', '2024', '2025',
            'what is', 'who is', 'where is', 'when is', 'how to', 'why is',
            'weather', 'stock', 'price', 'news about', 'information about',
            'tell me about', 'find information', 'look for', 'search for'
        ]
        
        # Check if this is a document processing request
        if has_file:
            return {
                "agent": "docling",
                "action": "process_document",
                "reason": "File uploaded - routing to document processor"
            }
        
        # Check for web search keywords
        elif any(keyword in message_lower for keyword in web_search_keywords):
            return {
                "agent": "web_search",
                "action": "search_web",
                "reason": f"Web search keywords detected: {[kw for kw in web_search_keywords if kw in message_lower]}"
            }
        
        # Check for document processing keywords
        elif any(keyword in message_lower for keyword in docling_keywords):
            return {
                "agent": "docling",
                "action": "process_document",
                "reason": f"Document processing keywords detected: {[kw for kw in docling_keywords if kw in message_lower]}"
            }
        
        # Check if this is asking about agent capabilities
        elif any(keyword in message_lower for keyword in ['what can you do', 'capabilities', 'agents', 'tools', 'help']):
            return {
                "agent": "router",
                "action": "explain_capabilities",
                "reason": "User asking about system capabilities"
            }
        
        # Check if this is a general chat request
        elif any(keyword in message_lower for keyword in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return {
                "agent": "router",
                "action": "general_chat",
                "reason": "Greeting detected - general conversation"
            }
        
        # Default to router for general queries
        else:
            return {
                "agent": "router",
                "action": "general_chat",
                "reason": "Default routing - general query"
            }
    
    async def general_chat(self, message: str, session_id: str) -> str:
        """Handle general conversation using Qwen3"""
        
        # Get conversation history
        conversation_history = agent_conversations.get(session_id, [])
        
        # Build context
        context = "You are a helpful AI assistant. You can help with general questions, chat, and can also process documents when uploaded.\n\n"
        
        if conversation_history:
            context += "Previous conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                context += f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}\n\n"
        
        context += f"Current message: {message}"
        
        # Call Ollama
        payload = {
            "model": self.model,
            "prompt": context,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = await ollama_client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            assistant_response = result.get('response', 'Sorry, I could not process your request.')
            
            # Store in conversation history
            if session_id not in agent_conversations:
                agent_conversations[session_id] = []
            
            agent_conversations[session_id].append({
                "user": message,
                "assistant": assistant_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 conversations
            if len(agent_conversations[session_id]) > 10:
                agent_conversations[session_id] = agent_conversations[session_id][-10:]
            
            return assistant_response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def explain_capabilities(self, message: str, session_id: str) -> str:
        """Handle requests about system capabilities"""
        
        capabilities_response = """🤖 **Multi-Agent System Capabilities**

I'm a Router Agent coordinating a multi-agent system with the following capabilities:

**🧠 Router Agent (Qwen3:0.6b)** - That's me!
• General conversation and chat
• Request routing and coordination
• Context-aware responses
• Session management

**📄 Docling Agent (Granite-Docling:258M)**
• Document parsing and analysis
• Text extraction from images, PDFs, DOCX
• Table and structure detection
• Chart and graph interpretation
• RAG-ready content preparation

**🌐 Web Search Agent (Brave Search API)**
• Real-time web search
• Current information and news
• Research and fact-checking
• Latest updates on any topic

**🔄 How to Use:**
• **General Chat**: Just talk to me like this!
• **Document Processing**: Upload a file and ask me to "analyze this document" or "extract text"
• **Web Search**: Ask me to "search for", "find information about", or "what is" something
• **Smart Routing**: I automatically route your requests to the right agent

**📎 Supported File Types:**
• Images (JPG, PNG)
• PDFs
• DOCX documents

**🔍 Example Search Queries:**
• "Search for latest news about AI"
• "What is the current weather in London?"
• "Find information about Python programming"
• "Tell me about recent developments in quantum computing"

Try uploading a document, asking me to search the web, or just chat! 🚀"""
        
        # Store in conversation history
        if session_id not in agent_conversations:
            agent_conversations[session_id] = []
        
        agent_conversations[session_id].append({
            "user": message,
            "assistant": capabilities_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return capabilities_response

class DoclingAgent:
    """Specialized agent for document processing using Granite-Docling"""
    
    def __init__(self):
        self.model = DOCLING_MODEL
    
    async def process_document(self, file_path: str, user_message: str) -> str:
        """Process document using Granite-Docling model with proper DocTags parsing"""
        
        try:
            print(f"🔍 Processing document: {file_path}")
            
            # Load and encode image
            with open(file_path, "rb") as f:
                image_data = f.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            print(f"📊 Image size: {len(image_data)} bytes, Base64 length: {len(image_b64)}")
            
            # Use Granite-Docling with simple direct prompt
            print("🔄 Using Granite-Docling for document extraction...")
            return await self._fallback_document_processing(file_path, user_message, image_b64)
                
        except Exception as e:
            print(f"❌ Document processing error: {str(e)}")
            return f"❌ Error processing document: {str(e)}"
    
    def _extract_content_from_docling_document(self, doc: 'DoclingDocument') -> Optional[str]:
        """Extract content from a parsed DoclingDocument"""
        try:
            content_parts = []
            
            # Extract text content from the document
            if hasattr(doc, 'text') and doc.text:
                content_parts.append(doc.text)
            
            # Extract structured elements if available
            if hasattr(doc, 'elements'):
                for element in doc.elements:
                    if hasattr(element, 'text') and element.text:
                        content_parts.append(element.text)
            
            # Join all content parts
            full_content = '\n\n'.join(content_parts)
            
            if full_content and len(full_content.strip()) > 50:
                return full_content.strip()
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting content from DoclingDocument: {str(e)}")
            return None
    
    def _extract_content_from_raw_doctags(self, doctags_output: str) -> Optional[str]:
        """Extract content from raw DocTags markup"""
        try:
            content_parts = []
            
            # Extract headings
            headings = re.findall(r'<heading[^>]*>(.*?)</heading>', doctags_output, re.DOTALL)
            for heading in headings:
                if heading.strip():
                    content_parts.append(f"# {heading.strip()}")
            
            # Extract paragraphs
            paragraphs = re.findall(r'<paragraph>(.*?)</paragraph>', doctags_output, re.DOTALL)
            for para in paragraphs:
                if para.strip():
                    content_parts.append(para.strip())
            
            # Extract table content
            tables = re.findall(r'<table>(.*?)</table>', doctags_output, re.DOTALL)
            for table in tables:
                if table.strip():
                    # Extract table rows and cells
                    rows = re.findall(r'<row>(.*?)</row>', table, re.DOTALL)
                    table_content = []
                    for row in rows:
                        cells = re.findall(r'<cell>(.*?)</cell>', row, re.DOTALL)
                        if cells:
                            table_content.append(' | '.join(cell.strip() for cell in cells))
                    
                    if table_content:
                        content_parts.append('\n'.join(table_content))
            
            # Extract list items
            items = re.findall(r'<item>(.*?)</item>', doctags_output, re.DOTALL)
            if items:
                list_content = []
                for item in items:
                    if item.strip():
                        list_content.append(f"• {item.strip()}")
                if list_content:
                    content_parts.append('\n'.join(list_content))
            
            # Join all content
            full_content = '\n\n'.join(content_parts)
            
            if full_content and len(full_content.strip()) > 50:
                return full_content.strip()
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting content from raw DocTags: {str(e)}")
            return None
    
    def _format_document_response(self, content: str, user_message: str, method: str) -> str:
        """Format the document response with proper structure"""
        
        # Clean up the content
        clean_content = content.strip()
        
        # Remove common technical headers
        technical_headers = [
            "Powered by TCPDF",
            "www.tcpdf.org",
            "TCPDF",
            "Generated by",
            "Document created"
        ]
        
        for header in technical_headers:
            clean_content = clean_content.replace(header, "").strip()
        
        # Improve text formatting
        clean_content = re.sub(r'\s+', ' ', clean_content)
        clean_content = clean_content.replace('. ', '.\n')
        clean_content = clean_content.replace('! ', '!\n')
        clean_content = clean_content.replace('? ', '?\n')
        clean_content = re.sub(r'\n+', '\n\n', clean_content)
        clean_content = clean_content.strip()
        
        # Format the response
        formatted_response = f"📄 **Document Analysis Complete ({method})**\n\n"
        
        # Check if user wants analysis or summary
        analysis_keywords = ['analyze', 'summarize', 'summary', 'overview', 'what is in this', 'explain this document']
        wants_analysis = any(keyword in user_message.lower() for keyword in analysis_keywords)
        
        if wants_analysis:
            # Provide a summary using the router model
            formatted_response += f"**📋 Document Summary:**\n\n"
            
            # Create a summary using the router model
            summary_prompt = f"""Please provide a comprehensive summary of this document content in 3-4 sentences. Focus on the main points, key information, and important details:

{clean_content[:1500]}

Provide a clear, informative summary that captures the essence of this document."""
            
            try:
                summary_payload = {
                    "model": ROUTER_MODEL,
                    "prompt": summary_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                }
                
                # Note: We need to make this async call from within an async context
                # For now, we'll show the content and suggest asking for a summary
                formatted_response += f"**📝 Extracted Content (first 2000 characters):**\n\n"
                if len(clean_content) > 2000:
                    formatted_response += f"{clean_content[:2000]}\n\n"
                    formatted_response += f"*... and {len(clean_content) - 2000} more characters*\n\n"
                    formatted_response += f"**💡 Tip:** Ask me to 'summarize this document' to get a complete overview of all content.\n\n"
                else:
                    formatted_response += f"{clean_content}\n\n"
                
            except Exception as e:
                print(f"❌ Summary generation failed: {str(e)}")
                formatted_response += f"{clean_content[:1000]}...\n\n"
        else:
            # Show the extracted content
            if len(clean_content) > 3000:
                formatted_response += f"**📝 Extracted Content (showing first 3000 characters):**\n\n"
                formatted_response += f"{clean_content[:3000]}\n\n"
                formatted_response += f"*... and {len(clean_content) - 3000} more characters*\n\n"
                formatted_response += f"**💡 Tip:** Ask me to 'analyze this document' to get a summary of all content.\n\n"
            else:
                formatted_response += f"**📝 Extracted Content:**\n\n"
                formatted_response += f"{clean_content}\n\n"
        
        # Add document statistics
        word_count = len(clean_content.split())
        formatted_response += f"**📊 Document Statistics:**\n"
        formatted_response += f"• Characters: {len(clean_content)}\n"
        formatted_response += f"• Words: {word_count}\n"
        formatted_response += f"• Processing Method: {method}\n"
        
        return formatted_response
    
    def _remove_duplicates(self, text: str) -> str:
        """Remove duplicate consecutive blocks of text"""
        lines = text.split('\n')
        seen = set()
        result = []
        
        for line in lines:
            line_clean = line.strip()
            if line_clean and line_clean not in seen:
                seen.add(line_clean)
                result.append(line)
        
        return '\n'.join(result)
    
    def _parse_doctags_to_text(self, doctags_text: str) -> str:
        """Parse DocTags XML to formatted text with proper table structure"""
        try:
            result = []
            found_content = False
            
            # Extract title
            titles = re.findall(r'<title>(.*?)</title>', doctags_text, re.DOTALL)
            for title in titles:
                result.append(f"# {title.strip()}\n")
                found_content = True
            
            # Extract section headers
            for level in range(1, 6):
                headers = re.findall(rf'<section_header_level_{level}>(.*?)</section_header_level_{level}>', doctags_text, re.DOTALL)
                for header in headers:
                    result.append(f"{'#' * (level + 1)} {header.strip()}\n")
                    found_content = True
            
            # Extract and format tables
            # According to DocTags spec: <table> or <otsl> with <fcel>, <lcel>, <nl>
            # Also handle <ched> for column headers
            tables = re.findall(r'<(?:table|otsl)>(.*?)</(?:table|otsl)>', doctags_text, re.DOTALL)
            for table in tables:
                table_rows = []
                
                # First, check for column headers with <ched>
                headers = re.findall(r'<ched>(.*?)(?=<ched>|<nl>|$)', table, re.DOTALL)
                if headers:
                    # Clean and add headers as first row
                    clean_headers = [h.strip() for h in headers if h.strip() and '<' not in h]
                    if clean_headers:
                        table_rows.append(clean_headers)
                
                # Split by <nl> (new line in table)
                rows = table.split('<nl>')
                for row in rows:
                    if '<ched>' in row:
                        continue  # Skip header row, already processed
                    
                    cells = []
                    # Extract all cells (fcel, lcel, or any cell tags)
                    all_cells = re.findall(r'<(?:fcel|lcel|cell)>(.*?)(?=<(?:fcel|lcel|cell|nl)|$)', row, re.DOTALL)
                    
                    cells.extend([c.strip() for c in all_cells if c.strip() and '<' not in c])
                    
                    if cells:
                        table_rows.append(cells)
                
                # Format as markdown table
                if table_rows:
                    result.append("\n**Table:**\n")
                    # First row as header
                    if len(table_rows) > 0:
                        result.append("| " + " | ".join(table_rows[0]) + " |")
                        result.append("|" + "|".join(["---"] * len(table_rows[0])) + "|")
                        # Data rows
                        for row in table_rows[1:]:
                            # Pad row if needed
                            while len(row) < len(table_rows[0]):
                                row.append("")
                            result.append("| " + " | ".join(row) + " |")
                    result.append("\n")
                    found_content = True
            
            # Extract regular text
            texts = re.findall(r'<text>(.*?)</text>', doctags_text, re.DOTALL)
            for text in texts:
                result.append(f"{text.strip()}\n")
                found_content = True
            
            # Extract lists
            unordered_lists = re.findall(r'<unordered_list>(.*?)</unordered_list>', doctags_text, re.DOTALL)
            for ul in unordered_lists:
                items = re.findall(r'<list_item>(.*?)</list_item>', ul, re.DOTALL)
                for item in items:
                    result.append(f"• {item.strip()}")
                result.append("\n")
                found_content = True
            
            ordered_lists = re.findall(r'<ordered_list>(.*?)</ordered_list>', doctags_text, re.DOTALL)
            for ol in ordered_lists:
                items = re.findall(r'<list_item>(.*?)</list_item>', ol, re.DOTALL)
                for i, item in enumerate(items, 1):
                    result.append(f"{i}. {item.strip()}")
                result.append("\n")
                found_content = True
            
            # If no structured content was found, try to extract any text between tags
            if not found_content:
                print("⚠️ No structured DocTags found, extracting raw text between tags")
                # Remove all XML tags and return the text
                clean_text = re.sub(r'<[^>]+>', ' ', doctags_text)
                # Clean up whitespace
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text
            
            formatted = '\n'.join(result)
            return formatted if formatted else doctags_text
            
        except Exception as e:
            print(f"❌ Error parsing DocTags: {str(e)}")
            # Return original text if parsing fails
            return doctags_text
    
    async def _fallback_document_processing(self, file_path: str, user_message: str, image_b64: str) -> str:
        """Fallback document processing using traditional methods"""
        
        # Granite-Docling is trained to output DocTags format with minimal/no prompting
        # According to the DocTags spec, it should output XML-like markup automatically
        prompts = [
            "",  # No prompt - let the model use its default behavior
            
            "Extract",  # Minimal prompt
            
            "Document"  # Single word prompt
        ]
        
        best_result = ""
        best_length = 0
        
        for i, prompt in enumerate(prompts):
            print(f"🔄 Trying fallback prompt {i+1}/3")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.9
                }
            }
            
            try:
                response = await ollama_client.post(OLLAMA_API_URL, json=payload)
                response.raise_for_status()
                
                result = response.json()
                output = result.get('response', '').strip()
                
                print(f"📝 Fallback prompt {i+1} result length: {len(output)}")
                
                # Keep the result with the most content
                if len(output) > best_length:
                    best_result = output
                    best_length = len(output)
                    
            except Exception as e:
                print(f"❌ Fallback prompt {i+1} failed: {str(e)}")
                continue
        
        if best_result and len(best_result) > 50:
            # Save raw output for debugging
            self._last_raw_output = best_result
            
            # Check if result contains DocTags XML markup
            if '<' in best_result and '>' in best_result:
                print("🔍 DocTags detected in output, parsing structure...")
                print(f"📝 Raw DocTags output (first 500 chars): {best_result[:500]}")
                
                # Parse DocTags to extract structured content
                structured_content = self._parse_doctags_to_text(best_result)
                print(f"📊 Parsed content length: {len(structured_content)}")
                
                return self._format_document_response(structured_content, user_message, "DocTags Parsing (Granite-Docling)")
            else:
                # Post-process to remove duplicates
                cleaned_result = self._remove_duplicates(best_result)
                return self._format_document_response(cleaned_result, user_message, "Granite-Docling Processing")
        else:
            # Try router model fallback
            print("🔄 Trying router model fallback...")
            try:
                fallback_payload = {
                    "model": ROUTER_MODEL,
                    "prompt": f"""Look at this image and extract all readable text. This appears to be a document. Extract any text you can see, including headers, body text, tables, or any information.

User message: {user_message}

Please provide all the text content you can extract from this document.""",
                    "images": [image_b64],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                }
                
                fallback_response = await ollama_client.post(OLLAMA_API_URL, json=fallback_payload)
                fallback_response.raise_for_status()
                fallback_result = fallback_response.json()
                fallback_output = fallback_result.get('response', '').strip()
                
                print(f"📝 Router fallback result length: {len(fallback_output)}")
                
                if len(fallback_output) > 50:
                    return self._format_document_response(fallback_output, user_message, "Router Model Fallback")
                    
            except Exception as e:
                print(f"❌ Router fallback also failed: {str(e)}")
            
            return "❌ I could only extract technical headers from this document. The document might be:\n• An image without readable text\n• A corrupted file\n• A file format not supported by the model\n\nPlease try uploading a different document or check if the file contains readable text."

class WebSearchAgent:
    """Specialized agent for web search using SearXNG and Brave Search API fallback"""
    
    def __init__(self):
        self.searxng_url = "http://localhost:8888"
        self.fallback_api_key = os.getenv('BRAVE_API_KEY', '')
        self.fallback_api_url = "https://api.search.brave.com/res/v1/web/search"
        self.use_searxng = True
        
    async def search_web(self, query: str, user_message: str) -> str:
        """Search the web using SearXNG (primary) or Brave Search API (fallback)"""
        
        # Try SearXNG first
        if self.use_searxng:
            try:
                print(f"🔍 SearXNG search query: {query}")
                result = await self._search_with_searxng(query, user_message)
                if result:
                    return result
                else:
                    print("⚠️ SearXNG returned no results, falling back to Brave API...")
            except Exception as e:
                print(f"❌ SearXNG search failed: {str(e)}")
                print("🔄 Falling back to Brave API...")
        
        # Fallback to Brave API
        return await self._search_with_brave(query, user_message)
    
    async def _search_with_searxng(self, query: str, user_message: str) -> Optional[str]:
        """Search using SearXNG"""
        try:
            print(f"🔍 Querying SearXNG at {self.searxng_url}")
            
            # Prepare search parameters
            params = {
                'q': query,
                'format': 'json',
                'categories': 'general'
            }
            
            # Make the API request to SearXNG
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.searxng_url}/search", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'results' not in data or not data['results']:
                    print("⚠️ SearXNG returned no results")
                    return None
                
                results = data['results']
                print(f"✅ SearXNG returned {len(results)} results")
                
                # Prepare search data for AI analysis
                search_data = []
                for i, result in enumerate(results[:5], 1):  # Get top 5 results
                    search_data.append({
                        'title': result.get('title', 'No title'),
                        'url': result.get('url', ''),
                        'description': result.get('content', 'No description available')
                    })
                
                # AI synthesis of results
                formatted_response = await self._synthesize_results(search_data, query, user_message, "SearXNG")
                return formatted_response
                
        except Exception as e:
            print(f"❌ SearXNG error: {str(e)}")
            return None
    
    async def _search_with_brave(self, query: str, user_message: str) -> str:
        """Search using Brave Search API"""
        try:
            print(f"🔍 Brave API search query: {query}")
            
            if not self.fallback_api_key:
                return "❌ Web search is not configured. Please set BRAVE_API_KEY environment variable or ensure SearXNG is running."
            
            # Prepare search parameters
            params = {
                'q': query,
                'count': 5,
                'offset': 0,
                'mkt': 'en-US',
                'safesearch': 'moderate'
            }
            
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.fallback_api_key
            }
            
            # Make the API request
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.fallback_api_url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if 'web' not in data or 'results' not in data['web']:
                    return "❌ No search results found."
                
                results = data['web']['results']
                
                if not results:
                    return f"❌ No results found for '{query}'. Try rephrasing your search."
                
                print(f"✅ Brave API returned {len(results)} results")
                
                # Prepare search data for AI analysis
                search_data = []
                for i, result in enumerate(results[:5], 1):
                    search_data.append({
                        'title': result.get('title', 'No title'),
                        'url': result.get('url', ''),
                        'description': result.get('description', 'No description available')
                    })
                
                # AI synthesis of results
                return await self._synthesize_results(search_data, query, user_message, "Brave Search API")
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "❌ Invalid Brave Search API key. Please check your BRAVE_API_KEY."
            elif e.response.status_code == 429:
                return "❌ Rate limit exceeded. Please try again later."
            else:
                return f"❌ Search API error: {e.response.status_code}"
                
        except Exception as e:
            print(f"❌ Brave API error: {str(e)}")
            return f"❌ Error performing web search: {str(e)}"
    
    async def _synthesize_results(self, search_data: list, query: str, user_message: str, source: str) -> str:
        """Synthesize search results using AI"""
        
        # Use the router model to analyze and synthesize the search results
        analysis_prompt = f"""Based on the following web search results for "{query}", provide a comprehensive and helpful answer. Synthesize the information from multiple sources to give the user the best possible response.

Search Results:
"""
        
        for i, data in enumerate(search_data, 1):
            analysis_prompt += f"""
{i}. {data['title']}
   URL: {data['url']}
   Description: {data['description']}
"""
        
        analysis_prompt += f"""

Please provide:
1. A comprehensive answer to the user's question based on the search results
2. Key information and facts
3. Be informative and helpful
4. If it's about current data (like stock prices), mention that the information is from real-time sources
5. Keep the response concise but complete

User's original question: {user_message}"""
        
        try:
            # Get AI analysis of the search results
            analysis_payload = {
                "model": ROUTER_MODEL,
                "prompt": analysis_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            analysis_response = await ollama_client.post(OLLAMA_API_URL, json=analysis_payload)
            analysis_response.raise_for_status()
            analysis_result = analysis_response.json()
            ai_analysis = analysis_result.get('response', '').strip()
            
            # Format the response with AI analysis first, then sources
            formatted_response = f"🌐 **Web Search Results for: {query}**\n\n"
            formatted_response += f"**📋 Comprehensive Answer:**\n"
            formatted_response += f"{ai_analysis}\n\n"
            
            # Add sources section
            formatted_response += f"**📚 Sources:**\n"
            for i, data in enumerate(search_data[:3], 1):  # Show top 3 sources
                formatted_response += f"{i}. [{data['title']}]({data['url']})\n"
            
            formatted_response += f"\n*Search powered by {source} • Analysis by {ROUTER_MODEL}*"
            
            return formatted_response
            
        except Exception as e:
            print(f"❌ AI analysis failed: {str(e)}")
            # Fallback to original format if AI analysis fails
            formatted_response = f"🌐 **Web Search Results for: {query}**\n\n"
            
            for i, result in enumerate(search_data[:3], 1):
                formatted_response += f"**{i}. {result['title']}**\n"
                formatted_response += f"🔗 {result['url']}\n"
                formatted_response += f"{result['description']}\n\n"
            
            formatted_response += f"*Search powered by {source}*"
            return formatted_response

# Initialize agents
router_agent = AgentRouter()
docling_agent = DoclingAgent()
web_search_agent = WebSearchAgent()

@app.on_event("shutdown")
async def app_shutdown():
    await ollama_client.aclose()

@app.get("/")
async def root():
    return {"message": "Multi-Agent System Backend", "status": "running", "agents": ["router", "docling"]}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload"""
    try:
        file_id = str(uuid.uuid4())
        file_suffix = Path(file.filename).suffix if file.filename else ".tmp"
        
        # Handle different file types
        if file.content_type == "application/pdf":
            file_suffix = ".pdf"
        elif "openxmlformats-officedocument" in (file.content_type or ""):
            file_suffix = ".docx"
        elif file.content_type and file.content_type.startswith("image/"):
            file_suffix = ".jpg"
        
        temp_file_path = UPLOAD_DIR / f"{file_id}{file_suffix}"
        
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        uploaded_files[file_id] = {
            "filename": file.filename,
            "path": str(temp_file_path),
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with agent routing"""
    start_time = time.time()
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Check if file is referenced
    has_file = False
    file_path = None
    if request.file_id and request.file_id in uploaded_files:
        has_file = True
        file_path = uploaded_files[request.file_id]["path"]
    
    try:
        # Route the message
        routing_decision = await router_agent.route_message(request.message, session_id, has_file)
        
        # Execute based on routing decision
        if routing_decision["agent"] == "docling" and has_file and file_path:
            response = await docling_agent.process_document(file_path, request.message)
            agent_used = "docling"
        elif routing_decision["agent"] == "web_search":
            response = await web_search_agent.search_web(request.message, request.message)
            agent_used = "web_search"
        elif routing_decision["action"] == "explain_capabilities":
            response = await router_agent.explain_capabilities(request.message, session_id)
            agent_used = "router (capabilities)"
        else:
            response = await router_agent.general_chat(request.message, session_id)
            agent_used = "router"
        
        processing_time = time.time() - start_time
        
        # Store in chat history
        chat_history.append({
            "session_id": session_id,
            "user_message": request.message,
            "assistant_response": response,
            "agent_used": agent_used,
            "routing_decision": routing_decision,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        })
        
        return ChatResponse(
            response=response,
            agent_used=agent_used,
            processing_time=round(processing_time, 2),
            session_id=session_id
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ChatResponse(
            response=f"❌ Error: {str(e)}",
            agent_used="error",
            processing_time=round(processing_time, 2),
            session_id=session_id
        )

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_messages": len(chat_history),
        "total_uploads": len(uploaded_files),
        "active_sessions": len(agent_conversations),
        "agents_available": ["router", "docling", "web_search"],
        "models": {
            "router": ROUTER_MODEL,
            "docling": DOCLING_MODEL,
            "web_search": "Brave Search API"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "multi-agent-system",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/last-doctags")
async def get_last_doctags():
    """Debug endpoint to see the last DocTags output"""
    return {
        "last_doctags": getattr(docling_agent, '_last_raw_output', 'No output yet'),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Multi-Agent System Backend")
    print("=" * 50)
    print(f"📍 Backend API: http://localhost:9050")
    print(f"🧠 Router Model: {ROUTER_MODEL}")
    print(f"📄 Docling Model: {DOCLING_MODEL}")
    print(f"🔧 Ollama API: {OLLAMA_API_URL}")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=9050)
