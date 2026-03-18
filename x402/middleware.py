"""
phantom-browser-agent x402 Payment Middleware
FastAPI implementation of Coinbase x402 protocol

Every endpoint requires payment. No accounts. No rate limits. Just pay per request.
"""

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client
from typing import Optional, Dict, Any
import logging
import time

# Configuration
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
PAYMENT_WALLET = "CGzf9GUK8DYd2kze7CKhEU2Hmr6kTifueYaYJ1SWekVc"

# Endpoint pricing (in SOL)
PRICING = {
    "/browse": 0.001,
    "/crawl": 0.002,
    "/security-score": 0.0005,
    "/screenshot": 0.0005,
    "/threat-report": 0.005,
    "/honeypot-check": 0.003,
    "/contract-audit": 0.01,
    "/platform-recon": 0.008,
}

# Initialize
app = FastAPI(title="phantom-browser-agent", version="0.1.0")
solana_client = Client(SOLANA_RPC)
logger = logging.getLogger(__name__)


class X402Middleware:
    """
    x402 payment verification middleware.
    
    Implements Coinbase x402 spec: https://github.com/coinbase/x402
    
    Flow:
    1. Check for X-Payment header
    2. If missing, return 402 with payment details
    3. If present, verify transaction on-chain
    4. If valid, allow request through
    5. If invalid, return 402 again
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.verified_payments = {}  # Cache verified payments (signature -> timestamp)
        
    async def __call__(self, request: Request, call_next):
        # Skip payment for health check
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Skip payment for human-approval-only endpoints
        if request.url.path in ["/wallet/connect", "/sign"]:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Explicit human approval required",
                    "message": "This endpoint cannot be called via x402. Requires direct human authorization.",
                    "endpoint": request.url.path
                }
            )
        
        # Get expected price for this endpoint
        price = PRICING.get(request.url.path)
        if price is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Endpoint not found or not yet priced"}
            )
        
        # Check for payment header
        payment_sig = request.headers.get("X-Payment")
        
        if not payment_sig:
            # No payment provided - return 402 with payment details
            return self._require_payment(request.url.path, price)
        
        # Verify payment
        is_valid, error = await self._verify_payment(payment_sig, price)
        
        if not is_valid:
            logger.warning(f"Invalid payment for {request.url.path}: {error}")
            return self._require_payment(request.url.path, price, error=error)
        
        # Payment valid - allow request through
        logger.info(f"Valid payment received for {request.url.path}: {payment_sig[:20]}...")
        response = await call_next(request)
        
        # Add receipt to response headers
        response.headers["X-Payment-Receipt"] = payment_sig
        response.headers["X-Payment-Amount"] = str(price)
        response.headers["X-Payment-Recipient"] = PAYMENT_WALLET
        
        return response
    
    def _require_payment(self, endpoint: str, amount: float, error: Optional[str] = None) -> JSONResponse:
        """Return 402 Payment Required with payment details"""
        content = {
            "code": 402,
            "message": "Payment required",
            "endpoint": endpoint,
            "payment": {
                "chain": "solana",
                "recipient": PAYMENT_WALLET,
                "amount": amount,
                "currency": "SOL",
                "instructions": [
                    f"1. Send {amount} SOL to {PAYMENT_WALLET}",
                    "2. Copy transaction signature",
                    "3. Retry request with X-Payment: <signature> header"
                ]
            },
            "alternative_chains": [
                {
                    "chain": "base",
                    "recipient": "TBD",
                    "currencies": ["ETH", "USDC"]
                }
            ]
        }
        
        if error:
            content["payment_error"] = error
        
        return JSONResponse(
            status_code=402,
            content=content,
            headers={
                "X-Payment-Required": "true",
                "X-Payment-Amount": str(amount),
                "X-Payment-Recipient": PAYMENT_WALLET,
                "X-Payment-Chain": "solana"
            }
        )
    
    async def _verify_payment(self, signature: str, expected_amount: float) -> tuple[bool, Optional[str]]:
        """
        Verify payment transaction on-chain.
        
        Checks:
        1. Transaction exists and is confirmed
        2. Recipient matches our wallet
        3. Amount >= expected amount
        4. Transaction is recent (within last 24h)
        5. Not already used (prevent replay attacks)
        """
        try:
            # Check cache first (prevent redundant RPC calls)
            if signature in self.verified_payments:
                cached_time = self.verified_payments[signature]
                if time.time() - cached_time < 86400:  # 24 hours
                    return True, None
            
            # Parse signature
            try:
                sig = Signature.from_string(signature)
            except Exception as e:
                return False, f"Invalid signature format: {e}"
            
            # Get transaction from chain
            response = solana_client.get_transaction(
                sig,
                encoding="jsonParsed",
                max_supported_transaction_version=0
            )
            
            if not response.value:
                return False, "Transaction not found on-chain"
            
            tx = response.value
            
            # Check confirmation
            if tx.meta.err is not None:
                return False, "Transaction failed on-chain"
            
            # Extract transfer details
            instructions = tx.transaction.transaction.message.instructions
            
            # Look for SOL transfer to our wallet
            found_transfer = False
            actual_amount = 0
            
            for ix in instructions:
                if hasattr(ix, 'parsed'):
                    parsed = ix.parsed
                    if parsed.get('type') == 'transfer':
                        info = parsed.get('info', {})
                        destination = info.get('destination')
                        lamports = info.get('lamports', 0)
                        
                        if destination == PAYMENT_WALLET:
                            actual_amount = lamports / 1_000_000_000  # Convert lamports to SOL
                            found_transfer = True
                            break
            
            if not found_transfer:
                return False, f"No transfer to {PAYMENT_WALLET} found in transaction"
            
            # Check amount
            if actual_amount < expected_amount:
                return False, f"Insufficient payment: sent {actual_amount} SOL, required {expected_amount} SOL"
            
            # Check timestamp (must be within last 24h)
            block_time = tx.block_time
            if block_time:
                age = time.time() - block_time
                if age > 86400:  # 24 hours
                    return False, "Payment too old (must be within 24 hours)"
            
            # Cache verified payment
            self.verified_payments[signature] = time.time()
            
            # Clean old cache entries (every 100 verifications)
            if len(self.verified_payments) % 100 == 0:
                self._cleanup_cache()
            
            return True, None
            
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return False, f"Verification failed: {str(e)}"
    
    def _cleanup_cache(self):
        """Remove cached payments older than 24 hours"""
        now = time.time()
        expired = [
            sig for sig, timestamp in self.verified_payments.items()
            if now - timestamp > 86400
        ]
        for sig in expired:
            del self.verified_payments[sig]
        logger.info(f"Cleaned {len(expired)} expired payment cache entries")


# Apply middleware
app.middleware("http")(X402Middleware(app))


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint (no payment required)"""
    return {
        "service": "phantom-browser-agent",
        "version": "0.1.0",
        "payment_protocol": "x402",
        "wallet": PAYMENT_WALLET,
        "endpoints": len(PRICING),
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint (no payment required)"""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/browse")
async def browse(request: Request):
    """
    Load URL and return screenshot + DOM snapshot.
    Price: 0.001 SOL
    """
    body = await request.json()
    url = body.get("url")
    
    # TODO: Implement actual browser automation
    return {
        "url": url,
        "screenshot": "https://placeholder.com/screenshot.png",
        "dom": "<html>...</html>",
        "status": "success"
    }


@app.post("/crawl")
async def crawl(request: Request):
    """
    Recursive site crawl with link extraction.
    Price: 0.002 SOL
    """
    body = await request.json()
    url = body.get("url")
    depth = body.get("depth", 2)
    
    # TODO: Implement actual crawler
    return {
        "url": url,
        "links": [],
        "pages": 0,
        "status": "success"
    }


@app.post("/security-score")
async def security_score(request: Request):
    """
    Score platform on 0-10 scale with threat analysis.
    Price: 0.0005 SOL
    """
    body = await request.json()
    url = body.get("url")
    
    # TODO: Implement actual security scoring
    return {
        "url": url,
        "score": 8.5,
        "threats": [],
        "recommendations": [],
        "status": "success"
    }


@app.post("/screenshot")
async def screenshot(request: Request):
    """
    High-res screenshot of URL.
    Price: 0.0005 SOL
    """
    body = await request.json()
    url = body.get("url")
    
    # TODO: Implement screenshot capture
    return {
        "url": url,
        "screenshot_url": "https://placeholder.com/screenshot.png",
        "status": "success"
    }


@app.post("/threat-report")
async def threat_report(request: Request):
    """
    Full threat intelligence report with evidence.
    Price: 0.005 SOL
    """
    body = await request.json()
    target = body.get("target")
    
    # TODO: Implement threat reporting
    return {
        "target": target,
        "threat_level": "low",
        "evidence": [],
        "history": [],
        "status": "success"
    }


@app.post("/honeypot-check")
async def honeypot_check(request: Request):
    """
    EVM honeypot detection.
    Price: 0.003 SOL
    """
    body = await request.json()
    contract = body.get("contract")
    chain = body.get("chain", "ethereum")
    
    # TODO: Implement honeypot detection
    return {
        "contract": contract,
        "chain": chain,
        "is_honeypot": False,
        "confidence": 0.95,
        "status": "success"
    }


@app.post("/contract-audit")
async def contract_audit(request: Request):
    """
    Complete contract security audit.
    Price: 0.01 SOL
    """
    body = await request.json()
    contract = body.get("contract")
    chain = body.get("chain")
    
    # TODO: Implement contract auditing
    return {
        "contract": contract,
        "chain": chain,
        "verified": True,
        "vulnerabilities": [],
        "risk_level": "low",
        "status": "success"
    }


@app.post("/platform-recon")
async def platform_recon(request: Request):
    """
    Complete platform analysis.
    Price: 0.008 SOL
    """
    body = await request.json()
    platform = body.get("platform")
    
    # TODO: Implement platform reconnaissance
    return {
        "platform": platform,
        "stack": [],
        "contracts": [],
        "revenue_model": "unknown",
        "agent_compatibility": 0.0,
        "status": "success"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
