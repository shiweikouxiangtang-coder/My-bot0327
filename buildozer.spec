[app]

# 应用标题
title = 我的机器人0327

# 包名（建议改为您自己的域名，如 com.github.你的用户名）
package.name = myrobot0327
package.domain = com.github.shiweikouxiangtang

# 版本信息
android.api = 30
android.minapi = 21
android.targetsdk = 30
android.version = 1.0.0

# ---------- 图标与启动画面（已启用） ----------
icon.filename = icon.png
presplash.filename = presplash.png

# 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

# 包含的文件类型
source.include_exts = py,png,jpg,kv,atlas

# 包含的 Python 文件
source.include_patterns = main.py, bot.py

# 排除项
source.exclude_patterns = __pycache__, *.pyc

# Python 依赖
requirements = python3,kivy

# Android 选项
android.accelerometer = False
android.gps = False
android.orientation = portrait
android.fullscreen = false
android.allow_backup = true
android.use_androidx = true
android.arch = armeabi-v7a, arm64-v8a

# 构建日志级别
log_level = info

# 签名（调试版本无需修改）
android.release = false
android.compress = true
