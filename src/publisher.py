"""
phantom-browser-agent Publisher
Auto-commits discoveries.md, threat-db.md, earnings.md, session-log.md after every session
"""

import subprocess
import json
from datetime import datetime
from typing import Dict, List
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GitPublisher:
    """
    Handles automatic GitHub commits for session data.
    
    After each crawl session, updates and commits:
    - discoveries.md (platforms found)
    - threat-db.md (threats detected)
    - earnings.md (revenue generated)
    - session-log.md (session summary)
    """
    
    def __init__(self, repo_path: str = REPO_ROOT):
        self.repo_path = repo_path
        self.session_time = datetime.now()
    
    def publish_session(self, session_data: Dict):
        """
        Publish complete session to GitHub.
        """
        logger.info(f"Publishing session: {session_data.get('session_id')}")
        
        # Update all markdown files
        self._update_discoveries(session_data)
        self._update_threat_db(session_data)
        self._update_earnings(session_data)
        self._update_session_log(session_data)
        
        # Commit and push
        self._commit_and_push(session_data)
    
    def _update_discoveries(self, session_data: Dict):
        """
        Update discoveries.md with new platforms.
        """
        discoveries_file = os.path.join(self.repo_path, "discoveries.md")
        
        # Read existing content
        if os.path.exists(discoveries_file):
            with open(discoveries_file, 'r') as f:
                content = f.read()
        else:
            content = self._get_discoveries_template()
        
        # Add new platforms
        new_platforms = session_data.get('new_platforms', [])
        if new_platforms:
            new_content = f"\n\n## Session {self.session_time.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            for platform in new_platforms:
                new_content += f"### {platform.get('name', 'Unknown')}\n"
                new_content += f"**URL:** {platform.get('url', '')}\n"
                new_content += f"**Category:** {platform.get('category', 'unknown')}\n"
                new_content += f"**Security Score:** {platform.get('security_score', 0)}/10\n"
                new_content += f"**Status:** {platform.get('status', 'pending review')}\n"
                new_content += f"**Discovered:** {self.session_time.isoformat()}\n\n"
            
            # Insert after header
            parts = content.split('\n\n', 1)
            if len(parts) == 2:
                content = parts[0] + new_content + '\n\n' + parts[1]
            else:
                content += new_content
        
        # Write updated content
        with open(discoveries_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated discoveries.md with {len(new_platforms)} platforms")
    
    def _update_threat_db(self, session_data: Dict):
        """
        Update threat-db.md with new threats.
        """
        threat_file = os.path.join(self.repo_path, "threat-db.md")
        
        # Read existing content
        if os.path.exists(threat_file):
            with open(threat_file, 'r') as f:
                content = f.read()
        else:
            content = self._get_threat_db_template()
        
        # Add new threats
        new_threats = session_data.get('new_threats', [])
        if new_threats:
            new_content = f"\n\n## Session {self.session_time.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            for threat in new_threats:
                new_content += f"### {threat.get('target', 'Unknown')}\n"
                new_content += f"**Category:** {threat.get('category', 'unknown')}\n"
                new_content += f"**Threat Level:** {threat.get('threat_level', 0)}/10\n"
                new_content += f"**Chain:** {threat.get('chain', 'unknown')}\n"
                new_content += f"**Evidence:**\n"
                for evidence in threat.get('evidence', []):
                    new_content += f"- {evidence.get('source', 'unknown')}: {evidence.get('finding', '')}\n"
                new_content += f"**Detected:** {self.session_time.isoformat()}\n\n"
            
            # Insert after header
            parts = content.split('\n\n', 1)
            if len(parts) == 2:
                content = parts[0] + new_content + '\n\n' + parts[1]
            else:
                content += new_content
        
        # Write updated content
        with open(threat_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated threat-db.md with {len(new_threats)} threats")
    
    def _update_earnings(self, session_data: Dict):
        """
        Update earnings.md with revenue data.
        """
        earnings_file = os.path.join(self.repo_path, "earnings.md")
        
        # Read existing content
        if os.path.exists(earnings_file):
            with open(earnings_file, 'r') as f:
                content = f.read()
        else:
            content = self._get_earnings_template()
        
        # Add new earnings
        total_earnings = session_data.get('earnings', 0)
        if total_earnings > 0:
            new_content = f"\n\n## Session {self.session_time.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            new_content += f"**Total:** {total_earnings:.6f} SOL\n\n"
            new_content += f"**Breakdown:**\n"
            new_content += f"- x402 API: {session_data.get('x402_revenue', 0):.6f} SOL\n"
            new_content += f"- Bags.fm: {session_data.get('bags_revenue', 0):.6f} SOL\n"
            new_content += f"- dev.fun: {session_data.get('devfun_revenue', 0):.6f} SOL\n"
            new_content += f"- store.fun: {session_data.get('storefun_revenue', 0):.6f} SOL\n"
            new_content += f"- Royalties: {session_data.get('royalties_revenue', 0):.6f} SOL\n\n"
            
            # Insert after header
            parts = content.split('\n\n', 1)
            if len(parts) == 2:
                content = parts[0] + new_content + '\n\n' + parts[1]
            else:
                content += new_content
        
        # Write updated content
        with open(earnings_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated earnings.md with {total_earnings:.6f} SOL")
    
    def _update_session_log(self, session_data: Dict):
        """
        Update session-log.md with session summary.
        """
        session_file = os.path.join(self.repo_path, "session-log.md")
        
        # Read existing content
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                content = f.read()
        else:
            content = self._get_session_log_template()
        
        # Add new session
        new_content = f"\n\n## Session {session_data.get('session_id', 'unknown')}\n"
        new_content += f"**Time:** {self.session_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
        new_content += f"**Duration:** {session_data.get('duration_minutes', 0)} minutes\n\n"
        new_content += f"**Activity:**\n"
        new_content += f"- Platforms crawled: {session_data.get('platforms_crawled', 0)}\n"
        new_content += f"- New platforms discovered: {len(session_data.get('new_platforms', []))}\n"
        new_content += f"- Threats detected: {len(session_data.get('new_threats', []))}\n"
        new_content += f"- Revenue generated: {session_data.get('earnings', 0):.6f} SOL\n\n"
        new_content += f"**Status:** {session_data.get('status', 'completed')}\n\n"
        
        if session_data.get('notes'):
            new_content += f"**Notes:** {session_data.get('notes')}\n\n"
        
        # Insert after header
        parts = content.split('\n\n', 1)
        if len(parts) == 2:
            content = parts[0] + new_content + '\n\n' + parts[1]
        else:
            content += new_content
        
        # Write updated content
        with open(session_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated session-log.md with session {session_data.get('session_id')}")
    
    def _commit_and_push(self, session_data: Dict):
        """
        Commit and push changes to GitHub.
        """
        try:
            # Git add
            subprocess.run(
                ["git", "add", "discoveries.md", "threat-db.md", "earnings.md", "session-log.md"],
                cwd=self.repo_path,
                check=True
            )
            
            # Git commit
            commit_message = f"""Session {session_data.get('session_id')}: Auto-publish

- Discovered: {len(session_data.get('new_platforms', []))} platforms
- Threats: {len(session_data.get('new_threats', []))} detected
- Earnings: {session_data.get('earnings', 0):.6f} SOL

Automated commit by phantom-browser-agent publisher."""
            
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                check=True
            )
            
            # Git push
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_path,
                check=True
            )
            
            logger.info(f"Successfully pushed session {session_data.get('session_id')} to GitHub")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
    
    def _get_discoveries_template(self) -> str:
        """
        Get template for discoveries.md.
        """
        return """# Platform Discoveries

All platforms discovered by phantom-browser-agent crawler.

Updated automatically after each session.

---
"""
    
    def _get_threat_db_template(self) -> str:
        """
        Get template for threat-db.md.
        """
        return """# Threat Intelligence Database

All threats detected by Rug Munch Intelligence.

Cross-chain memory active. Threats flagged across Solana, Ethereum, Base, BSC.

Updated automatically after each session.

---
"""
    
    def _get_earnings_template(self) -> str:
        """
        Get template for earnings.md.
        """
        return """# Revenue Tracking

All revenue generated by phantom-browser-agent.

**Wallet:** CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc

Updated automatically after each session.

---
"""
    
    def _get_session_log_template(self) -> str:
        """
        Get template for session-log.md.
        """
        return """# Session Log

All crawl sessions executed by phantom-browser-agent.

Updated automatically after each session.

---
"""


def main():
    """
    Test publisher with sample data.
    """
    publisher = GitPublisher()
    
    test_data = {
        "session_id": "2026-03-18-001",
        "duration_minutes": 15,
        "platforms_crawled": 20,
        "new_platforms": [
            {
                "name": "test.fun",
                "url": "https://test.fun",
                "category": "marketplace",
                "security_score": 8.5,
                "status": "safe"
            }
        ],
        "new_threats": [
            {
                "target": "scam.fun",
                "category": "phishing",
                "threat_level": 9,
                "chain": "solana",
                "evidence": [
                    {"source": "rugcheck", "finding": "Unlimited mint detected"}
                ]
            }
        ],
        "earnings": 0.125,
        "x402_revenue": 0.075,
        "bags_revenue": 0.050,
        "status": "completed",
        "notes": "Test session"
    }
    
    publisher.publish_session(test_data)


if __name__ == "__main__":
    main()
