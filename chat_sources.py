# chat_sources.py

def fetch_youtube_chat():
    # Placeholder: Replace with real YouTube integration
    yield "User1", "Hey everyone!"
    yield "ScammerYT", "Win prize now: https://bit.ly/scam"

def fetch_twitch_chat():
    # Placeholder: Replace with Twitch chat integration
    yield "TwitchFan", "Follow for follow!"
    yield "Troll123", "Claim Nitro: https://freestuff.io"

def fetch_discord_chat():
    # Placeholder: Replace with Discord bot integration
    yield "DiscordGuy", "Nice stream today!"
    yield "MaliciousUser", "Login fast: http://stealdata.ru"

def get_chat_source(platform):
    if platform == "YouTube":
        return fetch_youtube_chat
    elif platform == "Twitch":
        return fetch_twitch_chat
    elif platform == "Discord":
        return fetch_discord_chat
    else:
        raise ValueError("Unsupported platform")
