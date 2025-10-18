import requests
import csv

# Step 1: Fetch phishing URLs from OpenPhish
url = "https://openphish.com/feed.txt"
response = requests.get(url)

# Step 2: Prepare message dataset
lines = response.text.strip().split('\n')
messages = [f"Check this out: {line.strip()}" for line in lines[:100]]

# Step 3: Save to CSV
with open("phishing_messages.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["message", "label"])
    for msg in messages:
        writer.writerow([msg, "phishing"])

print("✅ phishing_messages.csv created with real phishing URLs.")
