"""
AI龙龟共生伙伴操作系统 — 四层记忆管理
FourLayerMemorySystem: SOUL/USER/TOOLS/SESSION
"""

import os, json, sqlite3
from datetime import datetime
from typing import Optional


class FourLayerMemorySystem:
    """四层记忆系统"""
    LAYERS = ["soul", "user", "tools", "session"]
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), "..", "memory")
        os.makedirs(self.base_path, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        self.db_path = os.path.join(self.base_path, "memory.db")
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layer TEXT NOT NULL,
                content TEXT NOT NULL,
                importance INTEGER DEFAULT 5,
                tags TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                accessed_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()
    
    def store(self, layer: str, content: str, importance: int = 5, tags: str = ""):
        if layer not in self.LAYERS:
            raise ValueError(f"Invalid layer: {layer}")
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO memories (layer, content, importance, tags) VALUES (?,?,?,?)",
            (layer, content, importance, tags)
        )
        conn.commit()
        conn.close()
    
    def search(self, layer: Optional[str] = None, query: str = "", limit: int = 10):
        conn = sqlite3.connect(self.db_path)
        if layer:
            rows = conn.execute(
                "SELECT * FROM memories WHERE layer=? AND content LIKE ? ORDER BY importance DESC LIMIT ?",
                (layer, f"%{query}%", limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
                (f"%{query}%", limit)
            ).fetchall()
        conn.close()
        return [{"id": r[0], "layer": r[1], "content": r[2], "importance": r[3], "tags": r[4]} for r in rows]
    
    def get_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        stats = {}
        for layer in self.LAYERS:
            count = conn.execute("SELECT COUNT(*) FROM memories WHERE layer=?", (layer,)).fetchone()[0]
            stats[layer] = count
        conn.close()
        return stats
