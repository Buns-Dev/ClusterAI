# news.py – Immersive News Panel with Voice Isolation Filters
import feedparser
import urllib.parse

def get_news(source_or_country="bbc"):
    """Fetch top headlines, providing a graphical frame and an optimized voice cue."""
    feeds = {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "reuters": "https://www.reuters.com/rss/topNews",
        "cnn": "http://rss.cnn.com/rss/edition.rss",
        "techcrunch": "https://techcrunch.com/feed/"
    }
    
    clean_input = source_or_country.strip().lower()
    
    if clean_input in feeds:
        feed_url = feeds[clean_input]
        header_title = f"📰 CORE INTELLIGENCE FEED :: {clean_input.upper()}"
        voice_phrase = f"Synchronizing top headlines from the {clean_input} news grid."
    else:
        encoded_query = urllib.parse.quote(clean_input)
        feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        header_title = f"🌍 REGIONAL DATA LINK :: {clean_input.upper()} SYSTEM RECON"
        voice_phrase = f"Scanning regional tracking updates for records regarding {source_or_country}."

    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:5]
        
        if entries:
            # Channel 1: Graphical display box
            panel = f"{header_title}\n"
            panel += "———————————————————————————————————————————————————————\n"
            for idx, entry in enumerate(entries, 1):
                panel += f" [{idx}] {entry.title}\n"
            panel += "———————————————————————————————————————————————————————\n📡 Live satellite transmission feed synchronized."
            
            return {"ui": panel, "voice": voice_phrase + " Data grid updated."}
        else:
            return {
                "ui": f"⚠️ System warning: No active headline entries located for '{source_or_country}'.",
                "voice": f"No active data entries found for {source_or_country}."
            }
    except Exception:
        return {
            "ui": "❌ Critical link failure: Unable to establish secure RSS data connection.",
            "voice": "Critical intelligence data link failure."
        }