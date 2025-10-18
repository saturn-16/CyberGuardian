# main.py

import streamlit as st
import time
import os
import re
import collections # For deque in YouTubeChat

# --- Placeholder Dashboard and Detector (As provided previously) ---
def update_ui_with_message(placeholder_container, username, message, is_suspicious, reasons):
    # This function now adds to the Streamlit elements inside the provided container
    # It doesn't use st.empty() internally for messages anymore to avoid clearing
    with placeholder_container:
        if is_suspicious:
            st.error(f"🚨 **SUSPICIOUS** from {username}: {message} (Reasons: {', '.join(reasons)})")
        else:
            st.write(f"💬 {username}: {message}")

def show_suspicious_messages():
    if 'suspicious_log' in st.session_state and st.session_state.suspicious_log:
        st.subheader("⚠️ Detected Phishing Attempts")
        # Display in reverse order to show latest first
        for user, msg, reasons in reversed(st.session_state.suspicious_log):
            st.warning(f"**{user}**: {msg} (Reasons: {', '.join(reasons)})")
    else:
        st.info("No suspicious messages detected yet.")

def is_phishing(message):
    message_lower = message.lower()
    reasons = []
    
    phishing_keywords = ["free", "giveaway", "nitro", "bitcoin", "crypto", "usdt", "eth", "sol", "scam", "click here", "claim", "prize", "winner", "reward", "verify", "wallet", "login", "authenticate"]
    for keyword in phishing_keywords:
        if keyword in message_lower:
            reasons.append(f"Contains '{keyword}' keyword")

    if re.search(r'(bit\.ly|tinyurl\.com|goo\.gl|cutt\.ly|rebrand\.ly|is\.gd|t\.co)', message_lower) or \
       (re.search(r'discord\.gg/[a-zA-Z0-9]+', message_lower) and "discord.gg/your_legit_server_id" not in message_lower):
        reasons.append("Contains shortened or suspicious link pattern")
    
    if "you.tube.com" in message_lower or "youtub.com" in message_lower:
        reasons.append("Typo-squatting or misspelled domain detected")

    urgency_phrases = ["urgent", "immediately", "now", "last chance"]
    for phrase in urgency_phrases:
        if phrase in message_lower:
            reasons.append(f"Contains '{phrase}' urgency phrase")

    if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', message_lower):
        reasons.append("Contains an IP address")

    if len(reasons) >= 1:
        return True, reasons
    
    return False, []
# --- End Placeholder Imports ---

# Import actual chat source classes
from chat_sources.youtube import YouTubeChat
from chat_sources.twitch import TwitchChat
from chat_sources.discord import DiscordChat


# --- Session State Initialization ---
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'suspicious_log' not in st.session_state:
    st.session_state.suspicious_log = []
if 'chat_fetcher_instance' not in st.session_state:
    st.session_state.chat_fetcher_instance = None
if 'chat_message_history' not in st.session_state:
    st.session_state.chat_message_history = [] # New: Store all messages for persistent display

# --- Streamlit UI Setup ---
st.set_page_config(page_title="CyberGuardian AI", layout="wide")

st.title("🛡️ CyberGuardian AI — Real-Time Phishing Detection for Streamers")

platform = st.selectbox("Select Platform", ["YouTube", "Twitch", "Discord"], key="platform_select")

# Input fields and Start/Stop Monitoring buttons
with st.form("monitoring_form"):
    if platform == "YouTube":
        stream_url = st.text_input("Enter YouTube Live Stream URL:", key="youtube_url_input")
        start_monitoring_button_clicked = st.form_submit_button("Start Monitoring YouTube")

    elif platform == "Twitch":
        twitch_token = st.text_input("Enter Twitch OAuth Token:", type="password", key="twitch_token_input")
        twitch_channel = st.text_input("Enter Twitch Channel Name:", key="twitch_channel_input")
        start_monitoring_button_clicked = st.form_submit_button("Start Monitoring Twitch")

    elif platform == "Discord":
        st.info("Discord integration requires a bot to be set up and invited to your server.")
        start_monitoring_button_clicked = st.form_submit_button("Start Monitoring Discord")

    # Stop Monitoring button
    if st.session_state.monitoring_active:
        if st.form_submit_button("Stop Monitoring"):
            st.session_state.monitoring_active = False
            st.session_state.chat_fetcher_instance = None
            st.info("Monitoring stopped.")
            st.rerun()

# --- Logic for Starting Monitoring ---
if start_monitoring_button_clicked and not st.session_state.monitoring_active:
    st.session_state.monitoring_active = True
    st.session_state.suspicious_log = [] # Clear previous suspicious log on new start
    st.session_state.chat_message_history = [] # Clear chat history on new start

    try:
        if platform == "YouTube":
            if stream_url:
                st.session_state.chat_fetcher_instance = YouTubeChat(stream_url=stream_url)
            else:
                st.warning("Please enter a YouTube Live Stream URL to start monitoring.")
                st.session_state.monitoring_active = False
        elif platform == "Twitch":
            if twitch_token and twitch_channel:
                st.session_state.chat_fetcher_instance = TwitchChat(token=twitch_token, channel=twitch_channel)
            else:
                st.warning("Please enter both Twitch OAuth Token and Channel Name.")
                st.session_state.monitoring_active = False
        elif platform == "Discord":
            st.session_state.chat_fetcher_instance = DiscordChat()
        
    except (ValueError, FileNotFoundError, ConnectionError) as e:
        st.error(f"❌ Error setting up chat fetcher: {e}")
        st.session_state.monitoring_active = False
        st.session_state.chat_fetcher_instance = None
    except Exception as e:
        st.error(f"An unexpected error occurred during setup: {e}")
        st.session_state.monitoring_active = False
        st.session_state.chat_fetcher_instance = None

    st.rerun() # Rerun immediately after attempting to set up

