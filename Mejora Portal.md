你是资深全栈工程师 + DevOps。我要你在现有 Portal 仓库中实现“登录/注册 + 角色/部门 + RBAC 权限控制”，并保持现有 Nginx 反向代理与 /go/<app_id> 跳转统计能力不被破坏。

【仓库背景（请先自行扫描确认）】
- 仓库目录类似：
  Portal/
    portal/
      app.py
      apps_config.json
      templates/
      static/
      requirements.txt
    scripts/
      deploy.sh
      restart-all.sh
      check-status.sh
- Nginx 当前把：
  /      -> 可能是 /home/ubuntu/Portal/static/index.html（静态）
  /app/  -> 127.0.0.1:8501 (Streamlit)
  /api/  -> 127.0.0.1:8000 (FastAPI)
  /health -> 返回 "Portal OK"
目标是：让 / 变成需要登录的 Portal Flask 页面（dashboard），并提供注册/登录/登出/管理员管理。

【业务需求】
1) Portal 增加登录界面（Login）。
2) Portal 增加注册界面（Register）。
   - 注册时，用户名使用“公司账号”（作为 username 字段存储；不强制邮箱格式，除非你发现项目已有约束）。
   - 注册需要设置：
     a) password
     b) 职位 role: junior | senior | manager | socio
     c) 部门 department（下拉）：
        - auditoria
        - precio de transferencia
        - tax
        - legal
        - administracion y finanza
        - IT
        - Quality & Risk Management
        - AOS
        - otros (a especificar) -> 若选 otros，额外输入 “otros_detalle”
3) 部门会影响用户在 Portal 中可见/可用的 apps（RBAC）。
4) Portal 有一个管理员账户：
   - username: Admin
   - password: Admin123
   管理员可以：
   - 查看/搜索用户
   - 修改用户 role / department / 是否启用
   - 重置用户密码（生成临时密码或手动设置）
5) 所有密码必须安全存储（hash+salt），严禁明文；Session/CSRF 要到位。
6) 保持 /go/<app_id> 的跳转统计能力（若当前已有），并在跳转前做权限校验：无权限则拒绝并提示。
7) 保持 apps_config.json 作为配置中心；在其中新增“访问控制字段”，对旧数据保持向后兼容（旧 app 没配置访问控制 -> 默认所有登录用户可见）。

【实现约束与建议】
- 技术栈优先：Flask + flask-login + werkzeug.security(或 bcrypt)；数据库使用 SQLite（文件放在 portal/data/ 下，例如 portal/data/users.db）。
- SECRET_KEY、数据库路径等写入环境变量（例如 .env 或 systemd Environment=），并提供合理默认。
- 需要一个“首次启动初始化”逻辑：若数据库不存在则自动创建表并写入 Admin 用户（Admin/Admin123 -> 写入 hash）。
- UI：尽量复用现有 templates/style（若已有），新增 login.html、register.html、admin.html、dashboard.html；界面语言用西班牙语（Portal 原本也是西语/中英混合，优先西语）。
- apps_config.json 新增字段建议（你可以按项目风格调整命名，但要写清楚并更新文档）：
  对每个 app 增加：
    "access": {
      "departments": ["auditoria", "tax", ...],   // 缺省或空 -> ALL
      "roles": ["junior","senior","manager","socio"] // 缺省或空 -> ALL
    }
  注意：department 的内部 id 需要统一；对带空格/特殊字符的显示名做映射（例如 "precio de transferencia" -> "precio_transferencia" 或保留原样但必须一致）。
  你需要选择一种一致的“内部 id 规范”，并在代码中集中定义映射表：
    - 显示名（UI） <-> 内部 id（存库/权限判断）
- 权限判断逻辑：
  用户可见 app 当且仅当：
    (app.access.departments 未定义或包含用户 department) AND
    (app.access.roles 未定义或包含用户 role)
- 路由保护：
  /login, /register 公开
  /logout 需登录
  / (dashboard) 需登录
  /go/<app_id> 需登录 + 权限校验
  /admin/* 仅 Admin 账户可用（或 role=admin；但需求指定用户名 Admin，就以此为准）
- Nginx 改造：
  把 / 代理到 portal 后端（例如 127.0.0.1:5000），并把 portal 静态资源通过 /static/ 提供（或由 Flask 提供）。
  保留 /app/、/api/、/health 的既有配置不变。
- systemd：
  新增 portal.service（gunicorn 启动 Flask app），并把 restart-all.sh/check-status.sh/deploy.sh 更新以包含 portal 服务。

【交付物（你必须输出）】
A) 完整代码改动（按仓库结构提交）：
   - portal/app.py（或拆分成 blueprint：auth/admin/dashboard）
   - portal/models.py（若你拆分）
   - portal/templates/*.html
   - portal/static/*（如需）
   - portal/requirements.txt 更新
   - scripts/ 与 systemd service 文件更新
B) apps_config.json schema 更新 + 示例（至少给出 2 个 app 的 access 示例）。
C) 文档更新：
   - README.md 增加：如何创建用户、Admin 登录、如何配置 app 权限字段、如何部署/升级。
   - GUIA_CONFIGURACION.md 增加：access 字段说明。
D) 最小测试与验证步骤：
   - 本地运行方式（flask/gunicorn）
   - curl 验证 /health
   - 1) 注册普通用户 2) 登录 3) 仅能看到本部门 apps 4) 无权限 /go/<app_id> 被拒绝 5) Admin 能修改用户权限

【开发步骤（请按此执行并在输出中逐项对照）】
1) 先扫描仓库并回答：当前 Portal 是静态首页还是 Flask 已在跑？/go/<app_id> 是否已实现？portal/app.py 现有路由有哪些？
2) 设计数据模型（SQLite）并实现迁移/初始化（首次启动自动创建 + 写 Admin）。
3) 实现认证模块（register/login/logout），密码 hash，session，CSRF。
4) 实现 RBAC：读取 apps_config.json -> 过滤 apps -> dashboard 渲染；/go/<app_id> 权限校验。
5) 实现 Admin 面板（用户列表、编辑 role/department/enabled、重置密码）。
6) Nginx + systemd + scripts：把 / 指向 portal；新增 portal.service；更新 deploy/restart/check-status 脚本。
7) 更新文档与提供验证步骤。

【重要：不确定点处理】
如果你发现以下任一项与仓库现状冲突，请先在输出里列出“冲突点与建议方案”，再给出你选择的默认方案并继续实现：
- 已存在用户体系/SSO
- portal 已有数据库或持久化方式（json/yaml）
- Nginx 已被其他服务占用 /
- 目录结构与文档不一致

现在开始执行。输出请包含：你发现的现状 -> 设计决策 -> 关键代码文件变更摘要 -> 部署/验证步骤。