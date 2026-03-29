#!/usr/bin/env python3
"""初始化测试数据"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = 'database.db'
UPLOAD_PATH = '../uploads'

def init_test_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now().strftime('%Y-%m-%d')

    # 专项数据
    specials = [
        (str(uuid.uuid4()), 'SP-2026-001', '混合云专项', '张明', 0, '混合云需求模板.xlsx', None, 'https://picsum.photos/200/200?random=1', now, now),
        (str(uuid.uuid4()), 'SP-2026-002', '邮箱迁移专项', '李华', 1, '邮箱迁移需求模板.xlsx', None, 'https://picsum.photos/200/200?random=2', now, now),
        (str(uuid.uuid4()), 'SP-2026-003', '微软替换专项', '王强', 1, None, None, 'https://picsum.photos/200/200?random=3', now, now),
        (str(uuid.uuid4()), 'SP-2026-004', '国际化专项', '赵敏', 2, None, None, 'https://picsum.photos/200/200?random=4', now, now),
    ]

    for s in specials:
        c.execute('''INSERT INTO special_project (id, code, name, leader, status, requirement_template, prompt_id, image, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', s)

    # Prompt模板数据
    prompts = [
        (str(uuid.uuid4()), '混合云专项Prompt', specials[0][0], '请根据以下专项建设方案和项目需求，生成专业的专项建设方案。\n\n专项建设方案：${specialPlan}\n项目需求：${requirement}', now),
        (str(uuid.uuid4()), '邮箱迁移专项Prompt', specials[1][0], '请根据邮箱迁移专项的建设方案和项目需求，生成详细的迁移方案。\n\n建设方案：${specialPlan}\n需求：${requirement}', now),
    ]

    for p in prompts:
        c.execute('''INSERT INTO prompt_template (id, name, special_id, content, created_at)
                   VALUES (?, ?, ?, ?, ?)''', p)

    # 更新专项的prompt_id
    c.execute('UPDATE special_project SET prompt_id = ? WHERE code = ?', (prompts[0][0], 'SP-2026-001'))
    c.execute('UPDATE special_project SET prompt_id = ? WHERE code = ?', (prompts[1][0], 'SP-2026-002'))

    # 项目数据
    projects = [
        (str(uuid.uuid4()), 'A省混合云平台项目', 'PRJ-2026-001', 'A省政务云', 'CUS-001', '张三', specials[0][0], '混合云建设方案.docx', 'A省混合云需求文档.xlsx', now, now),
        (str(uuid.uuid4()), 'B市邮箱迁移项目', 'PRJ-2026-002', 'B市人民政府', 'CUS-002', '李四', specials[1][0], '邮箱迁移方案.docx', 'B市邮箱需求文档.xlsx', now, now),
        (str(uuid.uuid4()), 'C企业微软替换项目', 'PRJ-2026-003', 'C科技有限公司', 'CUS-003', '王五', specials[2][0], '替换方案.docx', None, now, now),
    ]

    for p in projects:
        c.execute('''INSERT INTO project (id, name, code, customer_name, customer_code, project_manager, special_id, plan_url, requirement_doc, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', p)

    conn.commit()
    conn.close()
    print("测试数据初始化完成！")

if __name__ == '__main__':
    init_test_data()