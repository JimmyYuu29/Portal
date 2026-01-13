"""
Portal - 咨询事务所内部自动化工具统一入口
Internal Automation Tool Portal for Consulting Firm

Version: 1.0.0
Based on: Standard v3.1 Enhanced
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, jsonify, request, redirect, g

# ============================================================
# 配置
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('PORTAL_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'data', 'portal.db')
app.config['APPS_CONFIG'] = os.path.join(os.path.dirname(__file__), 'apps_config.json')

# ============================================================
# 数据库管理
# ============================================================

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库"""
    db = get_db()
    db.executescript('''
        -- 访问日志表
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            request_id TEXT
        );

        -- APP统计汇总表
        CREATE TABLE IF NOT EXISTS app_stats (
            app_id TEXT PRIMARY KEY,
            total_visits INTEGER DEFAULT 0,
            last_visit DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Portal访问统计表
        CREATE TABLE IF NOT EXISTS portal_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE,
            page_views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0
        );

        -- 每日访问者IP记录（用于计算UV）
        CREATE TABLE IF NOT EXISTS daily_visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            ip_address TEXT,
            UNIQUE(date, ip_address)
        );

        -- 创建索引以提高查询性能
        CREATE INDEX IF NOT EXISTS idx_access_logs_app_id ON access_logs(app_id);
        CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_portal_stats_date ON portal_stats(date);
    ''')
    db.commit()


app.teardown_appcontext(close_db)


# ============================================================
# APP配置管理
# ============================================================

def load_apps_config():
    """加载APP配置文件"""
    config_path = app.config['APPS_CONFIG']
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"apps": [], "categories": []}


def save_apps_config(config):
    """保存APP配置文件"""
    config_path = app.config['APPS_CONFIG']
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_apps_by_category():
    """按分类获取APP列表"""
    config = load_apps_config()
    apps = config.get('apps', [])
    categories = config.get('categories', [])

    # 按分类组织APP
    categorized = {}
    for cat in categories:
        categorized[cat['id']] = {
            'name': cat['name'],
            'icon': cat.get('icon', 'folder'),
            'apps': []
        }

    # 添加"其他"分类
    categorized['other'] = {
        'name': '其他 / Other',
        'icon': 'more-horizontal',
        'apps': []
    }

    for app_item in apps:
        if app_item.get('enabled', True):
            cat_id = app_item.get('category', 'other')
            if cat_id in categorized:
                categorized[cat_id]['apps'].append(app_item)
            else:
                categorized['other']['apps'].append(app_item)

    # 移除空分类
    return {k: v for k, v in categorized.items() if v['apps']}


# ============================================================
# 统计功能
# ============================================================

def record_portal_visit():
    """记录Portal访问"""
    db = get_db()
    today = datetime.now().date()
    ip = request.remote_addr

    # 更新PV
    db.execute('''
        INSERT INTO portal_stats (date, page_views, unique_visitors)
        VALUES (?, 1, 0)
        ON CONFLICT(date) DO UPDATE SET page_views = page_views + 1
    ''', (today,))

    # 尝试记录UV（如果是新访客）
    try:
        db.execute('''
            INSERT INTO daily_visitors (date, ip_address) VALUES (?, ?)
        ''', (today, ip))
        # 新访客，更新UV
        db.execute('''
            UPDATE portal_stats SET unique_visitors = unique_visitors + 1 WHERE date = ?
        ''', (today,))
    except sqlite3.IntegrityError:
        pass  # 已经记录过

    db.commit()


