import httpx
import feedparser
import asyncio
import logging
import json
import os

logger = logging.getLogger(__name__)

class NewsClient:
    SOURCES_FILE = "sources.json"

    DEFAULT_SOURCES = [
        "https://cointelegraph.com/rss",
        "https://cryptonews.com/news/feed/",
        "https://u.today/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://cryptoslate.com/feed/",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://finance.yahoo.com/news/rssindex"
    ]

    @classmethod
    def get_sources(cls) -> list[str]:
        if not os.path.exists(cls.SOURCES_FILE):
            try:
                with open(cls.SOURCES_FILE, 'w') as f:
                    json.dump(cls.DEFAULT_SOURCES, f)
                return cls.DEFAULT_SOURCES
            except Exception as e:
                logger.error(f"Error creando {cls.SOURCES_FILE}: {e}")
                return cls.DEFAULT_SOURCES
            
        try:
            with open(cls.SOURCES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo {cls.SOURCES_FILE}: {e}")
            return cls.DEFAULT_SOURCES

    @classmethod
    def add_source(cls, url: str) -> list[str]:
        sources = cls.get_sources()
        if url not in sources:
            sources.append(url)
            with open(cls.SOURCES_FILE, 'w') as f:
                json.dump(sources, f)
        return sources

    @classmethod
    def remove_source(cls, url: str) -> list[str]:
        sources = cls.get_sources()
        if url in sources:
            sources.remove(url)
            with open(cls.SOURCES_FILE, 'w') as f:
                json.dump(sources, f)
        return sources

    @classmethod
    async def fetch_one_source(cls, url: str) -> list[dict]:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5"
                }
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status() # Lanza error si la web devuelve 403 o 404
                
                # feedparser es tolerante a fallos y lee XML sucio sin quejarse
                feed = feedparser.parse(response.text)
                
                news_items = []
                for entry in feed.entries:
                    if hasattr(entry, 'title') and hasattr(entry, 'link'):
                        news_items.append({
                            "title": entry.title,
                            "url": entry.link
                        })
                return news_items
            except Exception as e:
                logger.warning(f"Fuente ignorada ({url}): {e}")
                return []

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[dict]:
        active_sources = cls.get_sources()
        
        tasks = [cls.fetch_one_source(url) for url in active_sources]
        results = await asyncio.gather(*tasks)
        
        all_news = [item for source_list in results for item in source_list]
        currency_upper = currency.upper()
        
        filtered = [item for item in all_news if currency_upper in item["title"].upper()][:limit]
        return filtered