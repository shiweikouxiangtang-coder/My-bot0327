[app]

title = 金小约
package.name = myrobot0327
package.domain = com.github.shiewikou
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,txt

fullscreen = 0
orientation = portrait

# 固定 Python 版本以避免 p4a 构建较新 hostpython 导致的 autoreconf 问题
requirements = python3==3.10.20,kivy==2.2.1,android

# NDK and SDK versions - locked for stability
android.ndk = 25b
android.sdk = 34
android.api = 34
android.targetsdk = 34
android.minapi = 21
android.build_tools = 34.0.0
android.accept_sdk_license = True

# Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Logging (1=minimal, 2=verbose)
log_level = 2

[buildozer]
# Use setup.py for better dependency resolution
p4a.extra_args = --use-setup-py
# Enable logging to help debug build issues
log_level = 2
