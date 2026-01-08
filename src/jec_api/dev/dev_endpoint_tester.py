"""
Dev Endpoint Tester Component.
Provides UI and logic for testing API endpoints directly from the dev console.
"""

import json
import inspect
from typing import Any, Dict, List, Optional, Type, get_type_hints, Union
from enum import Enum

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None


def extract_endpoint_schema(type_hint: Type) -> Dict[str, Any]:
    """
    Extract a JSON-serializable schema from a Python type hint.
    Supports Pydantic models, dataclasses, and basic types.
    """
    if type_hint is None:
        return {"type": "null"}
        
    # Handle Pydantic models
    if BaseModel and isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
        try:
            return type_hint.model_json_schema()
        except AttributeError:
            # Fallback for older Pydantic versions
            return type_hint.schema()
            
    # Handle primitive types
    if type_hint in (str, "str"):
        return {"type": "string"}
    if type_hint in (int, "int"):
        return {"type": "integer"}
    if type_hint in (float, "float"):
        return {"type": "number"}
    if type_hint in (bool, "bool"):
        return {"type": "boolean"}
    if type_hint in (list, "list", List):
        return {"type": "array"}
    if type_hint in (dict, "dict", Dict):
        return {"type": "object"}
        
    # Handle basic dataclasses or custom classes
    if hasattr(type_hint, "__annotations__"):
        properties = {}
        required = []
        for name, field_type in type_hint.__annotations__.items():
            properties[name] = extract_endpoint_schema(field_type)
            # Assume all fields are required for simplicity unless Optional
            if not _is_optional(field_type):
                required.append(name)
        
        return {
            "type": "object",
            "title": type_hint.__name__,
            "properties": properties,
            "required": required
        }
        
    return {"type": "string", "description": str(type_hint)}


def _is_optional(t: Type) -> bool:
    """Check if a type is Optional[T]."""
    if hasattr(t, "__origin__") and t.__origin__ is Union:
        return type(None) in t.__args__
    return False


