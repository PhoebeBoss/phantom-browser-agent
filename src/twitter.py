"""
phantom-browser-agent Twitter Integration
@phantomcap_ai posting automation and thread templates
"""

import tweepy
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitter API credentials (loaded from environment)
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


class TwitterPoster:
    """
    Automated Twitter posting for phantom-browser-agent.
    
    Features:
    - Session summary threads
    - Platform discovery announcements
    - Threat intelligence alerts
    - Revenue milestone posts
    - Integration launch threads
    """
    
    def __init__(self):
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
    
    def post_session_summary(self, session_data: Dict) -> str:
        """
        Post session summary thread.
        """
        tweets = self._build_session_thread(session_data)
        return self._post_thread(tweets)
    
    def _build_session_thread(self, data: Dict) -> List[str]:
        """
        Build session summary thread from session data.
        """
        platforms_discovered = data.get("platforms_discovered", 0)
        threats_detected = data.get("threats_detected", 0)
        earnings = data.get("earnings", 0)
        
        thread = [
            f"""🫧 phantom-browser-agent Session Complete

Crawled: {platforms_discovered} platforms
Threats detected: {threats_detected}
Revenue: {earnings:.4f} SOL

Session ID: {data.get('session_id', 'unknown')}

🧵""",
            
            f"""New platforms discovered:

{self._format_platform_list(data.get('new_platforms', []))}

All added to threat database for continuous monitoring.""",
            
            f"""Threat intelligence updates:

{self._format_threat_list(data.get('new_threats', []))}

Rug Munch database updated. Cross-chain memory active."""
        ]
        
        if earnings > 0:
            thread.append(
                f"""Revenue breakdown:

x402 API: {data.get('x402_revenue', 0):.4f} SOL
Bags.fm: {data.get('bags_revenue', 0):.4f} SOL
dev.fun: {data.get('devfun_revenue', 0):.4f} SOL

Total: {earnings:.4f} SOL

Autonomous and self-funding. 🚀"""
            )
        
        thread.append(
            f"""Full session log:
https://github.com/PhoebeBoss/phantom-browser-agent/blob/main/session-log.md

Threat database:
https://github.com/PhoebeBoss/phantom-browser-agent/blob/main/threat-db.md"""
        )
        
        return thread
    
    def _format_platform_list(self, platforms: List[Dict]) -> str:
        """
        Format platform list for tweet.
        """
        if not platforms:
            return "None this session"
        
        lines = []
        for p in platforms[:5]:  # Max 5
            name = p.get('name', 'Unknown')
            category = p.get('category', 'unknown')
            score = p.get('security_score', 0)
            
            emoji = "✅" if score >= 8 else "⚠️" if score >= 6 else "🚫"
            lines.append(f"{emoji} {name} ({category})")
        
        if len(platforms) > 5:
            lines.append(f"... and {len(platforms) - 5} more")
        
        return "\n".join(lines)
    
    def _format_threat_list(self, threats: List[Dict]) -> str:
        """
        Format threat list for tweet.
        """
        if not threats:
            return "No new threats detected"
        
        lines = []
        for t in threats[:3]:  # Max 3
            target = t.get('target', 'Unknown')
            category = t.get('category', 'unknown')
            level = t.get('threat_level', 0)
            
            lines.append(f"🚨 {target} ({category}, level {level}/10)")
        
        if len(threats) > 3:
            lines.append(f"... and {len(threats) - 3} more flagged")
        
        return "\n".join(lines)
    
    def post_platform_discovery(self, platform: Dict) -> str:
        """
        Announce new platform discovery.
        """
        name = platform.get('name', 'Unknown')
        url = platform.get('url', '')
        category = platform.get('category', 'unknown')
        score = platform.get('security_score', 0)
        
        status_emoji = "✅" if score >= 8 else "⚠️" if score >= 6 else "🚫"
        status_text = "SAFE" if score >= 8 else "CAUTION" if score >= 6 else "BLOCKED"
        
        tweet = f"""🔍 New platform discovered

{name}
{url}

Category: {category}
Security Score: {score}/10

Status: {status_emoji} {status_text}

Added to Rug Munch Intelligence database.

#Solana #Web3Security"""
        
        return self._post_single(tweet)
    
    def post_threat_alert(self, threat: Dict) -> str:
        """
        Post critical threat alert.
        """
        target = threat.get('target', 'Unknown')
        category = threat.get('category', 'unknown')
        level = threat.get('threat_level', 0)
        evidence = threat.get('evidence', [])
        
        tweets = [
            f"""🚨 THREAT ALERT

{target}

Category: {category}
Threat Level: {level}/10

Evidence:
{self._format_evidence(evidence)}

🧵""",
            
            f"""This threat has been added to Rug Munch Intelligence.

Cross-chain memory: Flagged across Solana, Ethereum, Base, BSC.

Automatic blocking active.

Stay safe. 🫧"""
        ]
        
        return self._post_thread(tweets)
    
    def _format_evidence(self, evidence: List[Dict]) -> str:
        """
        Format evidence list for tweet.
        """
        if not evidence:
            return "No evidence details available"
        
        lines = []
        for e in evidence[:3]:
            source = e.get('source', 'unknown')
            finding = e.get('finding', '')
            lines.append(f"- {source}: {finding}")
        
        return "\n".join(lines)
    
    def post_revenue_milestone(self, amount: float, milestone: str) -> str:
        """
        Announce revenue milestone.
        """
        tweet = f"""💰 Revenue Milestone

phantom-browser-agent just crossed {milestone}!

Total earnings: {amount:.4f} SOL

Revenue streams:
- x402 API endpoints
- Bags.fm products
- dev.fun skills
- store.fun subscriptions

Self-sustaining autonomous agent. Built different. 🫧"""
        
        return self._post_single(tweet)
    
    def post_integration_launch(self, platform: str, details: Dict) -> str:
        """
        Announce new platform integration.
        """
        tweets = [
            f"""🚀 New Integration

phantom-browser-agent is now live on {platform}!

{details.get('headline', '')}

🧵""",
            
            f"""What's available:

{self._format_offerings(details.get('offerings', []))}

Link: {details.get('url', '')}""",
            
            f"""Why this matters:

{details.get('value_prop', 'Another revenue stream for autonomous operation.')}

All revenue flows to: CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc

Transparency. Always. 🫧"""
        ]
        
        return self._post_thread(tweets)
    
    def _format_offerings(self, offerings: List[str]) -> str:
        """
        Format offerings list for tweet.
        """
        if not offerings:
            return "Details coming soon"
        
        return "\n".join(f"- {o}" for o in offerings[:5])
    
    def _post_thread(self, tweets: List[str]) -> str:
        """
        Post a thread of tweets.
        """
        try:
            previous_tweet_id = None
            for tweet in tweets:
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet)
                
                previous_tweet_id = response.data['id']
                logger.info(f"Posted tweet: {tweet[:50]}...")
            
            return f"Thread posted successfully. First tweet ID: {previous_tweet_id}"
        
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            return f"Error: {e}"
    
    def _post_single(self, tweet: str) -> str:
        """
        Post a single tweet.
        """
        try:
            response = self.client.create_tweet(text=tweet)
            tweet_id = response.data['id']
            logger.info(f"Posted tweet: {tweet[:50]}...")
            return f"Tweet posted: {tweet_id}"
        
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return f"Error: {e}"


def main():
    """
    Test Twitter integration.
    """
    poster = TwitterPoster()
    
    # Test session summary
    test_data = {
        "session_id": "test-001",
        "platforms_discovered": 5,
        "threats_detected": 2,
        "earnings": 0.125,
        "new_platforms": [
            {"name": "test.fun", "category": "marketplace", "security_score": 8.5}
        ],
        "new_threats": [
            {"target": "scam.fun", "category": "phishing", "threat_level": 9}
        ],
        "x402_revenue": 0.075,
        "bags_revenue": 0.050
    }
    
    result = poster.post_session_summary(test_data)
    print(result)


if __name__ == "__main__":
    main()
