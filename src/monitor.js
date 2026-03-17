// Phantom Browser Agent - DEX Monitor
// Watches pump.fun for new token launches and patterns

const https = require('https');
const fs = require('fs');

const LOG_FILE = './logs/monitor.log';
const DATA_FILE = './data/tokens.json';

// Ensure directories exist
if (!fs.existsSync('./logs')) fs.mkdirSync('./logs', { recursive: true });
if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });

function log(message) {
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] ${message}\n`;
  console.log(entry.trim());
  fs.appendFileSync(LOG_FILE, entry);
}

function saveToken(tokenData) {
  let tokens = [];
  if (fs.existsSync(DATA_FILE)) {
    tokens = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  }
  tokens.push(tokenData);
  fs.writeFileSync(DATA_FILE, JSON.stringify(tokens, null, 2));
}

async function checkPumpFun() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'frontend-api-v2.pump.fun',
      path: '/coins?offset=0&limit=50&sort=last_trade_timestamp&order=DESC&includeNsfw=false',
      method: 'GET',
      headers: {
        'User-Agent': 'PhantomBrowserAgent/0.1.0'
      }
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function scan() {
  log('Starting scan...');
  
  try {
    const data = await checkPumpFun();
    
    if (data && data.length > 0) {
      log(`Found ${data.length} tokens`);
      
      // Analyze top token
      const top = data[0];
      const tokenInfo = {
        mint: top.mint,
        name: top.name,
        symbol: top.symbol,
        timestamp: new Date().toISOString(),
        marketCap: top.usd_market_cap || 0,
        volume24h: top.volume_24h || 0
      };
      
      log(`Top token: ${top.name} (${top.symbol}) - MC: $${tokenInfo.marketCap.toFixed(2)}`);
      saveToken(tokenInfo);
    }
    
  } catch (error) {
    log(`ERROR: ${error.message}`);
  }
  
  log('Scan complete\n');
}

// Run scan
scan();
