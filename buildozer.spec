[app]

# 应用名称（显示在手机桌面）
title = 我的机器人

# 应用包名（唯一标识）
package.name = myrobot0327
package.domain = com.github.shiewikou

# 应用版本号（必须设置，解决你之前的报错）
version = 1.0.0

# 源代码目录（你的 main.py 在根目录，所以用 .）
source.dir = .

# 打包时包含的文件类型（保证你的 .txt 数据文件也被打包进去）
source.include_exts = py,png,jpg,jpeg,gif,ttf,txt

# 是否全屏（0为不全屏）
fullscreen = 0

# 屏幕方向（竖屏）
orientation = portrait

# 依赖库（核心是 kivy）
requirements = python3,kivy

# Android SDK 版本配置
android.api = 30
android.minapi = 21
android.targetsdk = 30

# 安卓权限（你的程序需要读写文件）
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 如果以后你有 icon.png 图标文件，取消下面这行的注释
# icon.filename = %(source.dir)s/icon.png
