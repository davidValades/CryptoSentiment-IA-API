import httpx
import xml.etree.ElementTree as ET
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
        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = await client.get(url, headers=headers, timeout=8.0)
                root = ET.fromstring(response.text)
                
                news_items = []
                for item in root.findall('./channel/item'):
                    title = item.find('title')
                    link = item.find('link')
                    # Extraemos título y url para nuestra trazabilidad
                    if title is not None and title.text and link is not None and link.text:
                        news_items.append({
                            "title": title.text.strip(),
                            "url": link.text.strip()
                        })
                return news_items
            except Exception as e:
                logger.warning(f"Error consultando fuente {url}: {e}")
                return []

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[dict]:
        active_sources = cls.get_sources()
        
        tasks = [cls.fetch_one_source(url) for url in active_sources]
        results = await asyncio.gather(*tasks)
        
        # Aplanamos la lista de diccionarios
        all_news = [item for source_list in results for item in source_list]
        currency_upper = currency.upper()
        
        # Filtramos buscando el ticker dentro de la clave 'title'
        filtered = [item for item in all_news if currency_upper in item["title"].upper()][:limit]
        return filtered