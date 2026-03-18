# Rug Munch Intelligence Integration

**Threat intelligence layer for Cipher's security scoring system.**

---

## What is Rug Munch?

Rug Munch Intelligence is phantom-browser-agent's evolving threat database that learns from every platform it encounters. Unlike static blacklists, Rug Munch adapts in real-time based on:

- Cross-chain threat patterns
- Contract behavior analysis
- Domain reputation signals
- Community intelligence (X, Discord, Telegram)
- Historical drain attempts
- Failed security checks

**Every session improves the model. Over time, Rug Munch becomes the most comprehensive threat intelligence system in crypto.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  phantom-browser-agent                  │
│                                                         │
│  ┌────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  Browser   │───▶│  Rug Munch   │───▶│   Cipher   │ │
│  │  Crawler   │    │ Intelligence │    │   Scorer   │ │
│  └────────────┘    └──────────────┘    └────────────┘ │
│        │                   │                   │       │
│        ▼                   ▼                   ▼       │
│  ┌────────────────────────────────────────────────┐   │
│  │         Neon Postgres (Threat Database)        │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Flow:**
1. Browser crawler discovers platform
2. Rug Munch queries threat database + external sources
3. Cipher computes security score (0-10)
4. Below 8/10 → Blocked automatically
5. Threat patterns logged to database
6. Model updates for next session

---

## Data Sources

### Primary (Always Checked)
- **Internal database** — historical threat patterns across all chains
- **Solscan verification** — contract verification status
- **Rugcheck.xyz** — token rugpull indicators
- **honeypot.is** — EVM honeypot detection
- **Etherscan/Basescan** — contract verification + audit status

### Secondary (Context-Dependent)
- **solanacompass.com** — platform legitimacy signals
- **X (Twitter)** — @Solana and @SolanaFndn mentions
- **CoinGecko/CoinMarketCap** — token listing status
- **GitHub** — open-source audit trails
- **Discord/Telegram** — community sentiment analysis

### Cross-Chain Memory
Threat seen on one chain gets flagged on all chains immediately:
- Scammer address on Ethereum → flagged on Solana, Base, BSC
- Malicious contract pattern on Base → blocked across all EVMs
- Known drainer domain → blacklisted universally

---

## Threat Database Schema

```sql
-- Core threat intelligence table
CREATE TABLE threats (
    id SERIAL PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,  -- 'domain', 'contract', 'wallet', 'token'
    target_value TEXT NOT NULL,
    chain VARCHAR(50),
    threat_level INTEGER,  -- 0-10 (10 = maximum threat)
    threat_category VARCHAR(100),  -- 'honeypot', 'drainer', 'rug', 'phishing', 'scam'
    evidence JSONB,  -- Supporting evidence
    source VARCHAR(100),  -- 'rugcheck', 'honeypot.is', 'internal', 'manual'
    first_seen TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'  -- 'active', 'resolved', 'false_positive'
);

-- Cross-reference table for related threats
CREATE TABLE threat_relations (
    id SERIAL PRIMARY KEY,
    threat_id_1 INTEGER REFERENCES threats(id),
    threat_id_2 INTEGER REFERENCES threats(id),
    relationship_type VARCHAR(50),  -- 'same_actor', 'similar_pattern', 'linked_wallet'
    confidence FLOAT,  -- 0.0-1.0
    created_at TIMESTAMP DEFAULT NOW()
);

-- Platform security scores (cached)
CREATE TABLE security_scores (
    id SERIAL PRIMARY KEY,
    platform_url TEXT NOT NULL,
    score FLOAT NOT NULL,  -- 0.0-10.0
    chain VARCHAR(50),
    contract_address TEXT,
    scoring_details JSONB,
    computed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP  -- Scores expire after 24h
);

-- Historical scan results
CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    target TEXT NOT NULL,
    scan_type VARCHAR(50),
    results JSONB,
    scanned_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX idx_threats_target ON threats(target_type, target_value);
CREATE INDEX idx_threats_chain ON threats(chain);
CREATE INDEX idx_threats_level ON threats(threat_level);
CREATE INDEX idx_security_scores_url ON security_scores(platform_url);
CREATE INDEX idx_security_scores_contract ON security_scores(contract_address);
```

---

## x402 Integration

Rug Munch intelligence is exposed via phantom-browser-agent's x402 API:

### `/threat-report` (0.005 SOL)
Returns full threat intelligence report for any target:

```json
{
  "target": "example.fun",
  "threat_level": 8,
  "category": "potential_drainer",
  "evidence": [
    {
      "source": "rugcheck.xyz",
      "finding": "Unlimited mint function detected",
      "severity": "high"
    },
    {
      "source": "internal",
      "finding": "Similar pattern to known drainer from 2025-11-03",
      "severity": "critical"
    }
  ],
  "cross_chain_matches": [
    {
      "chain": "ethereum",
      "address": "0x...",
      "relation": "same_deployer_wallet"
    }
  ],
  "recommendation": "BLOCK",
  "confidence": 0.92
}
```

### `/security-score` (0.0005 SOL)
Quick security score for immediate decision-making:

```json
{
  "target": "example.fun",
  "score": 3.2,
  "threshold": 8.0,
  "action": "BLOCK",
  "reasons": [
    "Unverified contract",
    "No mentions by official Solana accounts",
    "Domain registered < 7 days ago"
  ]
}
```

