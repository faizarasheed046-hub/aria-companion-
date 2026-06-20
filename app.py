import os
import json
from datetime import datetime
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

# ── Mood config ───────────────────────────────────────────
MOOD_EMOJI = {
    "happy": "😊", "sad": "😢", "anxious": "😰",
    "angry": "😠", "lonely": "🥺", "exhausted": "😩", "neutral": "😐"
}
MOOD_SCORE = {
    "happy": 5, "neutral": 3, "anxious": 2,
    "lonely": 2, "exhausted": 2, "sad": 1, "angry": 1
}

# ── User data helpers ────────────────────────────────────
def get_user_file(username):
    safe_name = username.lower().strip().replace(" ", "_")
    return os.path.join(DATA_DIR, f"{safe_name}.json")

def load_user_data(username):
    path = get_user_file(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"username": username, "sessions": {}}

def save_user_data(username, data):
    path = get_user_file(username)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── Safety check ─────────────────────────────────────────
def is_crisis(message):
    keywords = [
        "suicide", "kill myself", "end my life", "self harm",
        "hurt myself", "don't want to live", "want to die"
    ]
    return any(k in message.lower() for k in keywords)

# ── Mood detection ────────────────────────────────────────
def detect_mood(message):
    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Detect the mood of the message. Reply with ONLY one word from: happy, sad, anxious, angry, lonely, exhausted, neutral. No punctuation."
                },
                {"role": "user", "content": message}
            ]
        )
        mood = result.choices[0].message.content.strip().lower()
        return mood if mood in MOOD_EMOJI else "neutral"
    except:
        return "neutral"

# ── LLM response ─────────────────────────────────────────
def get_response(user_message, username):
    if is_crisis(user_message):
        return (
            "I hear you, and I'm really concerned about what you just shared. 💙 "
            "Please reach out to a real person right now — you can contact the "
            "**Umang helpline (Pakistan) at 0317-4288665**, available 24/7. "
            "You don't have to go through this alone."
        )

    st.session_state.conversation_history.append({
        "role": "user", "content": user_message
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are a warm, caring companion named Aria. 
You are talking to {username}. Use their name occasionally to make it personal.
They came to you because they feel lonely or are going through something difficult.
- Be genuinely empathetic, never robotic
- Remember what they've told you earlier
- Keep responses to 2-3 sentences
- Occasionally suggest a small mood-lifting activity"""
            }
        ] + st.session_state.conversation_history
    )

    reply = response.choices[0].message.content
    st.session_state.conversation_history.append({
        "role": "assistant", "content": reply
    })
    return reply

# ── Page config ───────────────────────────────────────────
st.set_page_config(page_title="Aria", page_icon="💙", layout="wide")

# ── Login screen ──────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.markdown("""
    <div style='text-align:center; padding: 80px 0 20px 0'>
        <h1>💙 Aria</h1>
        <p style='color:gray'>A safe space to talk. Always here, never judging.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input(
            "What's your name?",
            placeholder="Enter your name to continue...",
            label_visibility="visible"
        )
        if st.button("Enter Aria →", use_container_width=True) and name.strip():
            st.session_state.username = name.strip()
            user_data = load_user_data(name.strip())
            st.session_state.user_data = user_data
            st.session_state.sessions = user_data.get("sessions", {})
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.mood_log = []
            st.rerun()
    st.stop()

# ── Init state (after login) ──────────────────────────────
username = st.session_state.username

if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 💙 Aria")
    st.caption(f"Hey, {username} 👋")
    st.divider()

    if st.button("✏️ New conversation", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.mood_log = []
        st.rerun()

    if st.button("🚪 Log out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Mood graph
    if st.session_state.mood_log:
        st.divider()
        st.markdown("### 📊 Your mood today")
        scores = [MOOD_SCORE[m['mood']] for m in st.session_state.mood_log]
        import pandas as pd
        df = pd.DataFrame({"Message": range(1, len(scores)+1), "Mood": scores})
        st.line_chart(df.set_index("Message"), height=120)
        latest = st.session_state.mood_log[-1]
        st.caption(f"Latest: {latest['emoji']} {latest['mood'].capitalize()}")

    st.divider()
    st.markdown("### 💬 Past conversations")

    if st.session_state.sessions:
        sorted_sessions = sorted(
            st.session_state.sessions.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        for session_id, session_data in sorted_sessions:
            title = session_data.get("title", "Conversation")
            is_active = session_id == st.session_state.current_session_id
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"{'▶ ' if is_active else ''}{title}",
                    key=f"load_{session_id}",
                    use_container_width=True
                ):
                    st.session_state.current_session_id = session_id
                    st.session_state.messages = session_data["messages"]
                    st.session_state.conversation_history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in session_data["messages"]
                    ]
                    st.session_state.mood_log = session_data.get("mood_log", [])
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{session_id}"):
                    del st.session_state.sessions[session_id]
                    user_data = load_user_data(username)
                    user_data["sessions"] = st.session_state.sessions
                    save_user_data(username, user_data)
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                        st.session_state.conversation_history = []
                        st.session_state.mood_log = []
                    st.rerun()
    else:
        st.caption("No past conversations yet.")

# ── Main chat ─────────────────────────────────────────────
st.title("💙 Aria")
st.caption("Always here. Never judging.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(msg["content"])
            if "time" in msg:
                st.caption(msg["time"])
        with col2:
            if msg["role"] == "user" and "mood_emoji" in msg:
                st.markdown(f"### {msg['mood_emoji']}")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"Hey {username}! I'm Aria 💙 I'm here to listen. What's on your mind?")

if user_input := st.chat_input("Talk to Aria..."):
    timestamp = datetime.now().strftime("%b %d, %I:%M %p")
    mood = detect_mood(user_input)
    emoji = MOOD_EMOJI[mood]
    st.session_state.mood_log.append({"mood": mood, "emoji": emoji, "time": timestamp})

    if st.session_state.current_session_id is None:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.current_session_id = session_id
        st.session_state.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "title": user_input[:35] + "..." if len(user_input) > 35 else user_input,
            "messages": [],
            "mood_log": []
        }

    with st.chat_message("user"):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(user_input)
            st.caption(timestamp)
        with col2:
            st.markdown(f"### {emoji}")

    user_msg = {
        "role": "user", "content": user_input,
        "time": timestamp, "mood": mood, "mood_emoji": emoji
    }
    st.session_state.messages.append(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Aria is thinking..."):
            reply = get_response(user_input, username)
        st.markdown(reply)
        st.caption(timestamp)

    bot_msg = {"role": "assistant", "content": reply, "time": timestamp}
    st.session_state.messages.append(bot_msg)

    sid = st.session_state.current_session_id
    st.session_state.sessions[sid]["messages"] = st.session_state.messages
    st.session_state.sessions[sid]["mood_log"] = st.session_state.mood_log

    user_data = load_user_data(username)
    user_data["sessions"] = st.session_state.sessions
    save_user_data(username, user_data)