import random
import os
import datetime
import re
import collections

# --- Kivy 相关库导入 ---
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

# 设置背景为类似微信的浅灰色
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# --- 1. 配置路径 (适配安卓环境) ---
# 注意：在手机上，一般保存在应用的 user_data_dir，这样免去复杂的权限申请
BASE_DIR = "" 

FILE_QA = "qa.txt"
FILE_JOKES = "jokes.txt"
FILE_MATH = "math.txt"
FILE_TASKS = "tasks.txt"
FILE_KMOJ = "kaomoji.txt"

# --- 2. 状态机与上下文管理 ---
context = {"state": "IDLE", "math_answer": None, "task_to_del": None}
history_stack = collections.deque(maxlen=10)
memory = {"qa": {}, "jokes": [], "math": [], "tasks": [], "kmoj": {}}

# --- 3. 完整数据加载系统 ---
def load_all_data():
    memory["qa"] = {}
    memory["jokes"] = []
    memory["math"] = []
    memory["tasks"] = []
    memory["kmoj"] = {}

    if os.path.exists(FILE_QA):
        with open(FILE_QA, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    kw, ans = line.strip().split('|', 1)
                    memory["qa"].setdefault(kw, [])
                    if ans not in memory["qa"][kw]:
                        memory["qa"][kw].append(ans)
    
    if os.path.exists(FILE_KMOJ):
        with open(FILE_KMOJ, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    keywords = parts[0].split(',')
                    kaomojis = parts[1:]
                    for kw in keywords:
                        memory["kmoj"][kw.strip()] = kaomojis

    if os.path.exists(FILE_JOKES):
        with open(FILE_JOKES, "r", encoding="utf-8") as f:
            memory["jokes"] = [line.strip() for line in f if line.strip()]

    if os.path.exists(FILE_MATH):
        with open(FILE_MATH, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    memory["math"].append((parts[0], parts[1]))

    if os.path.exists(FILE_TASKS):
        with open(FILE_TASKS, "r", encoding="utf-8") as f:
            memory["tasks"] = [line.strip().split('|') for line in f if '|' in line]

def get_mood_emoji(u):
    for kw in memory["kmoj"].keys():
        if kw and kw != "默认" and kw in u:
            return random.choice(memory["kmoj"][kw])
    return random.choice(memory["kmoj"].get("默认", ["(●'◡'●)"]))

def parse_relative_date(date_str):
    today = datetime.datetime.now()
    if not date_str: return today.strftime("%Y-%m-%d")
    if "今天" in date_str: return today.strftime("%Y-%m-%d")
    if "明天" in date_str: return (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if "下周" in date_str: return (today + datetime.timedelta(weeks=1)).strftime("%Y-%m-%d")
    return date_str

# --- 单次对话处理逻辑 (替代原来的 while True) ---
def process_message(u):
    global context, history_stack, memory
    if not u: return None
    history_stack.append(u)
    
    # [A] 状态机：删除任务确认
    if context["state"] == "DELETE_TASK":
        if "是" in u:
            memory["tasks"] = [t for t in memory["tasks"] if t[1] != context["task_to_del"]]
            with open(FILE_TASKS, "w", encoding="utf-8") as f:
                for t in memory["tasks"]: f.write(f"{t[0]}|{t[1]}\n")
            context["state"] = "IDLE"
            return f"任务已从清单中自动删除。 {get_mood_emoji(u)}"
        else:
            context["state"] = "IDLE"
            return f"好的，保留该任务。 {get_mood_emoji(u)}"

    # [B] 状态机：数学答题验证
    if context["state"] == "MATH":
        context["state"] = "IDLE"
        if u == context["math_answer"]: 
            return f"正确！答对了。 {get_mood_emoji(u)}"
        else: 
            return f"错了，正确答案是 {context['math_answer']}。 {get_mood_emoji(u)}"

    # [C] 查询最近10轮上下文
    if u == "查一下历史" or u == "查一下上下文":
        res = "最近10轮的对话历史记录如下：\n"
        for index, hist in enumerate(history_stack):
            res += f"  {index + 1}. {hist}\n"
        return res

    # [D] 知识库持久化主动学习
    if u.startswith("回答|") and "|" in u:
        parts = u.split("|", 2)
        if len(parts) == 3:
            kw, ans = parts[1], parts[2]
            if ans not in memory["qa"].get(kw, []):
                memory["qa"].setdefault(kw, []).append(ans)
                with open(FILE_QA, "a", encoding="utf-8") as f: 
                    f.write(f"\n{kw}|{ans}")
                return f"学到了！已记住新回答：{kw} -> {ans} {get_mood_emoji(u)}"
            else:
                return f"知识库里已经有这个回答了，不需要重复学习。 {get_mood_emoji(u)}"

    # [E] 完成任务提醒触发 (我做完了)
    if "我做完了" in u:
        if memory["tasks"]:
            context["state"] = "DELETE_TASK"
            context["task_to_del"] = memory["tasks"][-1][1]
            return f"你完成任务了吗？是指 '{context['task_to_del']}' 吗？完成之后会自动删掉。 {get_mood_emoji(u)}"
        else:
            return f"你的任务清单现在是空的。 {get_mood_emoji(u)}"

    # [F] 插件：天气查询
    weather_m = re.search(r'(.*)天气', u)
    if weather_m:
        city = weather_m.group(1).strip() or "本地"
        return f"查询到{city}今日天气：晴朗，25℃，空气质量优。 {get_mood_emoji(u)}"

    # [G] 插件：任务录入 (升级版)
    if "记得" in u or "提醒" in u:
        date_keyword = None
        for d in ["今天", "明天", "下周"]:
            if d in u:
                date_keyword = d
                break
        
        content = re.sub(r'.*(记得|提醒)', '', u).replace(str(date_keyword), '').strip()
        if content:
            date_val = parse_relative_date(date_keyword)
            with open(FILE_TASKS, "a", encoding="utf-8") as f: f.write(f"{date_val}|{content}\n")
            memory["tasks"].append([date_val, content])
            return f"没问题，记下了：{date_val} 提醒您 {content}。 {get_mood_emoji(u)}"

    # [H] 笑话与数学题随机触发
    if "笑话" in u:
        if memory["jokes"]:
            return f"给你讲个笑话：{random.choice(memory['jokes'])} {get_mood_emoji(u)}"
        else:
            return f"笑话库空空如也。 {get_mood_emoji(u)}"
        
    if "数学" in u:
        if memory["math"]:
            q, a = random.choice(memory["math"])
            context["state"] = "MATH"
            context["math_answer"] = a
            return f"请听题：{q} 等于多少？ {get_mood_emoji(u)}"
        else:
            return f"没找到数学题库文件。 {get_mood_emoji(u)}"

    # [I] 知识库检索引擎
    matched = False
    for kw, answers in memory["qa"].items():
        if re.search(re.escape(kw), u):
            return f"{random.choice(answers)} {get_mood_emoji(u)}"
    
    # [J] 历史上下文意图补全逻辑
    if len(history_stack) > 1:
        combined = history_stack[-2] + u
        for kw, answers in memory["qa"].items():
            if re.search(re.escape(kw), combined):
                return f"(结合上文联想) {random.choice(answers)} {get_mood_emoji(u)}"

    # [K] 兜底未匹配回复
    return f"抱歉，我还不懂这个呢。你可以用 '回答|关键词|内容' 的格式教教我。 {get_mood_emoji(u)}"


# --- 自定义聊天气泡组件 ---
class ChatBubble(BoxLayout):
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        # 留白处理，让气泡不占满整行
        self.padding = [dp(10), dp(5), dp(10), dp(5)]
        
        # 消息文本标签
        self.msg_label = Label(
            text=text,
            color=(0, 0, 0, 1),
            size_hint_x=None,
            size_hint_y=None,
            halign='left',
            valign='middle',
            font_name='Roboto' # 若在中文环境下，这里后续可改为中文字体路径
        )
        # 动态绑定高度和宽度
        self.msg_label.bind(texture_size=self.update_bubble_size)
        self.msg_label.text_size = (Window.width * 0.65, None)

        # 气泡背景绘制
        with self.canvas.before:
            # 微信风格：用户是绿色，AI是白色
            if is_user:
                Color(0.58, 0.92, 0.41, 1) # #95EC69
            else:
                Color(1, 1, 1, 1) # #FFFFFF
            self.rect = RoundedRectangle(radius=[dp(10)])
            
        self.bind(pos=self.update_rect, size=self.update_rect)

        # 左右对齐逻辑
        spacer = Label(size_hint_x=1) # 弹簧垫片
        if is_user:
            self.add_widget(spacer)
            self.add_widget(self.msg_label)
        else:
            self.add_widget(self.msg_label)
            self.add_widget(spacer)
            
    def update_bubble_size(self, instance, size):
        self.msg_label.size = size
        # 设置整个水平布局的高度，气泡加上下边距
        self.height = size[1] + dp(20)
        
    def update_rect(self, instance, value):
        # 让彩色背景只包裹 msg_label
        self.rect.pos = (self.msg_label.x - dp(10), self.msg_label.y - dp(10))
        self.rect.size = (self.msg_label.width + dp(20), self.msg_label.height + dp(20))


# --- 主界面 UI ---
class WeChatApp(App):
    def build(self):
        # 确保初始化时获取正确路径 (适配安卓)
        global BASE_DIR, FILE_QA, FILE_JOKES, FILE_MATH, FILE_TASKS, FILE_KMOJ
        BASE_DIR = self.user_data_dir
        FILE_QA = os.path.join(BASE_DIR, "qa.txt")
        FILE_JOKES = os.path.join(BASE_DIR, "jokes.txt")
        FILE_MATH = os.path.join(BASE_DIR, "math.txt")
        FILE_TASKS = os.path.join(BASE_DIR, "tasks.txt")
        FILE_KMOJ = os.path.join(BASE_DIR, "kaomoji.txt")
        
        load_all_data()

        # 根布局
        root = BoxLayout(orientation='vertical')
        
        # 顶部标题栏 (深灰色)
        header = BoxLayout(size_hint_y=None, height=dp(50))
        with header.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.header_rect = RoundedRectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header, pos=self._update_header)
        
        title = Label(text="智能管家", color=(0.1, 0.1, 0.1, 1), bold=True)
        header.add_widget(title)
        root.add_widget(header)

        # 聊天滚动区
        self.scroll = ScrollView(size_hint=(1, 1))
        self.chat_history = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=dp(10))
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        self.scroll.add_widget(self.chat_history)
        root.add_widget(self.scroll)

        # 底部输入区
        bottom_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), padding=dp(8), spacing=dp(8))
        with bottom_bar.canvas.before:
            Color(0.96, 0.96, 0.96, 1)
            self.bottom_rect = RoundedRectangle(size=bottom_bar.size, pos=bottom_bar.pos)
        bottom_bar.bind(size=self._update_bottom, pos=self._update_bottom)
        
        self.input_box = TextInput(
            multiline=False, 
            size_hint_x=0.8,
            font_name='Roboto',
            background_color=(1, 1, 1, 1),
            padding=[dp(10), dp(10)]
        )
        self.input_box.bind(on_text_validate=self.send_message) # 支持回车发送
        bottom_bar.add_widget(self.input_box)

        send_btn = Button(
            text="发送",
            size_hint_x=0.2,
            background_color=(0.58, 0.92, 0.41, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        send_btn.bind(on_press=self.send_message)
        bottom_bar.add_widget(send_btn)

        root.add_widget(bottom_bar)

        # 启动时的今日提醒与问候
        Clock.schedule_once(self.startup_greeting, 0.5)

        return root
        
    def _update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
        
    def _update_bottom(self, instance, value):
        self.bottom_rect.pos = instance.pos
        self.bottom_rect.size = instance.size

    def startup_greeting(self, dt):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        count = 0
        reminders = ""
        for task_item in memory["tasks"]:
            if task_item[0] == today:
                reminders += f"\n• {task_item[1]}"
                count += 1
        
        greet_msg = "你好，我是智能管家！(●'◡'●)"
        if count > 0:
            greet_msg += f"\n\n今日任务提醒：{reminders}"
        else:
            greet_msg += "\n\n今天没有待办任务，好好休息吧！"
            
        self.add_bubble(greet_msg, is_user=False)

    def send_message(self, instance):
        user_text = self.input_box.text.strip()
        if not user_text:
            return
            
        # 1. 界面上添加用户发言（绿色气泡）
        self.add_bubble(user_text, is_user=True)
        self.input_box.text = ""
        
        # 2. 调用核心逻辑处理回复
        ai_reply = process_message(user_text)
        
        # 3. 界面上添加AI回复（白色气泡），延迟一点显得更真实
        if ai_reply:
            Clock.schedule_once(lambda dt: self.add_bubble(ai_reply, is_user=False), 0.2)

    def add_bubble(self, text, is_user):
        bubble = ChatBubble(text=text, is_user=is_user)
        self.chat_history.add_widget(bubble)
        # 自动滚动到底部
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

if __name__ == '__main__':
    WeChatApp().run()
