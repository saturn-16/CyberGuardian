import joblib
import re
import os
import streamlit as st

@st.cache_resource
def load_ml_assets():
    try:
        model_path = "ml_model.pkl"
        vectorizer_path = "vectorizer.pkl"

        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            st.error(f"Error: Model or vectorizer not found. Please run 'python train_model.py' first.")
            return None, None

        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        return model, vectorizer
    except Exception as e:
        st.error(f"Error loading ML model assets: {e}")
        return None, None

model, vectorizer = load_ml_assets()

# --- URL Analysis Helper Functions (No changes) ---

def contains_url(text):
    return bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))

def extract_urls(text):
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def is_shortened_url(url):
    shortener_domains = ['bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'cutt.ly', 'rebrand.ly', 'rb.gy', 'qr.net', 'buff.ly', 'is.gd', 's.id']
    try:
        domain = re.search(r'https?://(?:www\.)?([^/]+)', url).group(1)
        return any(sd in domain for sd in shortener_domains)
    except AttributeError:
        return False

def check_url_reputation(url):
    url_lower = url.lower()
    suspicious_tlds = ['.xyz', '.top', '.tk', '.online', '.site', '.info', '.biz', '.club', '.ru', '.cf', '.ga', '.gq', '.ml', '.pw', '.win', '.icu', '.bid', '.gdn', '.men']

    if re.search(r'http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower):
        return True, "URL uses an IP address instead of a domain name."

    if is_shortened_url(url):
        return True, "URL is a shortened link (common in phishing)."

    if any(tld in url_lower for tld in suspicious_tlds):
        return True, f"URL uses a suspicious TLD: {next(tld for tld in suspicious_tlds if tld in url_lower)}"

    phishing_keywords_in_url = ['login', 'verify', 'update', 'account', 'security', 'secure',
                                'paypal', 'bank', 'amazon', 'google', 'microsoft', 'apple',
                                'free', 'gift', 'prize', 'crypto', 'nft', 'discord', 'twitch',
                                'steam', 'netflix', 'roblox', 'grant', 'claim', 'urgent', 'confirm']
    common_brands = ['paypal', 'google', 'amazon', 'netflix', 'apple', 'microsoft', 'facebook', 'steam', 'twitch', 'discord', 'roblox', 'walmart']

    for keyword in phishing_keywords_in_url:
        if keyword in url_lower:
            if any(tld in url_lower for tld in suspicious_tlds):
                 return True, f"URL contains '{keyword}' and uses a suspicious TLD."

            for brand in common_brands:
                if brand in url_lower:
                    if not (f"{brand}.com" in url_lower or f"{brand}.net" in url_lower or f"{brand}.org" in url_lower):
                        return True, f"Potential brand impersonation: '{brand}' with non-standard TLD and keyword '{keyword}'."

    return False, "No suspicious patterns found by heuristics."


class PhishingDetector:
    def __init__(self):
        if model is None or vectorizer is None:
            st.warning("ML model or vectorizer not loaded. Phishing detection will rely only on URL heuristics and refined keywords for now.")
        self.model = model
        self.vectorizer = vectorizer
        self.phishing_threshold = 0.8 # Keep high for ML conservatism

        # Phishing Phrases: REMOVING generic 'now' and specific 'sol' from here.
        # We will rely on ML for general urgency/crypto, and exclusions for Streamlabs.
        self.phishing_phrases = [
            r'\baccount (suspended|locked|limited)\b', r'\b(urgent|immediate) action required\b', r'\bverify your (account|details|identity)\b',
            r'\bsecurity alert\b', r'\bunusual login\b', r'\bfinal warning\b', r'\bdata breach\b',
            r'\bconfirm your (details|info)\b', r'\breset (your)? password\b', r'\blogin (now|here)\b', # login now/here is fine
            r'\bclaim your prize\b', r'\bfree money\b', r'\bget rich quick\b', r'\b(win|won) (big|prize)\b',
            r'\bcongratulations you\'ve won\b', r'\bgovernment grant\b', r'\bfree bitcoin\b', r'\bfree crypto\b',
            r'\bfree nft\b', r'\bfree robux\b', r'\bgift card\b', r'\bexclusive offer\b', r'\blimited time offer\b',
            r'\bdouble your crypto\b', r'\bwallet connect\b', r'\b(crypto|nft|token) airdrop\b',
            r'\bpaypal (verification|security)\b', r'\bnetflix suspended\b', r'\bapple id update\b',
            r'\bsteam security\b', r'\bdiscord nitro (giveaway|free)\b', r'\btwitch prime (expiring|renewal)\b',
            r'\bamazon account (issue|alert)\b', r'\b(your|your\'s) (account|wallet) is (locked|frozen|suspended)\b',
            r'\bclick here to (claim|verify|login|update)\b'
        ]

        # --- REVISED GENERAL EXCLUSION PATTERNS (Even more comprehensive) ---
        self.general_exclusion_patterns = [
            # Streamlabs general pattern: Any message starting with "Streamlabs:"
            re.compile(r'^Streamlabs:', re.IGNORECASE),

            # Handle the "AJ: !duel @Lalitkumar Solapure all" type messages and similar
            re.compile(r'\b!duel\s+@?\w+.*?Solapure\b', re.IGNORECASE),
            re.compile(r'\b@AJ\s+and\s+@Lalitkumar Solapure\b', re.IGNORECASE), # For "thanks @AJ and @Lalitkumar Solapure"

            # Specific Name Exclusions (for 'sol' in 'Solapure', 'eth' in 'Navaneeth')
            re.compile(r'.*?\bLalitkumar Solapure\b.*?', re.IGNORECASE),
            re.compile(r'.*?\bNavaneeth\b.*?', re.IGNORECASE),

            # Contextual exclusions for very common words like "free" and "bitcoin"
            re.compile(r'\bfree\b(?:.*?\b(?:superchat|promote|game|giveaway|trial|playing|loan|denga|bhai|pura cafe|naam kar|contract sign)\b)?', re.IGNORECASE),
            re.compile(r'\bbitcoin\b(?:.*?\b(?:price|market|currency|trade|buy|sell|value|lekin wo aisa|kyun|mai toh vct|krdega)\b)?', re.IGNORECASE),
            re.compile(r'\bbtc\b(?:.*?\b(?:price|market|currency|trade|buy|sell|value)\b)?', re.IGNORECASE),

            # Explicitly exclude "happy now"
            re.compile(r'\bhappy now\b', re.IGNORECASE)
        ]


    def is_phishing(self, message):
        flagged = False
        suspicious_url = None
        reasons = []
        message_lower = message.lower()

        # 0. Check General Exclusion Patterns first (most specific false positive filters)
        for pattern in self.general_exclusion_patterns:
            if pattern.search(message):
                # If a message matches an exclusion pattern, it's definitely not phishing by these rules.
                # This prevents subsequent checks from flagging it.
                return False, None, f"Matched exclusion pattern: '{pattern.pattern}'"

        # 1. URL Heuristics (if not already excluded)
        urls = extract_urls(message)
        if urls:
            for url in urls:
                is_url_suspicious, url_reason = check_url_reputation(url)
                if is_url_suspicious:
                    flagged = True
                    suspicious_url = url
                    reasons.append(f"URL Heuristics: {url_reason} ({url})")
                    break

        # 2. Refined Keyword/Phrase-based Detection (if not already flagged)
        if not flagged:
            for phrase_regex in self.phishing_phrases:
                if re.search(phrase_regex, message, re.IGNORECASE):
                    # Contextual exclusion for "not phishing"
                    if "this is not phishing" in message_lower or "anti-phishing" in message_lower:
                        continue
                    
                    flagged = True
                    reasons.append(f"Keyword/Phrase detected: '{phrase_regex}'")
                    break

        # 3. ML Model Prediction (if not already flagged)
        if not flagged and self.model and self.vectorizer:
            try:
                message_vec = self.vectorizer.transform([message])
                probabilities = self.model.predict_proba(message_vec)[0]
                phishing_proba = probabilities[1]

                if phishing_proba >= self.phishing_threshold:
                    flagged = True
                    reasons.append(f"ML Model (Phishing Probability: {phishing_proba:.2f})")
            except Exception as e:
                # print(f"Error during ML prediction: {e}") # For debugging ML issues
                pass # Suppress error if ML model/vectorizer isn't loaded or fails

        return flagged, suspicious_url, ", ".join(reasons) if reasons else "No specific reason."