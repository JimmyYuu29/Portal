"""
Portal - Forvis Mazars Internal Automation Tools Portal
=======================================================
Version: 2.0.0
Based on: Standard v3.1 Enhanced

Features:
- Login / Register (RBAC by department & role)
- Admin panel (user management)
- Forgot password (Power Automate email)
- Reset password (one-time token, 30 min)
- Change password (logged-in users)
- /go/<app_id> redirect with access control + statistics
- External data directory (DATA_DIR) persistence
"""

import os
import json
import sqlite3
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, jsonify, request, redirect, url_for,
    flash, g, session, abort,
)
from flask_wtf import CSRFProtect
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    get_db, close_db, init_db,
    DEPARTMENTS, DEPARTMENT_CHOICES, ROLES, ROLE_CHOICES,
)
from power_automate_client import PowerAutomateClient

# ============================================================
# App Factory-style Initialization
# ============================================================

app = Flask(__name__)

# ---------- Configuration ----------
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), 'data'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',
    os.environ.get('PORTAL_SECRET_KEY', 'dev-secret-key-change-in-production'))
app.config['DATABASE'] = os.path.join(DATA_DIR, 'users.db')
app.config['APPS_CONFIG'] = os.path.join(os.path.dirname(__file__), 'apps_config.json')

# Session cookie security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
if os.environ.get('PORTAL_HTTPS', '').lower() == 'true':
    app.config['SESSION_COOKIE_SECURE'] = True

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# Domain for password reset links
PORTAL_DOMAIN = os.environ.get('PORTAL_DOMAIN', 'http://localhost:5000')

# ---------- Logging (sanitized) ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('portal')

# ---------- Extensions ----------
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para acceder.'
login_manager.login_message_category = 'warning'

pa_client = PowerAutomateClient()
pa_client.init_app(app)

# ---------- DB lifecycle ----------
app.teardown_appcontext(close_db)

# Ensure DATA_DIR and DB exist
os.makedirs(DATA_DIR, exist_ok=True)
init_db(app)


# ============================================================
# User Model for Flask-Login
# ============================================================

class User(UserMixin):
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.password_hash = row['password_hash']
        self.role = row['role']
        self.department = row['department']
        self.otros_detalle = row['otros_detalle'] or ''
        self.is_admin = bool(row['is_admin'])
        self.enabled = bool(row['enabled'])
        self.created_at = row['created_at']

    @property
    def is_active(self):
        return self.enabled

    @property
    def department_display(self):
        return DEPARTMENTS.get(self.department, self.department)

    @property
    def role_display(self):
        return ROLES.get(self.role, self.role)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        return User(row)
    return None


# ============================================================
# Helper: Admin required decorator
# ============================================================

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ============================================================
# App Config Management
# ============================================================

def load_apps_config():
    """Load APP configuration file."""
    config_path = app.config['APPS_CONFIG']
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error("Error loading apps config: %s", e)
    return {"apps": [], "categories": []}


def get_accessible_apps(user):
    """Return apps the user has access to (RBAC filtering)."""
    config = load_apps_config()
    all_apps = config.get('apps', [])
    if user.is_admin:
        return [a for a in all_apps if a.get('enabled', True)]

    accessible = []
    for app_item in all_apps:
        if not app_item.get('enabled', True):
            continue
        access = app_item.get('access', {})
        allowed_depts = access.get('departments', [])
        allowed_roles = access.get('roles', [])

        dept_ok = (not allowed_depts) or (user.department in allowed_depts)
        role_ok = (not allowed_roles) or (user.role in allowed_roles)

        if dept_ok and role_ok:
            accessible.append(app_item)
    return accessible


def get_apps_by_category(user):
    """Group accessible apps by category."""
    config = load_apps_config()
    categories = config.get('categories', [])
    accessible = get_accessible_apps(user)

    categorized = {}
    for cat in categories:
        categorized[cat['id']] = {
            'name': cat['name'],
            'icon': cat.get('icon', 'folder'),
            'apps': [],
        }
    categorized['other'] = {'name': 'Otros', 'icon': 'more-horizontal', 'apps': []}

    for app_item in accessible:
        cat_id = app_item.get('category', 'other')
        if cat_id in categorized:
            categorized[cat_id]['apps'].append(app_item)
        else:
            categorized['other']['apps'].append(app_item)

    return {k: v for k, v in categorized.items() if v['apps']}


def check_app_access(user, app_id):
    """Check if user can access a specific app. Returns (allowed, app_item)."""
    config = load_apps_config()
    apps = config.get('apps', [])
    target = None
    for a in apps:
        if a['id'] == app_id:
            target = a
            break
    if not target:
        return False, None
    if user.is_admin:
        return True, target

    access = target.get('access', {})
    allowed_depts = access.get('departments', [])
    allowed_roles = access.get('roles', [])
    dept_ok = (not allowed_depts) or (user.department in allowed_depts)
    role_ok = (not allowed_roles) or (user.role in allowed_roles)
    return (dept_ok and role_ok), target


