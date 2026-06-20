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

android.ndk = 23c
android.sdk = 30
android.api = 30
android.minapi = 21
android.targetsdk = 30

android.build_tools = 30.0.3
android.accept_sdk_license = True

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

log_level = 2