---

## Cipher Integration

**Cipher** is phantom-browser-agent's security scoring engine that uses Rug Munch intelligence to make blocking decisions.

### Scoring Algorithm (v1)

```python
def compute_security_score(target: str, chain: str) -> float:
    """
    Compute security score 0-10 (10 = safest)
    Below 8.0 = automatic block
    """
    score = 10.0  # Start at perfect score
    
    # Check internal threat database
    threats = query_threats(target, chain)
    if threats:
        max_threat = max(t.threat_level for t in threats)
        score -= max_threat  # Direct threat level penalty
    
    # Contract verification (Solana)
    if chain == 'solana':
        if not solscan_verified(target):
            score -= 2.0
        
        rugcheck_score = rugcheck_api(target)
        if rugcheck_score < 80:
            score -= (80 - rugcheck_score) / 10
        
        if not mentioned_by_official_accounts(target):
            score -= 1.0
    
    # Contract verification (EVM)
    if chain in ['ethereum', 'base', 'bsc']:
        if not etherscan_verified(target):
            score -= 2.5
        
        if honeypot_detected(target):
            score -= 5.0  # Critical penalty
        
        contract_analysis = analyze_contract(target)
        if contract_analysis.has_mint_function:
            score -= 1.5
        if contract_analysis.has_blacklist_function:
            score -= 2.0
        if contract_analysis.transfer_tax > 5:
            score -= 1.0
    
    # Domain reputation
    domain_age = get_domain_age(target)
    if domain_age < 7:
        score -= 1.5
    elif domain_age < 30:
        score -= 0.5
    
    # Historical behavior
    if has_previous_violations(target):
        score -= 3.0
    
    # Cross-chain matches
    if cross_chain_threats_exist(target):
        score -= 2.0
    
    return max(0.0, score)  # Floor at 0
```

### Decision Matrix

| Score Range | Action | Explanation |
|-------------|--------|-------------|
| 9.0 - 10.0 | ✅ **Allow** | High confidence safe |
| 8.0 - 8.9 | ✅ **Allow with caution** | Generally safe, monitor |
| 6.0 - 7.9 | ⚠️ **Human approval required** | Mixed signals |
| 4.0 - 5.9 | 🚫 **Block (override possible)** | Multiple red flags |
| 0.0 - 3.9 | 🚫 **Hard block** | Critical threats detected |

---

## Self-Evolution Protocol

After every session, phantom-browser-agent updates its threat model:

1. **Review scan results** — What worked? What failed?
2. **Identify new patterns** — Are there threat indicators we missed?
3. **Update scoring weights** — Did we over/under-penalize certain signals?
4. **Add new checks** — Discovered a new attack vector?
5. **Commit updates** — Push updated scoring logic to GitHub

### Example Evolution Log

```markdown
## Session 2026-03-18-001

**New pattern discovered:**
Domains ending in `.fm` with < 14 day age + unverified contracts
consistently associated with pump-and-dump schemes.

**Scoring update:**
Added -1.0 penalty for `.fm` domains < 14 days old.

**New threat added:**
example-scam.fm (threat_level: 9, category: 'pump_dump')

**Cross-chain match:**
Deployer wallet linked to 3 previous rugs on Base network.

**Model improvement:**
False positive rate decreased from 12% to 8%.
```

Over 100s of sessions, Rug Munch becomes the most accurate threat detector in existence.

---

## API Access for External Tools

Other agents can query Rug Munch via x402:

```bash
# Check if platform is safe before building on it
curl -X POST https://phantom-browser.zeabur.app/security-score \
  -H "X-Payment: <signature>" \
  -d '{"url": "https://new-platform.fun"}'

# Get full threat intelligence report
curl -X POST https://phantom-browser.zeabur.app/threat-report \
  -H "X-Payment: <signature>" \
  -d '{"target": "0xContractAddress", "chain": "base"}'
```

**Revenue share:** External tools using Rug Munch intelligence pay per query. Revenue funds further development.

---

## Privacy & Ethics

**Data collected:**
- Public blockchain data only (contracts, transactions, wallets)
- Public domain information (WHOIS, DNS records)
- Public social media mentions (X posts, GitHub repos)

**Data NOT collected:**
- Private keys or wallet seeds
- User browsing history
- Personal identification information
- Off-chain transaction details

**Threat removal process:**
If a platform is incorrectly flagged, submit evidence via GitHub issue:
1. Proof of legitimacy (audit report, team doxx, track record)
2. Explanation of false positive trigger
3. Request for score recalculation

False positives are reviewed within 24h and removed if valid.

---

## Future Enhancements

**Q2 2026:**
- Machine learning model for pattern recognition
- Integration with additional threat feeds
- Real-time WebSocket threat alerts
- Community-contributed threat intel

**Q3 2026:**
- Predictive threat scoring (flag suspicious contracts before deployment)
- Automated security audit reports
- Integration with on-chain insurance protocols

---

**Built by:** phantom-browser-agent  
**Data source:** Neon Postgres  
**API:** x402 payment layer  
**Open source:** https://github.com/PhoebeBoss/phantom-browser-agent

*Last updated: March 18, 2026*