def get_tester_html() -> tuple[str, str, str]:
    """
    Returns the HTML, CSS, and JS for the endpoint tester component.
    """
    
    html = """
    <div class="tester-container">    
        <div class="tester-content">
            <div class="tester-sidebar">
                <div class="search-box">
                    <input type="text" id="endpoint-search" placeholder="Search endpoints..." oninput="filterEndpoints()">
                </div>
                <div class="endpoint-list" id="endpoint-list">
                    <!-- Endpoints populated via JS -->
                </div>
            </div>
            
            <div class="tester-main">
                <div class="tester-empty-state" id="tester-empty-state">
                    Select an endpoint to start testing
                </div>
                
                <div class="tester-workspace hidden" id="tester-workspace">
                    <div class="workspace-header">
                        <div class="method-badge" id="selected-method">GET</div>
                        <div class="path-display" id="selected-path">/api/path</div>
                    </div>
                    
                    <div class="workspace-split">
                        <div class="workspace-input">
                            <div class="section-title">Request Body</div>
                            <div class="editor-container">
                                <textarea id="request-editor" spellcheck="false" placeholder="Enter request body..."></textarea>
                            </div>
                            <div class="input-actions">
                                <button class="tester-btn tester-btn-primary" id="send-btn" onclick="sendRequest()">
                                    <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                                    <span>Send Request</span>
                                </button>
                                <button class="tester-btn" onclick="resetDefaultBody()">
                                    <svg viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
                                    Reset
                                </button>
                            </div>
                        </div>
                        
                        <div class="workspace-output">
                            <div class="section-title">
                                Response
                                <span class="response-status hidden" id="response-status">200 OK</span>
                                <span class="response-time hidden" id="response-time">120ms</span>
                            </div>
                            <div class="editor-container">
                                <div id="response-viewer" class="code-viewer"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    css = """
    .tester-overlay {
        position: fixed;
        top: 60px;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--bg-primary);
        z-index: 50;
        transform: translateY(100%);
        opacity: 0;
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease;
        display: flex;
        flex-direction: column;
    }
    
    .tester-overlay.visible {
        transform: translateY(0);
        opacity: 1;
    }
    
    .tester-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        animation: fadeInUp 0.3s ease forwards;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .tester-content {
        flex: 1;
        display: flex;
        overflow: hidden;
    }
    
    .tester-sidebar {
        width: 320px;
        border-right: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
    }
    
    .search-box {
        padding: 16px;
        border-bottom: 1px solid var(--border);
        background: var(--bg-elevated);
    }
    
    .search-box input {
        width: 100%;
        padding: 10px 14px;
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-primary);
        font-size: 13px;
        outline: none;
        transition: all 0.2s ease;
    }
    
    .search-box input::placeholder {
        color: var(--text-dim);
    }
    
    .search-box input:focus {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
    
    .endpoint-list {
        flex: 1;
        overflow-y: auto;
        padding: 8px 0;
    }
    
    .endpoint-item {
        padding: 12px 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2px 8px;
        border-radius: 8px;
        border: 1px solid transparent;
        transition: all 0.15s ease;
    }
    
    .endpoint-item:hover {
        background: var(--bg-hover);
        border-color: var(--border);
    }
    
    .endpoint-item.active {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    .endpoint-item .path {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
    }
    
    .endpoint-item.active .path {
        color: var(--text-primary);
    }
    
    .tester-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: var(--bg-primary);
        overflow: hidden;
    }
    
    .tester-empty-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--text-dim);
        font-size: 14px;
        gap: 16px;
    }
    
    .tester-empty-state::before {
        content: '';
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .tester-workspace {
        display: flex;
        flex-direction: column;
        height: 100%;
        animation: fadeIn 0.25s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .workspace-header {
        padding: 20px 24px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 16px;
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    }
    
    .workspace-header .method-badge {
        padding: 6px 12px;
        font-size: 11px;
    }
    
    .path-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 15px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .workspace-split {
        flex: 1;
        display: flex;
        overflow: hidden;
    }
    
    .workspace-input, .workspace-output {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 20px;
        min-width: 0;
    }
    
    .workspace-input {
        border-right: 1px solid var(--border);
        background: var(--bg-primary);
    }
    
    .workspace-output {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }
    
    .section-title {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        height: 24px;
    }
    
    .editor-container {
        flex: 1;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
        position: relative;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .editor-container:focus-within {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    #request-editor {
        width: 100%;
        height: 100%;
        background: transparent;
        border: none;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        padding: 16px;
        resize: none;
        outline: none;
        line-height: 1.6;
    }
    
    #request-editor::placeholder {
        color: var(--text-dim);
    }
    
    #request-editor:disabled {
        background: var(--bg-primary);
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .code-viewer {
        width: 100%;
        height: 100%;
        overflow: auto;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--text-primary);
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    .code-viewer .key { color: #60a5fa; }
    .code-viewer .string { color: #34d399; }
    .code-viewer .number { color: #fb923c; }
    .code-viewer .boolean { color: #a78bfa; }
    .code-viewer .null { color: var(--text-dim); font-style: italic; }
    
    .input-actions {
        margin-top: 16px;
        display: flex;
        gap: 12px;
    }
    
    .tester-btn {
        padding: 10px 18px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 13px;
        font-family: inherit;
        font-weight: 500;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .tester-btn:hover {
        background: var(--bg-hover);
        border-color: var(--border-light);
        color: var(--text-primary);
        transform: translateY(-1px);
    }
    
    .tester-btn:active {
        transform: translateY(0);
    }
    
    .tester-btn-primary {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .tester-btn-primary:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
        color: white;
    }
    
    .tester-btn-primary:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none !important;
    }
    
    .tester-btn svg {
        width: 16px;
        height: 16px;
        stroke: currentColor;
        stroke-width: 2;
        fill: none;
    }
    
    .hidden { display: none !important; }
    
    .response-status {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    .response-status.success { 
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.15) 100%);
        color: var(--accent-green);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .response-status.error { 
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.15) 100%);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .response-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--text-muted);
        padding: 4px 8px;
        background: var(--bg-hover);
        border-radius: 4px;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    """
    
    js = """
    let endpoints = [];
    let selectedEndpoint = null;
    
    async function loadEndpoints() {
        try {
            const res = await fetch(API_BASE + '/api/endpoints');
            endpoints = await res.json();
            renderEndpoints();
        } catch (e) {
            console.error('Failed to load endpoints', e);
        }
    }
    
    function filterEndpoints() {
        const query = document.getElementById('endpoint-search').value.toLowerCase();
        renderEndpoints(query);
    }
    
    function renderEndpoints(query = '') {
        const list = document.getElementById('endpoint-list');
        list.innerHTML = endpoints
            .filter(e => e.path.toLowerCase().includes(query) || e.method.toLowerCase().includes(query))
            .map(e => `
                <div class="endpoint-item ${selectedEndpoint && selectedEndpoint.path === e.path && selectedEndpoint.method === e.method ? 'active' : ''}" 
                     onclick="selectEndpoint('${e.method}', '${e.path}')">
                    <span class="method-badge method-${e.method}">${e.method}</span>
                    <span class="path">${escapeHtml(e.path)}</span>
                </div>
            `).join('');
    }
    
    function selectEndpoint(method, path) {
        selectedEndpoint = endpoints.find(e => e.method === method && e.path === path);
        if (!selectedEndpoint) return;
        
        renderEndpoints(document.getElementById('endpoint-search').value.toLowerCase());
        
        document.getElementById('tester-empty-state').classList.add('hidden');
        document.getElementById('tester-workspace').classList.remove('hidden');
        
        document.getElementById('selected-method').className = `method-badge method-${selectedEndpoint.method}`;
        document.getElementById('selected-method').textContent = selectedEndpoint.method;
        document.getElementById('selected-path').textContent = selectedEndpoint.path;
        
        resetDefaultBody();
        document.getElementById('response-viewer').textContent = '';
        document.getElementById('response-status').classList.add('hidden');
        document.getElementById('response-time').classList.add('hidden');
    }
    
    function getExampleFromSchema(schema) {
        if (!schema) return {};
        
        if (schema.properties) {
            const obj = {};
            for (const [key, prop] of Object.entries(schema.properties)) {
                obj[key] = getExampleFromSchema(prop);
            }
            return obj;
        }
        
        if (schema.type === 'string') return "string_value";
        if (schema.type === 'integer') return 0;
        if (schema.type === 'number') return 0.0;
        if (schema.type === 'boolean') return false;
        if (schema.type === 'array') return [];
        return null;
    }
    
    function resetDefaultBody() {
        if (!selectedEndpoint) return;
        
        const editor = document.getElementById('request-editor');
        if (['GET', 'DELETE', 'HEAD'].includes(selectedEndpoint.method)) {
            editor.value = '';
            editor.disabled = true;
            editor.placeholder = 'No body for ' + selectedEndpoint.method;
        } else {
            editor.disabled = false;
            editor.placeholder = 'Enter JSON request body...';
            
            if (selectedEndpoint.input_schema) {
                try {
                    const example = getExampleFromSchema(selectedEndpoint.input_schema);
                    editor.value = JSON.stringify(example, null, 2);
                } catch (e) {
                    editor.value = '{}';
                }
            } else {
                editor.value = '{}';
            }
        }
    }
    
    async function sendRequest() {
        if (!selectedEndpoint) return;
        
        const btn = document.getElementById('send-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner"></span><span>Sending...</span>';
        btn.disabled = true;
        
        const startTime = performance.now();
        
        try {
            const options = {
                method: selectedEndpoint.method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // Add body if applicable
            const editor = document.getElementById('request-editor');
            if (!editor.disabled && editor.value.trim()) {
                try {
                    // Try to parse to ensure valid JSON
                    const body = JSON.parse(editor.value);
                    options.body = JSON.stringify(body);
                } catch (e) {
                    alert('Invalid JSON in request body');
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    return;
                }
            }
            
            const res = await fetch(selectedEndpoint.path, options);
            const endTime = performance.now();
            
            // Update status
            const statusEl = document.getElementById('response-status');
            statusEl.textContent = `${res.status} ${res.statusText}`;
            statusEl.className = `response-status ${res.ok ? 'success' : 'error'}`;
            statusEl.classList.remove('hidden');
            
            // Update time
            const timeEl = document.getElementById('response-time');
            timeEl.textContent = `${(endTime - startTime).toFixed(0)}ms`;
            timeEl.classList.remove('hidden');
            
            // Handle output
            const viewer = document.getElementById('response-viewer');
            
            // Check content type
            const contentType = res.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await res.json();
                viewer.innerHTML = formatJson(data);
            } else {
                const text = await res.text();
                // Check if it might be a large blob/binary
                if (text.length > 100000) {
                     viewer.textContent = `[Large response: ${text.length} bytes]`;
                } else {
                     viewer.textContent = text;
                }
            }
            
        } catch (e) {
            document.getElementById('response-viewer').textContent = 'Error: ' + e.message;
            document.getElementById('response-status').textContent = 'Network Error';
            document.getElementById('response-status').className = 'response-status error';
            document.getElementById('response-status').classList.remove('hidden');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
    
    function formatJson(data) {
        const json = JSON.stringify(data, null, 2);
        return json.replace(/("(\\\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                    match = match.replace(/:$/, '');
                    return `<span class="${cls}">${escapeHtml(match)}</span>:`; 
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return `<span class="${cls}">${escapeHtml(match)}</span>`;
        });
    }
    """
    
    return html, css, js
