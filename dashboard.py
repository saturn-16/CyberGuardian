# dashboard.py

import streamlit as st
import pandas as pd
import os

suspicious_csv = "suspicious_messages.csv"

# Initialize session state if not already
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "platform" not in st.session_state:
    st.session_state.platform = None

if "stream_url" not in st.session_state:
    st.session_state.stream_url = ""

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "suspicious_messages" not in st.session_state:
    st.session_state.suspicious_messages = []

def update_ui_with_message(message, is_phishing, sender=None):
    """Append and display chat messages in the chat box."""
    formatted_message = f"👤 {sender}: {message}" if sender else message
    if is_phishing:
        st.markdown(f"<div style='color:red; font-weight:bold;'>🚨 {formatted_message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:green;'>{formatted_message}</div>", unsafe_allow_html=True)

def log_suspicious_message(sender, message):
    """Log suspicious message to CSV and session_state."""
    entry = {"sender": sender, "message": message}
    st.session_state.suspicious_messages.append(entry)

    # If file exists, load and append only if not duplicate
    if os.path.exists(suspicious_csv):
        df = pd.read_csv(suspicious_csv)
        if not ((df["sender"] == sender) & (df["message"] == message)).any():
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            df.to_csv(suspicious_csv, index=False)
    else:
        df = pd.DataFrame([entry])
        df.to_csv(suspicious_csv, index=False)

def show_suspicious_messages():
    """Display suspicious messages logged so far."""
    st.subheader("🧾 Suspicious Messages Log")
    if os.path.exists(suspicious_csv):
        df = pd.read_csv(suspicious_csv)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No suspicious messages detected yet.")
    else:
        st.info("No suspicious messages logged yet.")
