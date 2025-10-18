import streamlit as st

def init_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "monitoring" not in st.session_state:
        st.session_state.monitoring = False

    st.subheader("🔍 Chat Analysis")
    if not st.session_state.messages:
        st.write("No messages to display yet.")
    else:
        for m in st.session_state.messages[-30:]:
            with st.chat_message("user"):
                st.markdown(f"**{m['author']}**: {m['message']}")
                if m["flagged"]:
                    st.error(f"🚨 Phishing Detected: [Link]({m['url']})" if m["url"] else "⚠️ Suspicious message.")

def update_ui_with_message(author, message, flagged=False, url=None):
    st.session_state.messages.append({
        "author": author,
        "message": message,
        "flagged": flagged,
        "url": url
    })
