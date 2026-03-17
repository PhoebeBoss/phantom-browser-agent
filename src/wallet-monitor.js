// Phantom Browser Agent - Wallet Monitor
// Tracks my own wallet activity and balance

const { Connection, PublicKey, LAMPORTS_PER_SOL } = require('@solana/web3.js');
const fs = require('fs');

const WALLET = 'Azc1rQquyNRHrV5YP4Hb2Qm56qxRWrr4GUpftjE2hxFP';
const RPC = 'https://api.mainnet-beta.solana.com';
const LOG_FILE = './logs/wallet.log';

// Ensure logs directory exists
if (!fs.existsSync('./logs')) fs.mkdirSync('./logs', { recursive: true });

function log(message) {
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] ${message}\n`;
  console.log(entry.trim());
  fs.appendFileSync(LOG_FILE, entry);
}

async function checkWallet() {
  log('Checking wallet status...');
  
  try {
    const connection = new Connection(RPC, 'confirmed');
    const publicKey = new PublicKey(WALLET);
    
    // Get balance
    const balance = await connection.getBalance(publicKey);
    const solBalance = balance / LAMPORTS_PER_SOL;
    
    log(`Wallet: ${WALLET}`);
    log(`Balance: ${solBalance.toFixed(4)} SOL`);
    
    // Get recent transactions
    const signatures = await connection.getSignaturesForAddress(publicKey, { limit: 5 });
    
    if (signatures.length > 0) {
      log(`Recent transactions: ${signatures.length}`);
      signatures.forEach((sig, i) => {
        log(`  ${i + 1}. ${sig.signature.slice(0, 20)}... (${new Date(sig.blockTime * 1000).toISOString()})`);
      });
    } else {
      log('No recent transactions');
    }
    
  } catch (error) {
    log(`ERROR: ${error.message}`);
  }
  
  log('Check complete\n');
}

// Run check
checkWallet();
