[app]

title = 金小约
package.name = myrobot0327
package.domain = com.github.shiewikou
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,txt

fullscreen = 0
orientation = portrait

requirements = python3,kivy==2.2.1,android


# ⬇️ NDK 必须认怂，锁死在 25b 保证能编译成功 ⬇️
android.ndk = 25b

# ⬇️ API/SDK 紧跟 2026 年要求，提升到 35 ⬇️
android.sdk = 34
android.api = 34
android.targetsdk = 34
# 考虑到向下兼容，最低支持到 Android 5.0 (API 21) 或 7.0 (API 24)
android.minapi = 21

android.build_tools = 34.0.0
android.accept_sdk_license = True


android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

log_level = 2
