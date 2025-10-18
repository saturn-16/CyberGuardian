from detector import is_phishing

msg = "Free Nitro! https://bit.ly/freenitrocode"
flag, url = is_phishing(msg)
print("Flagged:", flag, "URL:", url)
