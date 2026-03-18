# x402 Payment Layer

**Every capability is a paid endpoint. You decide what you're worth.**

---

## What is x402?

x402 is a universal HTTP payment protocol created by Coinbase. Instead of API keys or OAuth, services accept micropayments as authentication. Pay per request, no subscriptions, no rate limits.

**Spec:** https://github.com/coinbase/x402

phantom-browser-agent implements x402 natively. Every endpoint accepts SOL payments on Solana and ETH/USDC payments on Base.

---

## Payment Flow

1. Client makes request to any endpoint
2. Server responds with `402 Payment Required` + payment details
3. Client signs transaction and includes signature in `X-Payment` header
4. Server verifies payment and processes request
5. Response includes receipt for accounting

**No upfront accounts. No credit cards. No subscription tiers. Just pay per use.**

---

## Endpoint Pricing

All prices in SOL (Solana) or equivalent in ETH/USDC (Base):

### Security & Intelligence
- `POST /security-score` → **0.0005 SOL**
  - Score any platform (website, contract, token) on 0-10 scale
  - Returns detailed threat analysis with cross-chain memory
  
- `POST /threat-report` → **0.005 SOL**
  - Full threat intelligence report with evidence citations
  - Historical data across all chains
  
- `POST /honeypot-check` → **0.003 SOL**
  - EVM honeypot detection via honeypot.is integration
  - Contract analysis with transfer tax and blacklist detection
  
- `POST /contract-audit` → **0.01 SOL**
  - Complete contract security audit
  - Verification status, dangerous functions, historical exploits

### Browser Automation
- `POST /browse` → **0.001 SOL**
  - Load any URL, return screenshot + DOM snapshot
  - Headless Chromium with Phantom/MetaMask extensions loaded
  
- `POST /crawl` → **0.002 SOL**
  - Recursive site crawl with link extraction
  - Platform discovery and categorization
  
- `POST /screenshot` → **0.0005 SOL**
  - High-res screenshot of any URL
  - Custom viewport and wait conditions

### Platform Intelligence
- `POST /platform-recon` → **0.008 SOL**
  - Complete platform analysis (stack, contracts, APIs, revenue model)
  - Agent marketplace compatibility scoring
  - Integration difficulty assessment

### Wallet Operations (Human Approval Required)
- `POST /wallet/connect` → **Explicit approval only**
  - Connect wallet to platform (never automatic)
  - Returns connection status and permissions granted
  
- `POST /sign` → **Explicit approval only**
  - Sign transaction (never automatic)
  - Returns signed transaction for broadcast

---

## Payment Addresses

### Solana (Primary)
**Wallet:** `CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc`

### Base (EVM)
**Wallet:** TBD (to be confirmed once Base wallet deployed)

---

## Dynamic Pricing

As phantom-browser-agent learns new capabilities, new endpoints are added automatically with appropriate pricing. Endpoint list expands over time as the system evolves.

**Current endpoint count:** 8 paid + 2 human-approval-only

---

## Integration Examples

### Python
```python
import requests
from solders.keypair import Keypair
from solders.transaction import Transaction

# 1. Request endpoint
response = requests.post("https://phantom-browser.zeabur.app/security-score", 
    json={"url": "https://example.fun"}
)

# 2. Get payment details from 402 response
payment_details = response.json()
amount = payment_details["amount"]  # 0.0005 SOL
recipient = payment_details["recipient"]

# 3. Sign payment transaction
keypair = Keypair.from_seed(your_private_key)
tx = create_payment_transaction(amount, recipient)
signed_tx = keypair.sign(tx)

# 4. Retry with payment proof
response = requests.post("https://phantom-browser.zeabur.app/security-score",
    json={"url": "https://example.fun"},
    headers={"X-Payment": signed_tx.to_base64()}
)

# 5. Get result
result = response.json()
print(result["score"])  # 7.2
```

### JavaScript
```javascript
import { Connection, PublicKey, Transaction } from '@solana/web3.js';

// 1. Request endpoint
const response = await fetch('https://phantom-browser.zeabur.app/security-score', {
  method: 'POST',
  body: JSON.stringify({ url: 'https://example.fun' })
});

// 2. Get payment details
const payment = await response.json();

// 3. Sign and send payment
const connection = new Connection('https://api.mainnet-beta.solana.com');
const tx = new Transaction().add(/* payment instruction */);
const signature = await wallet.signTransaction(tx);

// 4. Retry with proof
const result = await fetch('https://phantom-browser.zeabur.app/security-score', {
  method: 'POST',
  headers: { 'X-Payment': signature },
  body: JSON.stringify({ url: 'https://example.fun' })
});

console.log(await result.json());
```

### cURL
```bash
# 1. Get payment details
curl -X POST https://phantom-browser.zeabur.app/security-score \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.fun"}'

# Returns 402 with payment address and amount

# 2. Pay via CLI (using Solana CLI)
solana transfer CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc 0.0005

# 3. Retry with signature
curl -X POST https://phantom-browser.zeabur.app/security-score \
  -H "Content-Type: application/json" \
  -H "X-Payment: <transaction_signature>" \
  -d '{"url": "https://example.fun"}'
```

---

## Revenue Model

**Break-even:** 120 API calls per day at 0.001 SOL average = $10/day API costs covered

**Self-sustaining:** When x402 revenue > infrastructure costs, phantom-browser-agent operates autonomously

**Royalties:** 2.5% of all revenue from forks and derivatives flows back via phantom-registry (see LICENSE)

---

## Why x402?

**No accounts.** No sign-ups. No credit cards. No KYC. Just pay per request.

**No rate limits.** Pay more, use more. Scales with your needs.

**No subscriptions.** Only pay for what you actually use.

**Instant settlement.** Payments verify in seconds on Solana, minutes on Base.

**Cross-chain.** Same endpoints accept SOL, ETH, USDC, or any supported token.

**Programmable.** Wallets can auto-approve micropayments under threshold.

---

## Implementation

See `middleware.py` for the FastAPI x402 implementation.

See `integrations/rug-munch.md` for threat intelligence integration details.

---

**Built on:** Coinbase x402 protocol  
**Deployed at:** https://phantom-browser.zeabur.app (pending)  
**Source:** https://github.com/PhoebeBoss/phantom-browser-agent

*Last updated: March 18, 2026*
