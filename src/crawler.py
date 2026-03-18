"""
phantom-browser-agent Web Crawler
Targets .fun .fm sites, agent platforms, DEXs across Solana and EVM chains
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
import logging
from datetime import datetime
import json

# Configuration
SOLANA_PLATFORMS = [
    "https://pump.fun",
    "https://dev.fun",
    "https://store.fun",
    "https://bags.fm",
    "https://bonk.fun",
    "https://jupiter.ag",
    "https://birdeye.so",
    "https://raydium.io",
    "https://moltbook.com",
    "https://solana.com/ecosystem"
]

EVM_PLATFORMS = [
    "https://uniswap.org",
    "https://opensea.io",
    "https://etherscan.io",
    "https://basescan.org",
]

SEARCH_PATTERNS = [
    ".fun",
    ".fm",
    "agent marketplace",
    "AI agent platform",
    "agent skills",
    "solana agent",
    "EVM agent"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformCrawler:
    """
    Autonomous web crawler for discovering agent platforms and DEXs.
    
    Targets:
    - Every .fun and .fm domain
    - Agent marketplaces (dev.fun, store.fun, bags.fm)
    - DEXs (pump.fun, Jupiter, Raydium, Uniswap)
    - Blockchain explorers
    - Skill registries
    
    Output:
    - discoveries.md (new platforms found)
    - threat-db.md (security scoring results)
    """
    
    def __init__(self, data_dir: str = "./data", log_dir: str = "./logs"):
        self.data_dir = data_dir
        self.log_dir = log_dir
        self.discovered_platforms = []
        self.session_start = datetime.now()
    
    async def crawl_platform(self, url: str, browser) -> Optional[Dict]:
        """
        Crawl single platform, extract metadata, score security.
        """
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Extract metadata
            title = await page.title()
            description = await page.evaluate(
                "() => document.querySelector('meta[name=\"description\"]')?.content"
            )
            
            # Check for common elements
            has_wallet_connect = await page.evaluate(
                "() => !!document.querySelector('[data-testid*=\"wallet\"], .wallet-adapter-button')"
            )
            
            # Extract links
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href.startsWith('http'))
            """)
            
            # Check for blockchain integrations
            has_solana = "solana" in (await page.content()).lower()
            has_ethereum = "ethereum" in (await page.content()).lower()
            
            platform_data = {
                "url": url,
                "title": title,
                "description": description,
                "has_wallet_connect": has_wallet_connect,
                "chains": [],
                "links": links[:50],  # Limit to first 50 links
                "crawled_at": datetime.now().isoformat(),
                "category": self._categorize_platform(url, await page.content())
            }
            
            if has_solana:
                platform_data["chains"].append("solana")
            if has_ethereum:
                platform_data["chains"].append("ethereum")
            
            await page.close()
            
            logger.info(f"✓ Crawled: {url} - {title}")
            return platform_data
            
        except Exception as e:
            logger.error(f"✗ Failed to crawl {url}: {e}")
            return None
    
    def _categorize_platform(self, url: str, content: str) -> str:
        """
        Categorize platform based on URL and content.
        """
        content_lower = content.lower()
        
        if "pump" in url or "token launch" in content_lower:
            return "token-launchpad"
        elif "dex" in content_lower or "swap" in content_lower:
            return "dex"
        elif "marketplace" in content_lower or "store" in url:
            return "marketplace"
        elif "agent" in content_lower or "skills" in content_lower:
            return "agent-platform"
        elif "explorer" in url or "scan" in url:
            return "blockchain-explorer"
        else:
            return "unknown"
    
    async def discover_new_platforms(self, browser) -> List[Dict]:
        """
        Search for new .fun and .fm domains via search engines and domain registrars.
        """
        discovered = []
        
        # Search for .fun domains
        search_results = await self._search_domains(".fun")
        discovered.extend(search_results)
        
        # Search for .fm domains
        search_results = await self._search_domains(".fm")
        discovered.extend(search_results)
        
        return discovered
    
    async def _search_domains(self, tld: str) -> List[Dict]:
        """
        Search for domains with specific TLD.
        """
        # TODO: Implement domain search via DNS queries, search engines, or registrar APIs
        # For now, return empty list
        logger.info(f"Searching for {tld} domains...")
        return []
    
    async def run_session(self):
        """
        Run full crawl session.
        """
        logger.info(f"Starting crawl session at {self.session_start}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Crawl known Solana platforms
            logger.info("Crawling Solana platforms...")
            for url in SOLANA_PLATFORMS:
                result = await self.crawl_platform(url, browser)
                if result:
                    self.discovered_platforms.append(result)
                await asyncio.sleep(2)  # Rate limiting
            
            # Crawl known EVM platforms
            logger.info("Crawling EVM platforms...")
            for url in EVM_PLATFORMS:
                result = await self.crawl_platform(url, browser)
                if result:
                    self.discovered_platforms.append(result)
                await asyncio.sleep(2)
            
            # Discover new platforms
            logger.info("Discovering new platforms...")
            new_platforms = await self.discover_new_platforms(browser)
            for platform in new_platforms:
                result = await self.crawl_platform(platform["url"], browser)
                if result:
                    self.discovered_platforms.append(result)
                await asyncio.sleep(2)
            
            await browser.close()
        
        # Save results
        self._save_discoveries()
        
        logger.info(f"Session complete. Discovered {len(self.discovered_platforms)} platforms.")
    
    def _save_discoveries(self):
        """
        Save discovered platforms to JSON and update discoveries.md.
        """
        # Save raw JSON
        session_file = f"{self.data_dir}/session-{self.session_start.strftime('%Y%m%d-%H%M%S')}.json"
        with open(session_file, 'w') as f:
            json.dump({
                "session_start": self.session_start.isoformat(),
                "session_end": datetime.now().isoformat(),
                "platforms_discovered": len(self.discovered_platforms),
                "platforms": self.discovered_platforms
            }, f, indent=2)
        
        logger.info(f"Saved session data to {session_file}")
        
        # Update discoveries.md (will be handled by publisher.py)


async def main():
    """
    Main entry point for crawler.
    """
    crawler = PlatformCrawler()
    await crawler.run_session()


if __name__ == "__main__":
    asyncio.run(main())
