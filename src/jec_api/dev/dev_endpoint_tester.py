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
                    
                    <div class="headers-section">
                        <div class="headers-toggle" onclick="toggleHeaders()">
                            <svg class="headers-chevron" id="headers-chevron" viewBox="0 0 24 24">
                                <polyline points="9 18 15 12 9 6"></polyline>
                            </svg>
                            <span class="headers-title">Headers</span>
                            <span class="headers-count" id="headers-count">2</span>
                        </div>
                        <div class="headers-list" id="headers-list">
                            <!-- Headers populated via JS -->
                        </div>
                    </div>
                    
                    <div class="workspace-split">
                        <div class="workspace-input">
                            <div class="section-title">Request Body</div>
                            <div class="editor-container">
                                <textarea id="request-editor" spellcheck="false" placeholder="Enter request body..."></textarea>
                            </div>
                            <div class="input-actions">
                                <button class="tester-btn" id="send-btn" onclick="sendRequest()">
                                    <span>Send</span>
                                </button>
                                <button class="tester-btn" onclick="resetDefaultBody()">
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
        border-color: var(--border-light);
    }
    
    .endpoint-list {
        flex: 1;
        overflow-y: auto;
        padding: 8px;
    }
    
    .endpoint-group {
        margin-bottom: 4px;
        border-radius: 8px;
        border: 1px solid var(--border);
        overflow: hidden;
        background: var(--bg-card);
        transition: all 0.2s ease;
    }
    
    .endpoint-group.expanded {
        border-color: var(--border-light);
    }
    
    .endpoint-group-header {
        padding: 12px 14px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: background 0.15s ease;
    }
    
    .endpoint-group-header:hover {
        background: var(--bg-hover);
    }
    
    .endpoint-group.expanded .endpoint-group-header {
        background: var(--bg-elevated);
        border-bottom: 1px solid var(--border);
    }
    
    .endpoint-group-chevron {
        width: 16px;
        height: 16px;
        stroke: var(--text-dim);
        stroke-width: 2;
        fill: none;
        transition: transform 0.2s ease;
        flex-shrink: 0;
    }
    
    .endpoint-group.expanded .endpoint-group-chevron {
        transform: rotate(90deg);
    }
    
    .endpoint-group-path {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--text-primary);
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .endpoint-group-count {
        font-size: 11px;
        color: var(--text-dim);
        background: var(--bg-primary);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .endpoint-group-methods {
        display: flex;
        gap: 4px;
    }
    
    .endpoint-group-methods .method-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;
    }
    
    .method-dot-GET { background: var(--accent-green); }
    .method-dot-POST { background: var(--accent-blue); }
    .method-dot-PUT { background: var(--accent-yellow); }
    .method-dot-DELETE { background: var(--accent-red); }
    .method-dot-PATCH { background: var(--accent-violet); }
    
    .endpoint-group-items {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.25s ease;
    }
    
    .endpoint-group.expanded .endpoint-group-items {
        max-height: 500px;
    }
    
    .endpoint-item {
        padding: 10px 14px 10px 40px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 1px solid var(--border);
        transition: all 0.1s ease;
    }
    
    .endpoint-item:last-child {
        border-bottom: none;
    }
    
    .endpoint-item:hover {
        background: var(--bg-hover);
    }
    
    .endpoint-item.active {
        background: var(--bg-active);
    }
    
    .endpoint-item .method-badge {
        font-size: 9px;
        padding: 2px 6px;
    }
    
    .endpoint-item .path {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
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
    
    .headers-section {
        border-bottom: 1px solid var(--border);
        background: var(--bg-primary);
    }
    
    .headers-toggle {
        padding: 10px 24px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        transition: background 0.15s;
    }
    
    .headers-toggle:hover {
        background: var(--bg-hover);
    }
    
    .headers-chevron {
        width: 14px;
        height: 14px;
        stroke: var(--text-dim);
        stroke-width: 2;
        fill: none;
        transition: transform 0.2s ease;
    }
    
    .headers-section.expanded .headers-chevron {
        transform: rotate(90deg);
    }
    
    .headers-title {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .headers-count {
        font-size: 10px;
        color: var(--text-dim);
        background: var(--bg-card);
        padding: 2px 6px;
        border-radius: 3px;
        margin-left: auto;
    }
    
    .headers-list {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.25s ease;
        background: var(--bg-card);
    }
    
    .headers-section.expanded .headers-list {
        max-height: 300px;
        overflow-y: auto;
    }
    
    .header-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 24px;
        border-bottom: 1px solid var(--border);
    }
    
    .header-row:last-child {
        border-bottom: none;
    }
    
    .header-row input {
        flex: 1;
        padding: 6px 10px;
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        outline: none;
        transition: border-color 0.15s;
    }
    
    .header-row input:focus {
        border-color: var(--border-light);
    }
    
    .header-row input::placeholder {
        color: var(--text-dim);
    }
    
    .header-row input.header-key {
        flex: 0.4;
    }
    
    .header-row input.header-value {
        flex: 0.6;
    }
    
    .header-row-remove {
        width: 24px;
        height: 24px;
        background: transparent;
        border: none;
        color: var(--text-dim);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.15s;
    }
    
    .header-row-remove:hover {
        background: var(--bg-hover);
        color: var(--accent-red);
    }
    
    .header-row-remove svg {
        width: 14px;
        height: 14px;
        stroke: currentColor;
        stroke-width: 2;
        fill: none;
    }
    
    .header-add-row {
        padding: 8px 24px;
    }
    
    .header-add-btn {
        padding: 4px 10px;
        background: transparent;
        border: 1px dashed var(--border);
        border-radius: 4px;
        color: var(--text-dim);
        cursor: pointer;
        font-size: 11px;
        font-family: inherit;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .header-add-btn:hover {
        border-color: var(--border-light);
        color: var(--text-secondary);
        background: var(--bg-hover);
    }
    
    .header-add-btn svg {
        width: 12px;
        height: 12px;
        stroke: currentColor;
        stroke-width: 2;
        fill: none;
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
        border-color: var(--border-light);
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
        gap: 10px;
    }
    
    .tester-btn {
        padding: 6px 12px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 12px;
        font-family: inherit;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .tester-btn:hover {
        background: var(--bg-hover);
        border-color: var(--border-light);
        color: var(--text-primary);
    }
    
    .tester-btn:active {
        background: var(--bg-active);
    }
    
    .tester-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .tester-btn svg {
        width: 14px;
        height: 14px;
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
        width: 12px;
        height: 12px;
        border: 2px solid var(--border);
        border-radius: 50%;
        border-top-color: var(--text-secondary);
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    """
    
    js = r"""
    let endpoints = [];
    let selectedEndpoint = null;
    let expandedGroup = null;
    let headersExpanded = false;
    let requestHeaders = [];
    
    const defaultHeaders = [
        { key: 'Content-Type', value: 'application/json' },
        { key: 'Accept', value: 'application/json' }
    ];
    
    function initHeaders() {
        requestHeaders = [...defaultHeaders];
        renderHeaders();
    }
    
    function toggleHeaders() {
        headersExpanded = !headersExpanded;
        const section = document.querySelector('.headers-section');
        if (headersExpanded) {
            section.classList.add('expanded');
        } else {
            section.classList.remove('expanded');
        }
    }
    
    function renderHeaders() {
        const list = document.getElementById('headers-list');
        const count = document.getElementById('headers-count');
        count.textContent = requestHeaders.length;
        
        list.innerHTML = requestHeaders.map((h, i) => `
            <div class="header-row">
                <input type="text" class="header-key" placeholder="Header name" 
                       value="${escapeHtml(h.key)}" onchange="updateHeader(${i}, 'key', this.value)">
                <input type="text" class="header-value" placeholder="Value" 
                       value="${escapeHtml(h.value)}" onchange="updateHeader(${i}, 'value', this.value)">
                <button class="header-row-remove" onclick="removeHeader(${i})" title="Remove">
                    <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
        `).join('') + `
            <div class="header-add-row">
                <button class="header-add-btn" onclick="addHeader()">
                    <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                    Add Header
                </button>
            </div>
        `;
    }
    
    function updateHeader(index, field, value) {
        if (requestHeaders[index]) {
            requestHeaders[index][field] = value;
        }
    }
    
    function addHeader() {
        requestHeaders.push({ key: '', value: '' });
        renderHeaders();
    }
    
    function removeHeader(index) {
        requestHeaders.splice(index, 1);
        renderHeaders();
    }
    
    function getHeadersObject() {
        const headers = {};
        for (const h of requestHeaders) {
            if (h.key.trim()) {
                headers[h.key.trim()] = h.value;
            }
        }
        return headers;
    }
    
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
    
    function groupEndpoints(filtered) {
        const groups = {};
        for (const e of filtered) {
            // Extract base path (first segment after leading /)
            const parts = e.path.split('/').filter(Boolean);
            const basePath = parts.length > 0 ? '/' + parts[0] : e.path;
            
            if (!groups[basePath]) {
                groups[basePath] = { path: basePath, endpoints: [], methods: new Set() };
            }
            groups[basePath].endpoints.push(e);
            groups[basePath].methods.add(e.method);
        }
        return Object.values(groups);
    }
    
    function renderEndpoints(query = '') {
        const list = document.getElementById('endpoint-list');
        const filtered = endpoints.filter(e => 
            e.path.toLowerCase().includes(query) || e.method.toLowerCase().includes(query)
        );
        
        const groups = groupEndpoints(filtered);
        
        list.innerHTML = groups.map(g => {
            const isExpanded = expandedGroup === g.path;
            const methodDots = [...g.methods].map(m => 
                `<span class="method-dot method-dot-${m}" title="${m}"></span>`
            ).join('');
            
            const endpointItems = g.endpoints.map(e => {
                const isActive = selectedEndpoint && 
                    selectedEndpoint.path === e.path && 
                    selectedEndpoint.method === e.method;
                return `
                    <div class="endpoint-item ${isActive ? 'active' : ''}" 
                         onclick="event.stopPropagation(); selectEndpoint('${e.method}', '${e.path}')">
                        <span class="method-badge method-${e.method}">${e.method}</span>
                        <span class="path">${escapeHtml(e.path)}</span>
                    </div>
                `;
            }).join('');
            
            return `
                <div class="endpoint-group ${isExpanded ? 'expanded' : ''}" data-path="${g.path}">
                    <div class="endpoint-group-header" onclick="toggleGroup('${g.path}')">
                        <svg class="endpoint-group-chevron" viewBox="0 0 24 24">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                        <span class="endpoint-group-path">${escapeHtml(g.path)}</span>
                        <span class="endpoint-group-methods">${methodDots}</span>
                        <span class="endpoint-group-count">${g.endpoints.length}</span>
                    </div>
                    <div class="endpoint-group-items">
                        ${endpointItems}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    function toggleGroup(path) {
        if (expandedGroup === path) {
            expandedGroup = null;
        } else {
            expandedGroup = path;
        }
        renderEndpoints(document.getElementById('endpoint-search').value.toLowerCase());
    }
    
    function selectEndpoint(method, path) {
        selectedEndpoint = endpoints.find(e => e.method === method && e.path === path);
        if (!selectedEndpoint) return;
        
        // Auto-expand the group containing this endpoint
        const parts = path.split('/').filter(Boolean);
        const basePath = parts.length > 0 ? '/' + parts[0] : path;
        expandedGroup = basePath;
        
        renderEndpoints(document.getElementById('endpoint-search').value.toLowerCase());
        
        document.getElementById('tester-empty-state').classList.add('hidden');
        document.getElementById('tester-workspace').classList.remove('hidden');
        
        document.getElementById('selected-method').className = `method-badge method-${selectedEndpoint.method}`;
        document.getElementById('selected-method').textContent = selectedEndpoint.method;
        document.getElementById('selected-path').textContent = selectedEndpoint.path;
        
        resetDefaultBody();
        initHeaders();
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
                headers: getHeadersObject()
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