# ============================================================
# Statistics helpers
# ============================================================

def record_portal_visit():
    """Record portal page visit."""
    try:
        db = get_db()
        today = datetime.now().date()
        ip = request.remote_addr or '0.0.0.0'
        db.execute('''
            INSERT INTO portal_stats (date, page_views, unique_visitors)
            VALUES (?, 1, 0)
            ON CONFLICT(date) DO UPDATE SET page_views = page_views + 1
        ''', (today,))
        try:
            db.execute('INSERT INTO daily_visitors (date, ip_address) VALUES (?, ?)', (today, ip))
            db.execute('UPDATE portal_stats SET unique_visitors = unique_visitors + 1 WHERE date = ?', (today,))
        except sqlite3.IntegrityError:
            pass
        db.commit()
    except Exception as e:
        logger.error("Error recording portal visit: %s", e)


def record_app_visit(app_id, username=None):
    """Record app redirect visit."""
    try:
        db = get_db()
        now = datetime.now()
        db.execute('''
            INSERT INTO access_logs (app_id, username, timestamp, ip_address, user_agent, request_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (app_id, username, now, request.remote_addr,
              request.user_agent.string, request.headers.get('X-Request-ID', '')))
        db.execute('''
            INSERT INTO app_stats (app_id, total_visits, last_visit)
            VALUES (?, 1, ?)
            ON CONFLICT(app_id) DO UPDATE SET total_visits = total_visits + 1, last_visit = ?
        ''', (app_id, now, now))
        db.commit()
    except Exception as e:
        logger.error("Error recording app visit: %s", e)


def get_dashboard_stats():
    """Get dashboard statistics."""
    default = {
        'today': {'page_views': 0, 'unique_visitors': 0},
        'total': {'page_views': 0, 'unique_visitors': 0},
        'top_apps': [], 'weekly_trend': [],
    }
    try:
        db = get_db()
        today = datetime.now().date()
        ts = db.execute(
            'SELECT COALESCE(page_views,0) as pv, COALESCE(unique_visitors,0) as uv FROM portal_stats WHERE date=?',
            (today,)).fetchone()
        total = db.execute(
            'SELECT COALESCE(SUM(page_views),0) as tpv, COALESCE(SUM(unique_visitors),0) as tuv FROM portal_stats'
        ).fetchone()
        top = db.execute(
            'SELECT app_id, total_visits, last_visit FROM app_stats ORDER BY total_visits DESC LIMIT 10'
        ).fetchall()
        week_ago = today - timedelta(days=7)
        trend = db.execute(
            'SELECT date, page_views, unique_visitors FROM portal_stats WHERE date>=? ORDER BY date',
            (week_ago,)).fetchall()
        return {
            'today': {'page_views': ts['pv'] if ts else 0, 'unique_visitors': ts['uv'] if ts else 0},
            'total': {'page_views': total['tpv'] if total else 0, 'unique_visitors': total['tuv'] if total else 0},
            'top_apps': [dict(r) for r in top],
            'weekly_trend': [dict(r) for r in trend],
        }
    except Exception as e:
        logger.error("Error getting dashboard stats: %s", e)
        return default


def log_audit(action, username=None, detail=None, ip=None):
    """Write an audit log entry (no sensitive data)."""
    try:
        db = get_db()
        db.execute(
            'INSERT INTO audit_log (action, username, detail, ip_address) VALUES (?,?,?,?)',
            (action, username, detail, ip or (request.remote_addr if request else None))
        )
        db.commit()
    except Exception:
        pass


# ============================================================
# Routes: Authentication
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if row and check_password_hash(row['password_hash'], password):
            user = User(row)
            if not user.enabled:
                flash('Tu cuenta está deshabilitada. Contacta al administrador.', 'danger')
                return render_template('login.html')
            login_user(user, remember=False)
            session.permanent = True
            log_audit('LOGIN', username=username)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        role = request.form.get('role', 'junior')
        department = request.form.get('department', 'otros')
        otros_detalle = request.form.get('otros_detalle', '').strip()

        errors = []
        if not username or len(username) < 2:
            errors.append('El nombre de usuario debe tener al menos 2 caracteres.')
        if not password or len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if password != password2:
            errors.append('Las contraseñas no coinciden.')
        if role not in ROLES:
            errors.append('Rol inválido.')
        if department not in DEPARTMENTS:
            errors.append('Departamento inválido.')
        if department == 'otros' and not otros_detalle:
            errors.append('Debes especificar el detalle para "Otros".')

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            errors.append('El nombre de usuario ya está registrado.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html',
                                   departments=DEPARTMENT_CHOICES, roles=ROLE_CHOICES,
                                   form=request.form)

        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        db.execute(
            """INSERT INTO users (username, password_hash, role, department, otros_detalle, is_admin, enabled)
               VALUES (?, ?, ?, ?, ?, 0, 1)""",
            (username, pw_hash, role, department, otros_detalle)
        )
        db.commit()
        log_audit('REGISTER', username=username, detail=f"dept={department}, role={role}")
        flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html',
                           departments=DEPARTMENT_CHOICES, roles=ROLE_CHOICES, form={})


@app.route('/logout')
@login_required
def logout():
    log_audit('LOGOUT', username=current_user.username)
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


# ============================================================
# Routes: Forgot / Reset Password
# ============================================================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()

        # Always show same message (anti-enumeration)
        flash_msg = 'Si la cuenta existe, recibirás un correo con instrucciones en unos minutos.'

        db = get_db()
        row = db.execute("SELECT * FROM users WHERE username = ? AND enabled = 1", (username,)).fetchone()
        if row:
            # Generate one-time token
            token = secrets.token_urlsafe(48)
            expires = datetime.utcnow() + timedelta(minutes=30)
            db.execute(
                "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
                (row['id'], token, expires)
            )
            db.commit()

            # Build reset link
            reset_link = f"{PORTAL_DOMAIN}/reset-password/{token}"

            # Determine email recipient
            email_to = username  # In corporate env, username IS the corporate account/email

            # Send via Power Automate
            pa_client.send_password_reset_email(
                to=email_to,
                username=username,
                reset_link=reset_link,
                request_ip=request.remote_addr or '0.0.0.0',
                expires_minutes=30,
            )
            log_audit('FORGOT_PASSWORD_REQUEST', username=username)

        flash(flash_msg, 'info')
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db = get_db()
    row = db.execute(
        """SELECT prt.*, u.username FROM password_reset_tokens prt
           JOIN users u ON prt.user_id = u.id
           WHERE prt.token = ? AND prt.used = 0 AND prt.expires_at > ?""",
        (token, datetime.utcnow())
    ).fetchone()

    if not row:
        flash('El enlace de restablecimiento es inválido o ha expirado.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        if not password or len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('reset_password.html', token=token)
        if password != password2:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_password.html', token=token)

        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        db.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                   (pw_hash, datetime.utcnow(), row['user_id']))
        db.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = ?", (row['id'],))
        db.commit()
        log_audit('PASSWORD_RESET', username=row['username'])
        flash('¡Contraseña restablecida con éxito! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# ============================================================
# Routes: Change Password (logged-in)
# ============================================================

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pw = request.form.get('old_password', '')
        new_pw = request.form.get('new_password', '')
        new_pw2 = request.form.get('new_password2', '')

        if not check_password_hash(current_user.password_hash, old_pw):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('change_password.html')
        if not new_pw or len(new_pw) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('change_password.html')
        if new_pw != new_pw2:
            flash('Las nuevas contraseñas no coinciden.', 'danger')
            return render_template('change_password.html')

        db = get_db()
        pw_hash = generate_password_hash(new_pw, method='pbkdf2:sha256', salt_length=16)
        db.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                   (pw_hash, datetime.utcnow(), current_user.id))
        db.commit()
        log_audit('PASSWORD_CHANGE', username=current_user.username)

        # Force re-login
        logout_user()
        flash('Contraseña cambiada con éxito. Por favor, inicia sesión de nuevo.', 'success')
        return redirect(url_for('login'))

    return render_template('change_password.html')


# ============================================================
# Routes: Dashboard (main portal page, requires login)
# ============================================================

@app.route('/')
def index():
    """Redirect root to dashboard (requires login) or login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main portal dashboard showing accessible apps."""
    record_portal_visit()
    apps_by_cat = get_apps_by_category(current_user)
    stats = get_dashboard_stats()
    config = load_apps_config()

    return render_template('dashboard.html',
                           apps_by_category=apps_by_cat,
                           stats=stats,
                           portal_name=config.get('portal_name', 'Portal de Herramientas'),
                           portal_description=config.get('portal_description', ''),
                           user=current_user,
                           departments=DEPARTMENTS,
                           roles=ROLES)


# ============================================================
# Routes: App Redirect with RBAC
# ============================================================

@app.route('/go/<app_id>')
@login_required
def go_to_app(app_id):
    """Redirect to app after RBAC check + access logging."""
    allowed, target_app = check_app_access(current_user, app_id)

    if not target_app:
        return render_template('error.html', message='Aplicación no encontrada.'), 404

    if not allowed:
        log_audit('ACCESS_DENIED', username=current_user.username, detail=f"app={app_id}")
        return render_template('error.html',
                               message='No tienes permiso para acceder a esta aplicación. '
                                       'Contacta al administrador si crees que es un error.'), 403

    # Record access
    record_app_visit(app_id, username=current_user.username)

    # Build redirect URL
    target_url = target_app['url']
    config = load_apps_config()

    if target_url.startswith('/') and not target_url.startswith('//'):
        server_ip = config.get('server_ip', '')
        target_port = target_app.get('port')
        request_port = request.host.split(':')[-1] if ':' in request.host else '80'
        if request_port not in ['80', '443'] and target_port and server_ip:
            target_url = f'http://{server_ip}:{target_port}/'

    return redirect(target_url)


# ============================================================
# Routes: Admin Panel
# ============================================================

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel - user management."""
    db = get_db()
    search = request.args.get('search', '').strip()
    if search:
        users = db.execute(
            "SELECT * FROM users WHERE username LIKE ? ORDER BY created_at DESC",
            (f'%{search}%',)
        ).fetchall()
    else:
        users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()

    return render_template('admin.html',
                           users=users,
                           search=search,
                           departments=DEPARTMENTS,
                           roles=ROLES,
                           department_choices=DEPARTMENT_CHOICES,
                           role_choices=ROLE_CHOICES)


@app.route('/admin/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def admin_edit_user(user_id):
    """Admin: edit user role/department/enabled."""
    db = get_db()
    user_row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user_row:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_panel'))

    role = request.form.get('role', user_row['role'])
    department = request.form.get('department', user_row['department'])
    otros_detalle = request.form.get('otros_detalle', user_row['otros_detalle'] or '')
    enabled = request.form.get('enabled', '0')
    enabled_val = 1 if enabled == '1' else 0

    if role not in ROLES:
        role = user_row['role']
    if department not in DEPARTMENTS:
        department = user_row['department']

    db.execute(
        """UPDATE users SET role=?, department=?, otros_detalle=?, enabled=?, updated_at=?
           WHERE id=?""",
        (role, department, otros_detalle, enabled_val, datetime.utcnow(), user_id)
    )
    db.commit()
    log_audit('ADMIN_EDIT_USER', username=current_user.username,
              detail=f"target={user_row['username']}, role={role}, dept={department}, enabled={enabled_val}")
    flash(f'Usuario {user_row["username"]} actualizado.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def admin_reset_user_password(user_id):
    """Admin: generate a temporary password for a user."""
    db = get_db()
    user_row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user_row:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_panel'))

    temp_pw = secrets.token_urlsafe(10)
    pw_hash = generate_password_hash(temp_pw, method='pbkdf2:sha256', salt_length=16)
    db.execute("UPDATE users SET password_hash=?, updated_at=? WHERE id=?",
               (pw_hash, datetime.utcnow(), user_id))
    db.commit()
    log_audit('ADMIN_RESET_PASSWORD', username=current_user.username,
              detail=f"target={user_row['username']}")

    flash(f'Contraseña temporal generada para {user_row["username"]}: {temp_pw} '
          f'(El usuario deberá cambiarla al iniciar sesión)', 'warning')
    return redirect(url_for('admin_panel'))


# ============================================================
# API Routes (preserved)
# ============================================================

@app.route('/api/stats')
def api_stats():
    """Statistics API endpoint."""
    stats = get_dashboard_stats()
    return jsonify(stats)


@app.route('/api/apps')
def api_apps():
    """App list API endpoint."""
    config = load_apps_config()
    return jsonify(config.get('apps', []))


@app.route('/api/apps/<app_id>/stats')
def api_app_stats(app_id):
    """Single app statistics API."""
    db = get_db()
    stats = db.execute(
        'SELECT app_id, total_visits, last_visit FROM app_stats WHERE app_id = ?',
        (app_id,)
    ).fetchone()
    if not stats:
        return jsonify({'error': 'No se encontraron estadísticas'}), 404
    recent = db.execute(
        'SELECT timestamp, ip_address, username FROM access_logs WHERE app_id = ? ORDER BY timestamp DESC LIMIT 20',
        (app_id,)
    ).fetchall()
    return jsonify({
        'app_id': app_id,
        'total_visits': stats['total_visits'],
        'last_visit': stats['last_visit'],
        'recent_visits': [dict(r) for r in recent],
    })


@app.route('/health')
@csrf.exempt
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
    })


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message='Acceso denegado.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Página no encontrada.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Error interno del servidor.'), 500


# ============================================================
# Run
# ============================================================

if __name__ == '__main__':
    app.run(
        host=os.environ.get('PORTAL_HOST', '127.0.0.1'),
        port=int(os.environ.get('PORTAL_PORT', 5000)),
        debug=os.environ.get('PORTAL_DEBUG', 'false').lower() == 'true',
    )
