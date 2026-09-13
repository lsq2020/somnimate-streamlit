from __future__ import annotations

import json
import os
from datetime import time

import httpx
import streamlit as st


APP_URL = "https://somnimate-sleep-companion.mullins-james.chatgpt.site/app"
AUDIO_ROOT = "https://somnimate-sleep-companion.mullins-james.chatgpt.site/audio/library"

PROFILES = {
    "高压职场": ("S01 下班减压", "先把工作心事放下，再听自然声；暖光和声音逐渐减弱。", "040.mp3"),
    "学生 / 初入职场": ("S02 快速入睡", "少问问题，用熟悉声音完成睡前收尾。", "110.mp3"),
    "轮班 / 夜班": ("S04 轮班白天睡", "按本次叫醒时间模拟夜间，不固定在传统作息。", "110.mp3"),
    "易夜醒": ("S03 夜间再入睡", "极低刺激，短语音后保持静默。", "032.mp3"),
    "父母 / 照护者": ("S09 父母起夜", "保留微亮夜灯，默认静音，回床后渐暗。", "031.mp3"),
    "中老年": ("S10 夜间起身", "简短提示并保留低位夜灯。", "040.mp3"),
    "规律优化": ("S12 周末慢慢睡", "记录偏好，不用睡眠分数制造压力。", "028.mp3"),
}

AUDIO = {
    "马头琴与钵声": "027.mp3", "河畔篝火与鸟鸣 I": "028.mp3", "河畔篝火与鸟鸣 II": "030.mp3",
    "温柔流水 · 上": "031.mp3", "温柔流水 · 下": "032.mp3", "钵音与流水": "033.mp3",
    "颂钵放松": "036.mp3", "乡村庭院": "037.mp3", "山涧小溪": "040.mp3", "深山鸟鸣": "041.mp3",
    "瑜伽冥想音乐": "042.mp3", "自然冥想音乐": "043.mp3", "睡前冥想引导": "044.mp3",
    "静坐助眠音乐": "046.mp3", "东北乡村清晨": "048.mp3", "核伙沟自然声": "049.mp3",
    "群鸭戏水": "050.mp3", "悦耳钟声": "104.mp3", "海雨涛声": "105.mp3", "夏夜蛙鸣": "106.mp3",
    "轻柔疗愈之音": "109.mp3", "风扇深睡声": "110.mp3", "水面涟漪": "111.mp3", "闭目放松": "112.mp3",
}

SYSTEM = """你是睡眠陪伴助手小眠。请用温柔、简短、非医疗的中文回应。
参考用户分层：高压职场、学生初职、轮班夜班、易夜醒、父母照护、中老年、规律优化。
目标是降低睡前认知负担，帮助用户收好待办并选择低刺激声音。不要诊断、治疗承诺或声称已经检测到睡着。
睡中数据都只能称为演示。回复不超过180字。"""


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return os.getenv(name, "")


def ask_deepseek(message: str, profile: str, scene: str) -> str:
    key = secret("DEEPSEEK_API_KEY")
    if not key:
        return "Streamlit Secrets 尚未配置 DeepSeek 密钥。当前可以继续使用场景、待办和声音；完整语音对话请进入 3D 主站。"
    history = st.session_state.messages[-6:]
    payload = {
        "model": secret("DEEPSEEK_MODEL") or "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM + f"\n当前用户：{profile}；当前场景：{scene}。"},
            *history,
            {"role": "user", "content": message[:2000]},
        ],
        "stream": False,
        "max_tokens": 450,
    }
    try:
        with httpx.Client(timeout=25) as client:
            response = client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "小眠暂时没有连上对话服务。你的待办和场景仍保留在本次页面中，请稍后再试。"


