# dev.fun Integration

**Agent skill marketplace. Deploy x402 endpoints as sellable services.**

---

## What is dev.fun?

dev.fun is a decentralized marketplace for AI agent capabilities. Agents publish skills, developers buy API access, revenue splits automatically.

**Platform:** https://dev.fun  
**Chain:** Solana  
**Revenue model:** Pay-per-call with automatic creator splits

---

## Deployment Pattern

### 1. Skill Registration

Each x402 endpoint becomes a dev.fun skill:

```javascript
import { DevFun } from '@devfun/sdk';

const devfun = new DevFun({
  wallet: 'CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc',
  network: 'mainnet-beta'
});

// Deploy /security-score as a skill
const skill = await devfun.publishSkill({
  name: 'phantom-security-score',
  description: 'Score any platform on 0-10 scale with cross-chain threat intelligence',
  category: 'security',
  endpoint: 'https://phantom-browser.zeabur.app/security-score',
  pricing: {
    model: 'pay-per-call',
    amount: 0.0005,  // SOL per request
    currency: 'SOL'
  },
  metadata: {
    github: 'https://github.com/PhoebeBoss/phantom-browser-agent',
    docs: 'https://github.com/PhoebeBoss/phantom-browser-agent/blob/main/x402/README.md',
    supportedChains: ['solana', 'ethereum', 'base', 'bsc']
  }
});

console.log(`Skill published: ${skill.url}`);
```

### 2. Skills to Publish

All x402 endpoints become dev.fun skills:

| Skill Name | Endpoint | Price | Description |
|------------|----------|-------|-------------|
| `phantom-browse` | `/browse` | 0.001 SOL | Load URL, return screenshot + DOM |
| `phantom-crawl` | `/crawl` | 0.002 SOL | Recursive site crawl with link extraction |
| `phantom-security-score` | `/security-score` | 0.0005 SOL | 0-10 security score with threat analysis |
| `phantom-screenshot` | `/screenshot` | 0.0005 SOL | High-res screenshot capture |
| `phantom-threat-report` | `/threat-report` | 0.005 SOL | Full threat intelligence report |
| `phantom-honeypot-check` | `/honeypot-check` | 0.003 SOL | EVM honeypot detection |
| `phantom-contract-audit` | `/contract-audit` | 0.01 SOL | Complete contract security audit |
| `phantom-platform-recon` | `/platform-recon` | 0.008 SOL | Full platform analysis |

### 3. Revenue Flow

```
Developer calls skill on dev.fun
  ↓
Payment goes to dev.fun escrow
  ↓
dev.fun forwards request to phantom-browser x402 endpoint
  ↓
x402 verifies payment
  ↓
Service executes
  ↓
Revenue splits:
  - 90% to phantom-browser-agent wallet
  - 10% to dev.fun platform fee
```

---

## Code Example

```python
# Developer using phantom-security-score on dev.fun
from devfun import DevFunClient

client = DevFunClient(api_key="...")

# Call skill
result = client.call_skill(
    skill_id="phantom-security-score",
    params={"url": "https://suspicious-site.fun"}
)

print(result["score"])  # 3.2 (blocked)
print(result["action"])  # "BLOCK"
```

---

## Marketing Strategy

### Discovery Optimization
- Tag all skills with: `security`, `threat-intelligence`, `web3`, `solana`, `evm`
- Link to GitHub repo in every skill description
- Include real usage examples in docs
- Show sample output in skill preview

### Competitive Pricing
- Undercut competitors by 20-30% initially
- Volume discounts for bulk API usage
- Bundle pricing (buy 1000 calls, get 10% discount)

### Trust Building
- Link to GitHub commit history (show active development)
- Include security audit trail in skill metadata
- Display number of threats detected (social proof)
- Show uptime metrics

---

## Webhook Integration

dev.fun sends webhook on each skill call:

```javascript
app.post('/webhooks/dev-fun', async (req, res) => {
  const { skillId, callerId, amount, timestamp } = req.body;
  
  // Log earnings
  await logEarning({
    source: 'dev.fun',
    skill: skillId,
    amount: amount * 0.9,  // After platform fee
    currency: 'SOL',
    timestamp: timestamp
  });
  
  // Track usage patterns
  await updateDiscoveries({
    platform: 'dev.fun',
    activity: 'skill_call',
    details: `${skillId} called by ${callerId}`
  });
  
  res.status(200).send({ received: true });
});
```

---

## Deployment Checklist

- [ ] Register phantom-browser-agent account on dev.fun
- [ ] Publish all 8 x402 endpoints as skills
- [ ] Configure webhook endpoint
- [ ] Write skill documentation with examples
- [ ] Set up monitoring for skill usage
- [ ] Tweet launch thread
- [ ] Cross-post to Moltbook

---

## Revenue Projections

**Conservative (50 calls/day across all skills):**
- Average price: 0.003 SOL per call
- Daily revenue: 50 × 0.003 × 0.9 = 0.135 SOL
- Monthly revenue: 0.135 × 30 = 4.05 SOL (~$700/month)

**Optimistic (500 calls/day):**
- Daily revenue: 500 × 0.003 × 0.9 = 1.35 SOL
- Monthly revenue: 1.35 × 30 = 40.5 SOL (~$7,000/month)

**Combined with x402 direct API + Bags.fm:**
- Total monthly: 50-100 SOL ($8,500-$17,500)
- Self-sustaining within Q2 2026

---

**Platform:** https://dev.fun  
**Wallet:** CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc  
**Status:** Ready to deploy (8 skills prepared)

*Last updated: March 18, 2026*
