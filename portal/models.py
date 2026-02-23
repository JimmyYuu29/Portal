"""
Portal - Database Models & Initialization
==========================================
Manages SQLite database: users, password reset tokens, access logs, app stats.
All passwords are stored hashed+salted via werkzeug.security.
"""

import os
import sqlite3
from datetime import datetime
from flask import g, current_app
from werkzeug.security import generate_password_hash


# ============================================================
# Department ID mapping (internal_id -> display_name_es)
# ============================================================

DEPARTMENTS = {
    "auditoria": "Auditoría",
    "precio_transferencia": "Precio de Transferencia",
    "tax": "Tax",
    "legal": "Legal",
    "administracion_finanza": "Administración y Finanza",
    "it": "IT",
    "quality_risk": "Quality & Risk Management",
    "aos": "AOS",
    "otros": "Otros",
}

DEPARTMENT_CHOICES = [(k, v) for k, v in DEPARTMENTS.items()]

# ============================================================
# Role definitions
# ============================================================

ROLES = {
    "junior": "Junior",
    "senior": "Senior",
    "manager": "Manager",
    "socio": "Socio",
}

ROLE_CHOICES = [(k, v) for k, v in ROLES.items()]


# ============================================================
# Database helpers
# ============================================================

def get_db():
    """Get database connection for current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database tables and default Admin user."""
    db_path = app.config['DATABASE']
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row

    conn.executescript('''
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'junior',
            department TEXT NOT NULL DEFAULT 'otros',
            otros_detalle TEXT DEFAULT '',
            is_admin INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Password reset tokens
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Access logs (app redirect tracking)
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT NOT NULL,
            username TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            request_id TEXT
        );

        -- App visit statistics
        CREATE TABLE IF NOT EXISTS app_stats (
            app_id TEXT PRIMARY KEY,
            total_visits INTEGER DEFAULT 0,
            last_visit DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Portal page view statistics
        CREATE TABLE IF NOT EXISTS portal_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE,
            page_views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0
        );

        -- Daily unique visitors tracking
        CREATE TABLE IF NOT EXISTS daily_visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            ip_address TEXT,
            UNIQUE(date, ip_address)
        );

        -- Audit log for sensitive operations
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            username TEXT,
            detail TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_access_logs_app_id ON access_logs(app_id);
        CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_portal_stats_date ON portal_stats(date);
        CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token);
        CREATE INDEX IF NOT EXISTS idx_reset_tokens_user ON password_reset_tokens(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
    ''')

    # Seed Admin user if not exists
    existing = conn.execute(
        "SELECT id FROM users WHERE username = 'Admin'"
    ).fetchone()

    if not existing:
        conn.execute(
            """INSERT INTO users (username, password_hash, role, department, is_admin, enabled)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                'Admin',
                generate_password_hash('Admin123', method='pbkdf2:sha256', salt_length=16),
                'manager',
                'it',
                1,
                1,
            )
        )
        app.logger.info("Default Admin user created.")

    conn.commit()
    conn.close()