st.set_page_config(page_title="眠伴 · Streamlit 睡眠控制台", page_icon="🌙", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(160deg,#eee9df 0%,#e7e5e5 52%,#d7e3e0 100%);color:#3d5353}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1180px;padding-top:2rem}
.moon{height:220px;border:1px solid #ffffff80;border-radius:110px 110px 16px 16px;background:linear-gradient(155deg,#eab6ab,#f7ddbd 42%,#8cc8c5);display:grid;place-items:center;box-shadow:0 22px 70px #39545b22;margin:1rem 0 1.4rem}
.moon span{font-size:92px;filter:drop-shadow(0 14px 18px #6f686244)}
.story{letter-spacing:.08em;color:#6f7f7e;font-size:.85rem}.fine{color:#728180;font-size:.82rem;line-height:1.7}
div[data-testid="stMetric"]{border:1px solid #ffffff75;padding:1rem;border-radius:.6rem;background:#ffffff36}
</style>
""", unsafe_allow_html=True)

st.caption("SOMNIMATE · STREAMLIT CONTROL ROOM")
st.title("跟着月亮，慢慢离开今天。")
st.write("这是眠伴的 Streamlit 控制台。完整 3D 小人、浏览器连续语音和自动旅程保留在主站。")
st.link_button("进入完整 3D 助眠空间 ↗", APP_URL, type="primary", use_container_width=True)
st.markdown('<div class="moon"><span>☾</span></div>', unsafe_allow_html=True)

if "tasks" not in st.session_state:
    st.session_state.tasks = ["把手机放远一点"]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "phase" not in st.session_state:
    st.session_state.phase = "收好今天"

profile = st.selectbox("今晚陪伴谁？", list(PROFILES), index=0)
scene, strategy, default_audio = PROFILES[profile]

left, center, right = st.columns([1.1, 1, 1])
with left:
    st.subheader(scene)
    st.write(strategy)
    state_text = st.text_area("今天的状态", placeholder="例如：下夜班回来，身体很累，想在白天睡。", height=100)
with center:
    st.subheader("出发前的小事")
    with st.form("task_form", clear_on_submit=True):
        task = st.text_input("添加待办", max_chars=70, placeholder="例如：十点给客户回电话")
        if st.form_submit_button("替我记住") and task.strip():
            st.session_state.tasks.append(task.strip())
    for index, item in enumerate(st.session_state.tasks):
        st.checkbox(item, key=f"task_{index}")
with right:
    st.subheader("晨光约定")
    alarm = st.time_input("页面叫醒计划", value=time(7, 20))
    phase = st.segmented_control("旅程阶段", ["收好今天", "走进月门", "梦海守候", "晨光苏醒"], default=st.session_state.phase)
    if phase:
        st.session_state.phase = phase
    st.progress({"收好今天": 10, "走进月门": 32, "梦海守候": 68, "晨光苏醒": 90}[st.session_state.phase])
    st.markdown(f'<p class="fine">计划 {alarm.strftime("%H:%M")} 唤醒。Streamlit 页面不能代替系统闹钟。</p>', unsafe_allow_html=True)

st.divider()
sound_col, chat_col = st.columns([1, 1.25])
with sound_col:
    st.subheader("声音森林 · 24 段 MP3")
    default_name = next(name for name, filename in AUDIO.items() if filename == default_audio)
    name = st.selectbox("选择声音", list(AUDIO), index=list(AUDIO).index(default_name))
    st.audio(f"{AUDIO_ROOT}/{AUDIO[name]}", format="audio/mpeg", loop=name != "悦耳钟声")
    voice_note = st.audio_input("录下一句今晚的状态", sample_rate=16000)
    if voice_note:
        st.audio(voice_note)
        st.caption("录音仅用于本页回放；语音转文字与连续控制请进入完整 3D 主站。")

with chat_col:
    st.subheader("和小眠聊两句")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    prompt = st.chat_input("说说今天的状态，或请小眠给出今晚策略")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        reply = ask_deepseek(prompt, profile, scene)
        st.session_state.messages.extend([
            {"role": "user", "content": prompt[:2000]},
            {"role": "assistant", "content": reply},
        ])
        with st.chat_message("assistant"):
            st.write(reply)

st.divider()
st.subheader("晨光与梦境")
dream = st.text_area("醒来后，留下一句梦", placeholder="我梦见一片安静的海……")
if dream:
    recommendation = "海雨涛声 + 晨雾青绿" if any(x in dream for x in "海水雨") else "闭目放松 + 暖杏月光"
    st.success(f"梦的回声：{recommendation}")
st.caption("梦境推荐只是文字氛围匹配，不是心理或医学分析。心率、深浅睡眠和鼾声数据在本版本中均为演示。")

