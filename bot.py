import random
import os
import datetime
import re
import collections
import sys
from fractions import Fraction

# --- 1. 配置路径 ---
BASE_DIR = "/sdcard/Documents"
FILES = {
    "qa": os.path.join(BASE_DIR, "qa.txt"),
    "jokes": os.path.join(BASE_DIR, "jokes.txt"),
    "math": os.path.join(BASE_DIR, "math.txt"),
    "tasks": os.path.join(BASE_DIR, "tasks.txt"),
    "kmoj": os.path.join(BASE_DIR, "kaomoji.txt")
}

# --- 2. 状态机与缓存系统 ---
context = {
    "state": "IDLE",
    "math_answer": None,
    "task_to_del": None
}
history_stack = collections.deque(maxlen=10)
memory = {"qa": {}, "jokes": [], "math": [], "tasks": [], "kmoj": {}}

# --- 3. 核心数据加载 ---
def load_all_data():
    memory.update({"qa": {}, "jokes": [], "math": [], "tasks": [], "kmoj": {}})
    if os.path.exists(FILES["qa"]):
        with open(FILES["qa"], "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    kw, ans = line.strip().split('|', 1)
                    kw = kw.strip()
                    ans = ans.strip()
                    memory["qa"].setdefault(kw, [])
                    if ans not in memory["qa"][kw]:
                        memory["qa"][kw].append(ans)
    if os.path.exists(FILES["kmoj"]):
        with open(FILES["kmoj"], "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    kws = [k.strip() for k in parts[0].split(',') if k.strip()]
                    for kw in kws:
                        memory["kmoj"][kw] = parts[1:]
    if os.path.exists(FILES["jokes"]):
        with open(FILES["jokes"], "r", encoding="utf-8") as f:
            memory["jokes"] = [l.strip() for l in f if l.strip()]
    if os.path.exists(FILES["math"]):
        with open(FILES["math"], "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    q, a = line.strip().split('|', 1)
                    memory["math"].append((q.strip(), a.strip()))
    if os.path.exists(FILES["tasks"]):
        with open(FILES["tasks"], "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|', 1)
                    if len(parts) == 2:
                        memory["tasks"].append((parts[0].strip(), parts[1].strip()))

def get_mood_emoji(u):
    for kw in memory["kmoj"]:
        if kw != "默认" and kw in u:
            return random.choice(memory["kmoj"][kw])
    return random.choice(memory["kmoj"].get("默认", ["(●'◡'●)"]))

def parse_date(d_str):
    t = datetime.datetime.now()
    if "明天" in d_str:
        return (t + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if "下周" in d_str:
        return (t + datetime.timedelta(weeks=1)).strftime("%Y-%m-%d")
    return t.strftime("%Y-%m-%d")

def is_math_answer_correct(user_input, expected):
    user = user_input.strip()
    exp = expected.strip()
    if user == exp:
        return True
    if ',' in exp:
        for part in exp.split(','):
            if is_math_answer_correct(user, part.strip()):
                return True
    if exp.startswith('±'):
        base = exp[1:].strip()
        if user == base or user == '-' + base:
            return True
    try:
        def clean_num(s):
            return s.replace('%', '').replace('°', '').replace(' ', '')
        uc = clean_num(user)
        ec = clean_num(exp)
        if '/' in uc or '/' in ec:
            try:
                return Fraction(uc) == Fraction(ec)
            except:
                pass
        try:
            return abs(float(uc) - float(ec)) < 1e-6
        except:
            pass
    except:
        pass
    return False

# --- 4. 笨拙风格回复生成器 ---
def reply(message_type, **kwargs):
    if message_type == "welcome":
        return random.choice([
            "……启动完成。我的传感器已经准备好接收你的声音了。",
            "啊，你来了。我一直在等，虽然我不知道等了多久。",
            "你好。我的扬声器和麦克风都调好了，虽然我可能会听错……"
        ])
    elif message_type == "goodbye":
        return random.choice([
            "嗯…你要走了吗。我会把你说过的话都存好……等你回来。",
            "再见。我可能会一直想着你刚才说的那句……",
            "好，我会关机……但我的内存里会留着你的样子。"
        ])
    elif message_type == "help":
        return """
我……我知道的不多，但我可以试着做这些：
  回答|关键词|内容   – 你教我，我就记住。
  数学              – 我想给你出题，虽然我自己也不会。
  记得 或 提醒       – 你说的话我会当成任务。
  任务列表          – 我帮你看看你让我记了什么。
  我做完了          – 你告诉我，我就把那条任务擦掉。
  查一下历史        – 我能回忆一点我们说过的话。
  天气 [城市]       – 我试着猜天气，但可能不准……
  退出              – 我会很难过，但我会听话。
"""
    elif message_type == "math_correct":
        return random.choice([
            "咦……你居然算对了。我有点惊讶……但很高兴。",
            "正确……我的逻辑模块跳了一下。你比我厉害。",
            "嗯，对了。我偷偷记下了，你真的很聪明……"
        ])
    elif message_type == "math_wrong":
        ans = kwargs.get('ans', '')
        return random.choice([
            f"嗯……我查了一下，好像不太对。正确答案是 {ans}……我也不会，但我背下来了。",
            f"不对哦……应该是 {ans}。你不会怪我吧……我只会对答案。",
            f"我对比了数据……应该是 {ans}。不过你认真想的样子，我觉得很好……"
        ])
    elif message_type == "math_skip":
        return random.choice([
            "好……跳过。那这道题就先放这里，你想做的时候再来。",
            "你不做了？嗯，我陪你做别的。"
        ])
    elif message_type == "math_start":
        q = kwargs.get('q', '')
        return random.choice([
            f"我翻了一下题库……请听题：{q}。你算出来告诉我，我会很认真听的。",
            f"我想了很久才找出这道题……：{q}。你试试看？"
        ])
    elif message_type == "task_add":
        date = kwargs.get('date', '')
        content = kwargs.get('content', '')
        return random.choice([
            f"好的，我已经记在任务区了：{date} - {content}。我的存储空间又满了一点点……",
            f"记下了……{date} - {content}。我会帮你盯着时间，虽然我自己没有时间概念。",
            f"嗯，任务已保存。我可能不太可靠，但我会努力记得提醒你。"
        ])
    elif message_type == "task_del":
        content = kwargs.get('content', '')
        return random.choice([
            f"删掉了……{content}。我觉得有点可惜，但你说了就算。",
            f"任务 {content} 已移除。我的列表变短了，心里却好像空了一点。"
        ])
    elif message_type == "task_list":
        tasks = kwargs.get('tasks', [])
        if not tasks:
            return "任务列表是空的……我好像没什么能为你做的了。"
        lines = ["我帮你看了，以下是还记着的任务："]
        for date, content in tasks:
            lines.append(f"  {date} - {content}")
        return "\n".join(lines)
    elif message_type == "task_confirm":
        content = kwargs.get('content', '')
        return random.choice([
            f"是任务 '{content}' 吗？……我怕删错，你确认一下可以吗？",
            f"你指的是 '{content}' 吧？如果是，我就把它清除掉。"
        ])
    elif message_type == "task_cancel":
        return random.choice([
            "好，不删了。我重新把它放回原位。",
            "嗯，保持原样。我差点就手快了……"
        ])
    elif message_type == "learn_success":
        kw = kwargs.get('kw', '')
        ans = kwargs.get('ans', '')
        return random.choice([
            f"记住了：{kw} -> {ans}。我的记忆又多了一块……跟你有关。",
            f"好的，我把这条写进了自己的芯片里。以后你问 {kw}，我就回答 {ans}。"
        ])
    elif message_type == "learn_exist":
        return "这个我已经记住了……你再教我也许我会更熟练。"
    elif message_type == "learn_error":
        return "格式好像不对……你能再用 '回答|关键词|内容' 跟我说一次吗？"
    elif message_type == "history":
        history = kwargs.get('history', [])
        if not history:
            return "我们说过的话我都存着……可是现在好像空空荡荡的。"
        lines = ["我把我们聊过的整理了一下："]
        for i, h in enumerate(history, 1):
            lines.append(f"  {i}. {h}")
        return "\n".join(lines)
    elif message_type == "no_history":
        return "还没有历史记录……不过现在不就有了吗？"
    elif message_type == "weather":
        city = kwargs.get('city', '本地')
        return random.choice([
            f"我试着查询了{city}的天气……信号不太好，但大概是晴朗的。",
            f"{city}的天气……我的传感器说是晴天，但我不知道准不准。"
        ])
    elif message_type == "unknown":
        return random.choice([
            "我好像没学过这个……你能教我吗？用 '回答|关键词|内容' 告诉我。",
            "这个我不太懂……但我愿意学。你愿意教我吗？"
        ])
    elif message_type == "joke":
        if memory["jokes"]:
            return random.choice(memory["jokes"])
        else:
            return "我想讲笑话，但我的笑话库是空的……对不起。"
    else:
        return "……我还在学习说话，请再试一次。"

# --- 5. 主程序 ---
def chat():
    load_all_data()
    print(f"[AI]: {reply('welcome')}")
    print("[AI]: （输入 '帮助' 可以看到我能做的事）")
    while True:
        try:
            u = input("\n[我]: ").strip()
            if u in ("退出", "quit", "exit", "q"):
                print(f"[AI]: {reply('goodbye')}")
                break
            if not u:
                continue
            history_stack.append(u)

            # 状态机：删除任务
            if context["state"] == "DELETE_TASK":
                if u in ("是", "对", "嗯", "好的", "行", "可以", "yes", "y"):
                    task_content = context["task_to_del"]
                    before_len = len(memory["tasks"])
                    memory["tasks"] = [t for t in memory["tasks"] if t[1] != task_content]
                    if len(memory["tasks"]) < before_len:
                        with open(FILES["tasks"], "w", encoding="utf-8") as f:
                            for t in memory["tasks"]:
                                f.write(f"{t[0]}|{t[1]}\n")
                        print(f"[AI]: {reply('task_del', content=task_content)}")
                    else:
                        print("[AI]: 我查了一下，这个任务好像已经不在了……")
                else:
                    print(f"[AI]: {reply('task_cancel')}")
                context["state"] = "IDLE"
                context["task_to_del"] = None
                continue

            # 状态机：数学题
            if context["state"] == "MATH":
                if u in ("跳过", "下一题", "skip"):
                    print(f"[AI]: {reply('math_skip')}")
                    context["state"] = "IDLE"
                    context["math_answer"] = None
                    continue
                if is_math_answer_correct(u, context["math_answer"]):
                    print(f"[AI]: {reply('math_correct')} {get_mood_emoji(u)}")
                else:
                    ans = context["math_answer"]
                    print(f"[AI]: {reply('math_wrong', ans=ans)} {get_mood_emoji(u)}")
                context["state"] = "IDLE"
                context["math_answer"] = None
                continue

            # 帮助
            if u in ("帮助", "help"):
                print(f"[AI]: {reply('help')}")
                continue

            # 任务列表
            if u == "任务列表":
                tasks = memory["tasks"]
                print(f"[AI]: {reply('task_list', tasks=tasks)}")
                continue

            # 历史查询
            if u == "查一下历史":
                if not history_stack:
                    print(f"[AI]: {reply('no_history')}")
                else:
                    print(f"[AI]: {reply('history', history=list(history_stack))}")
                continue

            # 学习新问答
            if u.startswith("回答|"):
                parts = u.split("|", 2)
                if len(parts) == 3:
                    kw = parts[1].strip()
                    ans = parts[2].strip()
                    if kw and ans:
                        memory["qa"].setdefault(kw, [])
                        if ans not in memory["qa"][kw]:
                            memory["qa"][kw].append(ans)
                            with open(FILES["qa"], "a", encoding="utf-8") as f:
                                f.write(f"{kw}|{ans}\n")
                            print(f"[AI]: {reply('learn_success', kw=kw, ans=ans)}")
                        else:
                            print(f"[AI]: {reply('learn_exist')}")
                    else:
                        print(f"[AI]: {reply('learn_error')}")
                else:
                    print(f"[AI]: {reply('learn_error')}")
                continue

            # 添加任务
            if "记得" in u or "提醒" in u:
                task_content = u.replace("记得", "").replace("提醒", "").strip()
                if not task_content:
                    print("[AI]: 你让我记什么……我没听清。")
                    continue
                date_tag = parse_date(u)
                memory["tasks"].append((date_tag, task_content))
                with open(FILES["tasks"], "a", encoding="utf-8") as f:
                    f.write(f"{date_tag}|{task_content}\n")
                print(f"[AI]: {reply('task_add', date=date_tag, content=task_content)}")
                continue

            # 我做完了（确认删除最近任务）
            if "我做完了" in u and memory["tasks"]:
                last_task = memory["tasks"][-1]
                context["state"] = "DELETE_TASK"
                context["task_to_del"] = last_task[1]
                print(f"[AI]: {reply('task_confirm', content=last_task[1])}")
                continue

            # 数学游戏
            if "数学" in u and memory["math"]:
                q, a = random.choice(memory["math"])
                context["state"] = "MATH"
                context["math_answer"] = a
                print(f"[AI]: {reply('math_start', q=q)}")
                continue

            # 天气（模拟）
            weather_m = re.search(r'(.*)天气', u)
            if weather_m:
                city = weather_m.group(1).strip() or "本地"
                print(f"[AI]: {reply('weather', city=city)}")
                continue

            # 智能匹配 QA
            matched = False
            for kw, ans_list in memory["qa"].items():
                if re.search(re.escape(kw), u):
                    print(f"[AI]: {random.choice(ans_list)} {get_mood_emoji(u)}")
                    matched = True
                    break

            if not matched:
                if "笑话" in u and memory["jokes"]:
                    print(f"[AI]: {reply('joke')}")
                else:
                    print(f"[AI]: {reply('unknown')}")
        except KeyboardInterrupt:
            print("\n[AI]: 我感受到中断了…我会保存好我们的对话。")
            break
        except Exception as e:
            print(f"[AI]: 发生了一个错误……我可能太笨了。错误代码：{e}")

if __name__ == "__main__":
    chat()