# --- Live Chat Feed Display ---
if st.session_state.monitoring_active:
    st.success(f"✅ Monitoring started for {platform}...")
    st.subheader("Live Chat Feed")

    # Custom CSS for the scrollable chat box
    st.markdown("""
    <style>
    .chat-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        height: 400px; /* Fixed height for the chat box */
        overflow-y: auto; /* Enable vertical scrolling */
        background-color: #f9f9f9;
        margin-bottom: 15px;
        display: flex; /* Use flexbox to push content to bottom */
        flex-direction: column-reverse; /* New messages appear at the bottom */
    }
    .chat-message {
        margin-bottom: 5px;
        word-wrap: break-word; /* Ensure long words wrap */
    }
    </style>
    """, unsafe_allow_html=True)

    # This is the actual container where messages will be displayed
    # We use a unique key for the container to ensure it's stable across reruns
    chat_display_container = st.container(height=400, border=True) # Streamlit's native way to create scrollable container
                                                                  # This is better than custom CSS for basic scroll

    # Old way with custom CSS (less native Streamlit, but more control if needed)
    # chat_display_container = st.empty()
    # chat_display_container.markdown('<div class="chat-box" id="chat-scroll-area"></div>', unsafe_allow_html=True)
    # chat_inner_placeholder = chat_display_container.empty()


# --- Main Monitoring Loop ---
if st.session_state.monitoring_active and st.session_state.chat_fetcher_instance:
    # Use st.status for a loading indicator during fetch (optional)
    with st.status("Fetching new messages...", expanded=False, state="running") as status:
        try:
            messages_fetched = st.session_state.chat_fetcher_instance.fetch_messages()
            status.update(label=f"Fetched {len(messages_fetched)} new messages.", state="complete", expanded=False)
            
            if messages_fetched:
                for message_data in messages_fetched:
                    username = message_data.get("username", "Unknown")
                    message = message_data.get("message", "")

                    if not message:
                        continue
                    
                    is_suspicious, reasons = is_phishing(message)
                    
                    # Store message data along with its suspicious status and reasons
                    st.session_state.chat_message_history.append({
                        "username": username,
                        "message": message,
                        "is_suspicious": is_suspicious,
                        "reasons": reasons
                    })

                    if is_suspicious:
                        st.session_state.suspicious_log.append((username, message, reasons))
            # else:
            #     status.update(label="No new messages.", state="complete")

        except Exception as e:
            st.error(f"Error fetching or processing messages: {e}")
            st.session_state.monitoring_active = False
            st.session_state.chat_fetcher_instance = None
            status.update(label="Monitoring stopped due to error.", state="error")
            st.rerun() # Rerun to stop the loop

    # Re-render all messages from history into the chat_display_container
    # Using st.container(height=...) makes this straightforward.
    with chat_display_container:
        chat_display_container.empty() # Clear previous content before re-rendering
        for msg_data in st.session_state.chat_message_history:
            update_ui_with_message(st.empty(), # Pass an empty placeholder for each message
                                   msg_data["username"], 
                                   msg_data["message"], 
                                   msg_data["is_suspicious"], 
                                   msg_data["reasons"])
    
    # Scroll to the bottom if there are many messages (requires JS injection)
    # Streamlit's native container doesn't automatically scroll on new content.
    # For automatic scroll, you might need JavaScript.
    # Example (more advanced, often brittle with Streamlit reruns):
    # st.markdown("""
    # <script>
    #     var objDiv = document.getElementById("chat-scroll-area");
    #     if (objDiv) {
    #         objDiv.scrollTop = objDiv.scrollHeight;
    #     }
    # </script>
    # """, unsafe_allow_html=True)


    # Determine polling interval
    poll_interval = 3
    if hasattr(st.session_state.chat_fetcher_instance, 'get_poll_interval'):
        poll_interval = st.session_state.chat_fetcher_instance.get_poll_interval()

    time.sleep(poll_interval)
    st.rerun() # Trigger a rerun to fetch new messages


# --- Footer / Review Options ---
st.markdown("---")
if st.button("Show All Detected Phishing Attempts"):
    show_suspicious_messages()

# Display current suspicious messages if any were logged (useful after stopping monitoring)
if st.session_state.suspicious_log and not st.session_state.monitoring_active:
    st.subheader("⚠️ Detected Phishing Attempts (Last Session)")
    for user, msg, reasons in reversed(st.session_state.suspicious_log):
        st.warning(f"**{user}**: {msg} (Reasons: {', '.join(reasons)})")