[app]

title = xiaoybot
package.name = myrobot0327
package.domain = com.github.shiewikou
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,txt

fullscreen = 0
orientation = portrait

requirements = python3,kivy==2.3.0,android

# Android SDK/NDK 版本锁定
android.ndk = 23c
android.sdk = 33
android.api = 30
android.minapi = 21
android.targetsdk = 30

# 关键修复：指定稳定 build-tools 并自动接受许可证
android.build_tools = 30.0.3
android.accept_sdk_license = True

# ✅已按你的要求加上读取和写入权限（同时保留网络权限）
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# icon.filename = %(source.dir)s/icon.png
