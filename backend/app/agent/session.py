"""内存会话：多轮状态、待确认报价、附件上下文。"""
from __future__ import annotations

import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.agent.config import SESSION_TTL_SECONDS


@dataclass
class UploadedFile:
    filename: str
    content: bytes
    text_preview: str = ""


@dataclass
class AgentSession:
    session_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    quote_type: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)
    pending_quote: Optional[Dict[str, Any]] = None
    confirmed_quote: Optional[Dict[str, Any]] = None
    last_bom_items: List[Dict[str, Any]] = field(default_factory=list)
    files: List[UploadedFile] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = time.time()


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, AgentSession] = {}

    def _purge_locked(self) -> None:
        now = time.time()
        expired = [
            sid
            for sid, s in self._sessions.items()
            if now - s.updated_at > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]

    def get_or_create(self, session_id: Optional[str] = None) -> AgentSession:
        with self._lock:
            self._purge_locked()
            sid = (session_id or "").strip() or str(uuid.uuid4())
            sess = self._sessions.get(sid)
            if sess is None:
                sess = AgentSession(session_id=sid)
                self._sessions[sid] = sess
            sess.touch()
            return sess

    def get(self, session_id: str) -> Optional[AgentSession]:
        with self._lock:
            self._purge_locked()
            sess = self._sessions.get(session_id)
            if sess:
                sess.touch()
            return sess

    def save(self, session: AgentSession) -> None:
        with self._lock:
            session.touch()
            self._sessions[session.session_id] = session


store = SessionStore()
