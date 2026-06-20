import random
import os
import datetime
import re
import collections

# --- 1. 配置路径 (6个核心文件，新增profile用户档案) ---
BASE_DIR = "/sdcard/Documents"
FILE_QA = os.path.join(BASE_DIR, "qa.txt")
FILE_JOKES = os.path.join(BASE_DIR, "jokes.txt")
FILE_MATH = os.path.join(BASE_DIR, "math.txt")
FILE_TASKS = os.path.join(BASE_DIR, "tasks.txt")
FILE_KMOJ = os.path.join(BASE_DIR, "kaomoji.txt")
FILE_PROFILE = os.path.join(BASE_DIR, "profile.txt") # [新增] 用户档案存储文件

# --- 2. 状态机与上下文管理 ---
context = {"state": "IDLE", "math_answer": None, "task_to_del": None}
history_stack = collections.deque(maxlen=10)
# [新增] profile 内存区，用于存储列表数据
memory = {"qa": {}, "jokes": [], "math": [], "tasks": [], "kmoj": {}, "profile": {}}

# --- 3. 完整数据加载系统 (全部通过文本持久化) ---
def load_all_data():
    memory["qa"] = {}
    memory["jokes"] = []
    memory["math"] = []
    memory["tasks"] = []
    memory["kmoj"] = {}
    memory["profile"] = {}

    # [1] 加载问答库 (支持同义词组)
    if os.path.exists(FILE_QA):
        with open(FILE_QA, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    kw_part, ans = line.strip().split('|', 1)
                    keywords = kw_part.split(',') 
                    for kw in keywords:
                        kw = kw.strip()
                        if not kw: continue
                        memory["qa"].setdefault(kw, [])
                        if ans not in memory["qa"][kw]:
                            memory["qa"][kw].append(ans)
    
    # [2] 加载颜文字库
    if os.path.exists(FILE_KMOJ):
        with open(FILE_KMOJ, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    memory["kmoj"][parts[0]] = parts[1:]

    # [3] 加载笑话库
    if os.path.exists(FILE_JOKES):
        with open(FILE_JOKES, "r", encoding="utf-8") as f:
            memory["jokes"] = [line.strip() for line in f if line.strip()]

    # [4] 加载数学题库
    if os.path.exists(FILE_MATH):
        with open(FILE_MATH, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    memory["math"].append((parts[0], parts[1]))

    # [5] 加载任务清单
    if os.path.exists(FILE_TASKS):
        with open(FILE_TASKS, "r", encoding="utf-8") as f:
            memory["tasks"] = [line.strip().split('|') for line in f if '|' in line]

    # [6] 加载用户档案库 (例如格式: 讨厌|张三 或 爱好|吃苹果)
    if os.path.exists(FILE_PROFILE):
        with open(FILE_PROFILE, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    key, val = line.strip().split('|', 1)
                    memory["profile"].setdefault(key, [])
                    if val not in memory["profile"][key]:
                        memory["profile"][key].append(val)

# --- 4. 辅助工具区 (新增词性替换与手机API接口) ---
def get_mood_emoji(u):
    if "开心" in u or "哈哈" in u: return random.choice(memory["kmoj"].get("开心", ["(＾▽＾)"]))
    if "难过" in u or "哭" in u: return random.choice(memory["kmoj"].get("难过", ["(╥﹏╥)"]))
    return random.choice(memory["kmoj"].get("默认", ["(●'◡'●)"]))

def parse_relative_date(date_str):
    today = datetime.datetime.now()
    if not date_str: return today.strftime("%Y-%m-%d")
    if "今天" in date_str: return today.strftime("%Y-%m-%d")
    if "明天" in date_str: return (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if "下周" in date_str: return (today + datetime.timedelta(weeks=1)).strftime("%Y-%m-%d")
    return date_str

def check_tasks_today():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    count = 0
    for task_item in memory["tasks"]:
        if task_item[0] == today:
            print(f"[AI]: 今日任务提醒：{task_item[1]}")
            count += 1
    if count == 0:
        print("[AI]: 今天没有待办任务，好好休息吧！")

# [新增功能] 常规词性动态替换 (打乱副词/形容词)
def apply_synonyms(text):
    # 本地小型同义词典
    synonyms_dict = {
        "开心": ["高兴", "快乐", "愉悦", "欢喜"],
        "漂亮": ["美丽", "好看", "迷人", "精致"],
        "非常": ["特别", "极其", "十分", "分外"],
        "难过": ["伤心", "悲痛", "心痛", "失落"],
        "不错": ["挺好", "可以", "很赞", "优秀"],
        "喜欢": ["钟意", "青睐", "偏爱", "看好"]
    }
    for word, replacements in synonyms_dict.items():
        if word in text and random.random() < 0.4: # 40% 的概率触发词汇替换，避免每次都换显得生硬
            text = text.replace(word, random.choice(replacements), 1)
    return text

# [预留接口] 手机自带软件天气 API 触发点
def fetch_local_weather(city):
    # 这里是接入你手机软件 API 的地方。
    # 如果你是用 Termux，可以使用 os.popen('termux-location') 或者其他软件的 Intent。
    # 待你写入具体 API 代码后，直接 return 你的真实天气字符串即可。
    return f"{city}今日天气：多云转晴，26℃。(注：请在此函数内替换为你的本地API代码)"

# --- 5. 主循环程序 ---
def chat():
    load_all_data()
    print("--- 智能管家 [极智扩容版] ---")
    check_tasks_today()
    
    while True:
        try:
            u = input("\n[我]: ").strip()
            if u == "退出": break
            if not u: continue
            history_stack.append(u)
            
            # [A] 状态机：删除任务确认
            if context["state"] == "DELETE_TASK":
                if "是" in u:
                    memory["tasks"] = [t for t in memory["tasks"] if t[1] != context["task_to_del"]]
                    with open(FILE_TASKS, "w", encoding="utf-8") as f:
                        for t in memory["tasks"]: f.write(f"{t[0]}|{t[1]}\n")
                    print(f"[AI]: {apply_synonyms('任务已从清单中自动删除。非常不错！')} {get_mood_emoji(u)}")
                else:
                    print(f"[AI]: {apply_synonyms('好的，保留该任务。')} {get_mood_emoji(u)}")
                context["state"] = "IDLE"
                continue

            # [B] 状态机：数学答题验证
            if context["state"] == "MATH":
                if u == context["math_answer"]: 
                    print(f"[AI]: {apply_synonyms('正确！答对了，非常棒！')} {get_mood_emoji(u)}")
                else: 
                    print(f"[AI]: 错了，正确答案是 {context['math_answer']}。 {get_mood_emoji(u)}")
                context["state"] = "IDLE"
                continue

            # [C] 查询最近10轮上下文
            if u in ["查一下历史", "查一下上下文"]:
                print(f"[AI]: 最近10轮的对话历史记录如下：")
                for index, hist in enumerate(history_stack):
                    print(f"  {index + 1}. {hist}")
                continue

            # [D] 知识库持久化主动学习
            if u.startswith("回答|") and "|" in u:
                parts = u.split("|", 2)
                if len(parts) == 3:
                    kw_part, ans = parts[1], parts[2]
                    keywords = kw_part.split(',')
                    learned = False
                    for kw in keywords:
                        kw = kw.strip()
                        if not kw: continue
                        if ans not in memory["qa"].get(kw, []):
                            memory["qa"].setdefault(kw, []).append(ans)
                            learned = True
                    if learned:
                        with open(FILE_QA, "a", encoding="utf-8") as f: 
                            f.write(f"\n{kw_part}|{ans}")
                        print(f"[AI]: {apply_synonyms('学到了！已记住新回答。')} {get_mood_emoji(u)}")
                    else:
                        print(f"[AI]: {apply_synonyms('我已经知道这个回答了，不需要重复学习。')} {get_mood_emoji(u)}")
                continue

            # [E] 完成任务触发
            if "我做完了" in u:
                if memory["tasks"]:
                    context["state"] = "DELETE_TASK"
                    context["task_to_del"] = memory["tasks"][-1][1]
                    print(f"[AI]: 你完成任务了吗？是指 '{context['task_to_del']}' 吗？回复'是'将自动删除。")
                else:
                    print(f"[AI]: 你的任务清单现在是空的。 {get_mood_emoji(u)}")
                continue

            # [F] 插件：天气查询 (调用独立预留的接口函数)
            weather_m = re.search(r'(.*)天气', u)
            if weather_m:
                city = weather_m.group(1).strip() or "本地"
                weather_info = fetch_local_weather(city)
                print(f"[AI]: {weather_info} {get_mood_emoji(u)}")
                continue

            # [G] 插件：任务录入
            match_task = re.search(r'(今天|明天|下周)?.*(记得|提醒)(.*)', u)
            if match_task:
                date_val = parse_relative_date(match_task.group(1))
                content = match_task.group(3).strip()
                if content:
                    with open(FILE_TASKS, "a", encoding="utf-8") as f: f.write(f"{date_val}|{content}\n")
                    memory["tasks"].append([date_val, content])
                    print(f"[AI]: 没问题，记下了：{date_val} 提醒您 {content}。 {get_mood_emoji(u)}")
                    continue

            # [H] 新增：用户档案 - 主动记忆与提取
            # 记忆逻辑：当我输入 "我喜欢苹果" 或 "我讨厌张三" 或 "我的爱好是看书" 时自动保存
            profile_learn = re.search(r'我(喜欢|讨厌|爱好是|爱)(.*)', u)
            if profile_learn and not u.endswith("什么") and not u.endswith("谁"):
                p_key = profile_learn.group(1).replace("是", "") # 提取"喜欢"/"讨厌"/"爱好"
                p_val = profile_learn.group(2).strip()
                if p_val:
                    memory["profile"].setdefault(p_key, [])
                    if p_val not in memory["profile"][p_key]:
                        memory["profile"][p_key].append(p_val)
                        with open(FILE_PROFILE, "a", encoding="utf-8") as f: f.write(f"{p_key}|{p_val}\n")
                        print(f"[AI]: {apply_synonyms('收到，我已经记住了你的这个信息。非常开心能更了解你！')} {get_mood_emoji(u)}")
                    else:
                        print(f"[AI]: 这个档案我早就记住啦。 {get_mood_emoji(u)}")
                    continue

            # 提取逻辑：当我询问 "我喜欢什么" 或 "我讨厌谁" 时提取档案
            profile_query = re.search(r'我(喜欢|讨厌|爱好)(什么|谁)', u)
            if profile_query:
                p_key = profile_query.group(1)
                p_vals = memory["profile"].get(p_key, [])
                if p_vals:
                    items = "、".join(p_vals)
                    print(f"[AI]: 我记得你的{p_key}是：{items}。对吧？ {get_mood_emoji(u)}")
                else:
                    print(f"[AI]: 抱歉，我的档案里还没记录你{p_key}什么，快告诉我吧！ {get_mood_emoji(u)}")
                continue

            # [I] 插件：笑话与数学题
            if "笑话" in u:
                if memory["jokes"]:
                    ans_text = apply_synonyms(f"给你讲个笑话：{random.choice(memory['jokes'])}")
                    print(f"[AI]: {ans_text} {get_mood_emoji(u)}")
                else:
                    print(f"[AI]: 笑话库空空如也。 {get_mood_emoji(u)}")
                continue
                
            if "数学" in u:
                if memory["math"]:
                    q, a = random.choice(memory["math"])
                    context["state"] = "MATH"
                    context["math_answer"] = a
                    print(f"[AI]: 请听题：{q} 等于多少？ {get_mood_emoji(u)}")
                else:
                    print(f"[AI]: 没找到数学题库文件。 {get_mood_emoji(u)}")
                continue

             # [J] 知识库检索引擎 (优化：最长匹配优先)
from rapidfuzz import process, fuzz

# [智能匹配]
matched = False
# 直接找最像的那个，cutoff=70 表示相似度至少要 70% 才算匹配
# keys 就是你所有的关键词
keys = list(memory["qa"].keys())
match = process.extractOne(u, keys, scorer=fuzz.token_sort_ratio)

if match and match[1] >= 70:
    best_key = match[0]
    print(f"[AI]: (猜你在问'{best_key}') {random.choice(memory['qa'][best_key])} {get_mood_emoji(u)}")
    matched = True

# 只有没匹配到才报不懂
if not matched: 
    print(f"[AI]: 我还不懂呢，教我一下？（用法：回答|关键词|内容）")




            # [K] 历史上下文意图联想补全
            if not matched and len(history_stack) > 1:
                combined = history_stack[-2] + u
                for kw, answers in memory["qa"].items():
                    if re.search(re.escape(kw), combined):
                        ans_text = apply_synonyms(random.choice(answers))
                        print(f"[AI]: (结合上文) {ans_text} {get_mood_emoji(u)}")
                        matched = True
                        break

            # [L] 兜底未匹配回复
            if not matched: 
                print(f"[AI]: 抱歉，我还不太懂这个。你可以用 '回答|关键词|内容' 教教我。 {get_mood_emoji(u)}")

        except Exception as e:
            print(f"[系统错误]: 发生异常，信息为: {e}")

if __name__ == "__main__":
    chat()
