import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 专项表
    c.execute('''CREATE TABLE IF NOT EXISTS special_project (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        leader TEXT NOT NULL,
        status INTEGER DEFAULT 0,
        requirement_template TEXT,
        prompt_id TEXT,
        image TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')

    # 项目表
    c.execute('''CREATE TABLE IF NOT EXISTS project (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_code TEXT NOT NULL,
        project_manager TEXT NOT NULL,
        special_id TEXT NOT NULL,
        plan_url TEXT,
        requirement_doc TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (special_id) REFERENCES special_project(id)
    )''')

    # Prompt模板表
    c.execute('''CREATE TABLE IF NOT EXISTS prompt_template (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        special_id TEXT UNIQUE,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY (special_id) REFERENCES special_project(id)
    )''')

    conn.commit()
    conn.close()

# 工具函数：执行查询
def query_db(query, params=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchone() if one else c.fetchall()
    conn.close()
    return result

def execute_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

# ========== 专项API ==========

@app.route('/api/specials', methods=['GET'])
def get_specials():
    rows = query_db('SELECT * FROM special_project ORDER BY created_at DESC')
    return jsonify([dict(row) for row in rows])

@app.route('/api/specials', methods=['POST'])
def create_special():
    data = request.json
    id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d')
    execute_db(
        '''INSERT INTO special_project (id, code, name, leader, status, requirement_template, prompt_id, image, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (id, data['code'], data['name'], data['leader'], data.get('status', 0),
         data.get('requirement_template'), data.get('prompt_id'), data.get('image'), now, now)
    )
    return jsonify({'id': id})

@app.route('/api/specials/<special_id>', methods=['PUT'])
def update_special(special_id):
    data = request.json
    now = datetime.now().strftime('%Y-%m-%d')

    # 获取现有数据
    existing = query_db('SELECT * FROM special_project WHERE id=?', (special_id,), one=True)
    if not existing:
        return jsonify({'error': '专项不存在'}), 404

    # 只更新传入的字段
    code = data.get('code', existing['code'])
    name = data.get('name', existing['name'])
    leader = data.get('leader', existing['leader'])
    status = data.get('status', existing['status'])
    requirement_template = data.get('requirement_template', existing['requirement_template'])
    prompt_id = data.get('prompt_id', existing['prompt_id'])
    image = data.get('image', existing['image'])

    execute_db(
        '''UPDATE special_project SET code=?, name=?, leader=?, status=?, requirement_template=?, prompt_id=?, image=?, updated_at=?
           WHERE id=?''',
        (code, name, leader, status, requirement_template, prompt_id, image, now, special_id)
    )
    return jsonify({'success': True})

@app.route('/api/specials/<special_id>', methods=['DELETE'])
def delete_special(special_id):
    execute_db('DELETE FROM special_project WHERE id=?', (special_id,))
    return jsonify({'success': True})

# ========== 项目API ==========

@app.route('/api/projects', methods=['GET'])
def get_projects():
    rows = query_db('SELECT * FROM project ORDER BY created_at DESC')
    return jsonify([dict(row) for row in rows])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d')
    execute_db(
        '''INSERT INTO project (id, name, code, customer_name, customer_code, project_manager, special_id, plan_url, requirement_doc, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (id, data['name'], data['code'], data['customer_name'], data['customer_code'],
         data['project_manager'], data['special_id'], data.get('plan_url'), data.get('requirement_doc'), now, now)
    )
    return jsonify({'id': id})

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json
    now = datetime.now().strftime('%Y-%m-%d')
    execute_db(
        '''UPDATE project SET name=?, code=?, customer_name=?, customer_code=?, project_manager=?, special_id=?, plan_url=?, requirement_doc=?, updated_at=?
           WHERE id=?''',
        (data['name'], data['code'], data['customer_name'], data['customer_code'],
         data['project_manager'], data['special_id'], data.get('plan_url'), data.get('requirement_doc'), now, project_id)
    )
    return jsonify({'success': True})

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    execute_db('DELETE FROM project WHERE id=?', (project_id,))
    return jsonify({'success': True})

# ========== Prompt模板API ==========

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    rows = query_db('SELECT * FROM prompt_template ORDER BY created_at DESC')
    return jsonify([dict(row) for row in rows])

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    data = request.json
    id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d')
    execute_db(
        '''INSERT INTO prompt_template (id, name, special_id, content, created_at)
           VALUES (?, ?, ?, ?, ?)''',
        (id, data['name'], data.get('special_id'), data.get('content'), now)
    )
    return jsonify({'id': id})

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    data = request.json
    execute_db(
        '''UPDATE prompt_template SET name=?, special_id=?, content=? WHERE id=?''',
        (data['name'], data.get('special_id'), data.get('content'), prompt_id)
    )
    return jsonify({'success': True})

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    execute_db('DELETE FROM prompt_template WHERE id=?', (prompt_id,))
    return jsonify({'success': True})

# ========== 文件上传 ==========

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file'}), 400

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 返回可访问的URL
    file_url = f"/uploads/{filename}"
    return jsonify({'url': file_url, 'filename': file.filename})

@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 下载需求模板
@app.route('/api/specials/<special_id>/template')
def download_template(special_id):
    sp = query_db('SELECT requirement_template FROM special_project WHERE id=?', (special_id,), one=True)
    if not sp or not sp['requirement_template']:
        return jsonify({'error': '模板不存在'}), 404

    filename = sp['requirement_template']
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404

# 前端页面入口
@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

# ========== 数据库管理页面 ==========

@app.route('/admin/db')
def admin_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取所有表
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]

    html = "<html><head><meta charset='utf-8'><title>数据库管理</title>"
    html += "<style>body{font-family:Arial,sans-serif;padding:20px} "
    html += "table{border-collapse:collapse;width:100%;margin:20px 0} "
    html += "th,td{border:1px solid #ddd;padding:8px;text-align:left} "
    html += "th{background:#f5f5f5} h2{margin-top:30px}</style></head><body>"
    html += "<h1>专项管理系统 - 数据库管理</h1>"

    for table in tables:
        html += f"<h2>{table}</h2><table><thead><tr>"
        # 表头
        c.execute(f"PRAGMA table_info({table})")
        columns = c.fetchall()
        for col in columns:
            html += f"<th>{col[1]}</th>"
        html += "</tr></thead><tbody>"

        # 数据
        c.execute(f"SELECT * FROM {table}")
        for row in c.fetchall():
            html += "<tr>"
            for val in row:
                html += f"<td>{val or ''}</td>"
            html += "</tr>"
        html += "</tbody></table>"

    conn.close()
    html += "</body></html>"
    return html

if __name__ == '__main__':
    init_db()
    print("服务器启动: http://localhost:5001")
    print("数据库管理: http://localhost:5001/admin/db")
    app.run(debug=True, port=5001)