def record_app_visit(app_id):
    """记录APP访问"""
    db = get_db()
    now = datetime.now()

    # 记录访问日志
    db.execute('''
        INSERT INTO access_logs (app_id, timestamp, ip_address, user_agent, request_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (app_id, now, request.remote_addr, request.user_agent.string, request.headers.get('X-Request-ID', '')))

    # 更新汇总统计
    db.execute('''
        INSERT INTO app_stats (app_id, total_visits, last_visit)
        VALUES (?, 1, ?)
        ON CONFLICT(app_id) DO UPDATE SET
            total_visits = total_visits + 1,
            last_visit = ?
    ''', (app_id, now, now))

    db.commit()


def get_dashboard_stats():
    """获取仪表板统计数据"""
    db = get_db()
    today = datetime.now().date()

    # 今日统计
    today_stats = db.execute('''
        SELECT COALESCE(page_views, 0) as pv, COALESCE(unique_visitors, 0) as uv
        FROM portal_stats WHERE date = ?
    ''', (today,)).fetchone()

    # 总访问量
    total_stats = db.execute('''
        SELECT COALESCE(SUM(page_views), 0) as total_pv, COALESCE(SUM(unique_visitors), 0) as total_uv
        FROM portal_stats
    ''').fetchone()

    # APP访问统计
    app_stats = db.execute('''
        SELECT app_id, total_visits, last_visit
        FROM app_stats
        ORDER BY total_visits DESC
        LIMIT 10
    ''').fetchall()

    # 最近7天趋势
    week_ago = today - timedelta(days=7)
    weekly_trend = db.execute('''
        SELECT date, page_views, unique_visitors
        FROM portal_stats
        WHERE date >= ?
        ORDER BY date
    ''', (week_ago,)).fetchall()

    return {
        'today': {
            'page_views': today_stats['pv'] if today_stats else 0,
            'unique_visitors': today_stats['uv'] if today_stats else 0
        },
        'total': {
            'page_views': total_stats['total_pv'] if total_stats else 0,
            'unique_visitors': total_stats['total_uv'] if total_stats else 0
        },
        'top_apps': [dict(row) for row in app_stats],
        'weekly_trend': [dict(row) for row in weekly_trend]
    }


# ============================================================
# 路由
# ============================================================

@app.route('/')
def index():
    """Portal首页"""
    record_portal_visit()

    # 初始化数据库（如果需要）
    with app.app_context():
        init_db()

    apps_by_category = get_apps_by_category()
    stats = get_dashboard_stats()
    config = load_apps_config()

    return render_template('index.html',
                         apps_by_category=apps_by_category,
                         stats=stats,
                         portal_name=config.get('portal_name', 'Consulting Tools Portal'),
                         portal_description=config.get('portal_description', '咨询事务所内部自动化工具统一入口'))


@app.route('/go/<app_id>')
def go_to_app(app_id):
    """跳转到指定APP并记录统计"""
    config = load_apps_config()
    apps = config.get('apps', [])

    # 查找APP
    target_app = None
    for app_item in apps:
        if app_item['id'] == app_id:
            target_app = app_item
            break

    if not target_app:
        return render_template('error.html', message='APP not found'), 404

    # 记录访问
    record_app_visit(app_id)

    # 跳转到APP
    return redirect(target_app['url'])


@app.route('/api/stats')
def api_stats():
    """获取统计数据API"""
    stats = get_dashboard_stats()
    return jsonify(stats)


@app.route('/api/apps')
def api_apps():
    """获取APP列表API"""
    config = load_apps_config()
    return jsonify(config.get('apps', []))


@app.route('/api/apps/<app_id>/stats')
def api_app_stats(app_id):
    """获取单个APP的统计数据"""
    db = get_db()

    # 基础统计
    stats = db.execute('''
        SELECT app_id, total_visits, last_visit
        FROM app_stats WHERE app_id = ?
    ''', (app_id,)).fetchone()

    if not stats:
        return jsonify({'error': 'No stats found'}), 404

    # 最近访问记录
    recent_visits = db.execute('''
        SELECT timestamp, ip_address
        FROM access_logs
        WHERE app_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
    ''', (app_id,)).fetchall()

    return jsonify({
        'app_id': app_id,
        'total_visits': stats['total_visits'],
        'last_visit': stats['last_visit'],
        'recent_visits': [dict(row) for row in recent_visits]
    })


@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


# ============================================================
# 错误处理
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500


# ============================================================
# 启动
# ============================================================

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)

    # 初始化数据库
    with app.app_context():
        init_db()

    # 启动应用
    app.run(
        host=os.environ.get('PORTAL_HOST', '0.0.0.0'),
        port=int(os.environ.get('PORTAL_PORT', 5000)),
        debug=os.environ.get('PORTAL_DEBUG', 'false').lower() == 'true'
    )
