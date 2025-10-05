import React, { useState, useEffect } from 'react';
import { Plus, Wallet, Trash2, RefreshCw, Eye, EyeOff, Building2, Key, AlertTriangle } from 'lucide-react';

const WalletAggregator = () => {
  const [accounts, setAccounts] = useState([]);
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const [loading, setLoading] = useState(false);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [accountType, setAccountType] = useState('wallet'); // 'wallet' or 'exchange'
  const [newAccount, setNewAccount] = useState({ 
    address: '', 
    name: '', 
    chain: 'ethereum',
    exchange: 'coinbase',
    apiKey: '',
    apiSecret: '',
    apiPassphrase: '' // For some exchanges
  });
  const [totalValue, setTotalValue] = useState(0);
  const [hideSmallBalances, setHideSmallBalances] = useState(false);
  const [showApiWarning, setShowApiWarning] = useState(false);

  // Mock data for demonstration
  const mockWalletData = {
    ethereum: {
      native: { symbol: 'ETH', balance: 2.5, price: 2400 },
      tokens: [
        { symbol: 'USDC', balance: 1500, price: 1 },
        { symbol: 'UNI', balance: 100, price: 8.5 },
        { symbol: 'LINK', balance: 50, price: 15 }
      ]
    },
    bitcoin: {
      native: { symbol: 'BTC', balance: 0.15, price: 45000 }
    }
  };

  const mockExchangeData = {
    coinbase: [
      { symbol: 'BTC', balance: 0.25, price: 45000 },
      { symbol: 'ETH', balance: 3.2, price: 2400 },
      { symbol: 'USDC', balance: 5000, price: 1 },
      { symbol: 'SOL', balance: 45, price: 95 }
    ],
    binance: [
      { symbol: 'BTC', balance: 0.1, price: 45000 },
      { symbol: 'ETH', balance: 1.8, price: 2400 },
      { symbol: 'BNB', balance: 15, price: 320 },
      { symbol: 'USDT', balance: 2500, price: 1 }
    ],
    kraken: [
      { symbol: 'BTC', balance: 0.05, price: 45000 },
      { symbol: 'ETH', balance: 0.8, price: 2400 },
      { symbol: 'ADA', balance: 1000, price: 0.45 }
    ]
  };

  const exchangeOptions = [
    { value: 'coinbase', label: 'Coinbase Pro', requiresPassphrase: false },
    { value: 'binance', label: 'Binance', requiresPassphrase: false },
    { value: 'kraken', label: 'Kraken', requiresPassphrase: false },
    { value: 'kucoin', label: 'KuCoin', requiresPassphrase: true },
    { value: 'bybit', label: 'Bybit', requiresPassphrase: false },
    { value: 'okx', label: 'OKX', requiresPassphrase: true },
    { value: 'gateio', label: 'Gate.io', requiresPassphrase: false },
    { value: 'huobi', label: 'Huobi', requiresPassphrase: false }
  ];

  const chainOptions = [
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'bitcoin', label: 'Bitcoin' },
    { value: 'polygon', label: 'Polygon' },
    { value: 'binance-smart-chain', label: 'BSC' },
    { value: 'avalanche', label: 'Avalanche' },
    { value: 'solana', label: 'Solana' },
    { value: 'cardano', label: 'Cardano' }
  ];

  // Load accounts from localStorage
  useEffect(() => {
    const savedAccounts = localStorage.getItem('web3-accounts');
    if (savedAccounts) {
      setAccounts(JSON.parse(savedAccounts));
    }
  }, []);

  // Save accounts to localStorage
  useEffect(() => {
    localStorage.setItem('web3-accounts', JSON.stringify(accounts));
    calculateTotalValue();
  }, [accounts, baseCurrency]);

  const fetchWalletData = async (address, chain) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return mockWalletData[chain] || { native: { symbol: 'ETH', balance: 0, price: 0 }, tokens: [] };
  };

  const fetchExchangeData = async (exchange, apiKey, apiSecret, apiPassphrase) => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    // In production, make actual API calls to exchange
    return mockExchangeData[exchange] || [];
  };

  const convertPrice = (amount, fromSymbol, toCurrency) => {
    const conversionRates = {
      USD: { ETH: 2400, BTC: 45000, SOL: 95, BNB: 320, ADA: 0.45, MATIC: 0.8, USDC: 1, USDT: 1, UNI: 8.5, LINK: 15 },
      EUR: { ETH: 2200, BTC: 41000, SOL: 87, BNB: 292, ADA: 0.41, MATIC: 0.73, USDC: 0.91, USDT: 0.91, UNI: 7.8, LINK: 13.7 },
      BTC: { ETH: 0.053, BTC: 1, SOL: 0.0021, BNB: 0.0071, ADA: 0.00001, MATIC: 0.000018, USDC: 0.000022, USDT: 0.000022, UNI: 0.00019, LINK: 0.00033 },
      ETH: { ETH: 1, BTC: 18.75, SOL: 0.04, BNB: 0.13, ADA: 0.00019, MATIC: 0.00033, USDC: 0.00042, USDT: 0.00042, UNI: 0.0035, LINK: 0.0063 }
    };
    return amount * (conversionRates[toCurrency]?.[fromSymbol] || 0);
  };

  const addAccount = async () => {
    if (accountType === 'wallet' && (!newAccount.address || !newAccount.name)) return;
    if (accountType === 'exchange' && (!newAccount.apiKey || !newAccount.apiSecret || !newAccount.name)) return;
    
    setLoading(true);
    try {
      let accountData;
      let newAccountObj;

      if (accountType === 'wallet') {
        accountData = await fetchWalletData(newAccount.address, newAccount.chain);
        newAccountObj = {
          id: Date.now(),
          type: 'wallet',
          address: newAccount.address,
          name: newAccount.name,
          chain: newAccount.chain,
          data: accountData,
          lastUpdated: new Date().toISOString()
        };
      } else {
        accountData = await fetchExchangeData(newAccount.exchange, newAccount.apiKey, newAccount.apiSecret, newAccount.apiPassphrase);
        newAccountObj = {
          id: Date.now(),
          type: 'exchange',
          exchange: newAccount.exchange,
          name: newAccount.name,
          data: accountData,
          lastUpdated: new Date().toISOString(),
          // Note: In production, encrypt and secure API credentials
          credentials: {
            apiKey: newAccount.apiKey.slice(0, 6) + '...' + newAccount.apiKey.slice(-4), // Store masked version
            hasCredentials: true
          }
        };
      }
      
      setAccounts(prev => [...prev, newAccountObj]);
      setNewAccount({ 
        address: '', 
        name: '', 
        chain: 'ethereum',
        exchange: 'coinbase',
        apiKey: '',
        apiSecret: '',
        apiPassphrase: ''
      });
      setShowAddAccount(false);
      setAccountType('wallet');
    } catch (error) {
      console.error('Error adding account:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeAccount = (id) => {
    setAccounts(prev => prev.filter(a => a.id !== id));
  };

  const refreshAccount = async (id) => {
    setLoading(true);
    try {
      const account = accounts.find(a => a.id === id);
      if (account) {
        let updatedData;
        if (account.type === 'wallet') {
          updatedData = await fetchWalletData(account.address, account.chain);
        } else {
          // In production, decrypt and use stored credentials
          updatedData = await fetchExchangeData(account.exchange, 'stored_api_key', 'stored_api_secret');
        }
        
        setAccounts(prev => prev.map(a => 
          a.id === id 
            ? { ...a, data: updatedData, lastUpdated: new Date().toISOString() }
            : a
        ));
      }
    } catch (error) {
      console.error('Error refreshing account:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotalValue = () => {
    let total = 0;
    accounts.forEach(account => {
      if (account.type === 'wallet') {
        if (account.data?.native) {
          total += convertPrice(account.data.native.balance, account.data.native.symbol, baseCurrency);
        }
        if (account.data?.tokens) {
          account.data.tokens.forEach(token => {
            total += convertPrice(token.balance, token.symbol, baseCurrency);
          });
        }
      } else if (account.type === 'exchange' && Array.isArray(account.data)) {
        account.data.forEach(asset => {
          total += convertPrice(asset.balance, asset.symbol, baseCurrency);
        });
      }
    });
    setTotalValue(total);
  };

  const formatCurrency = (value) => {
    if (baseCurrency === 'BTC') {
      return `₿${value.toFixed(8)}`;
    } else if (baseCurrency === 'ETH') {
      return `Ξ${value.toFixed(6)}`;
    } else if (baseCurrency === 'EUR') {
      return `€${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else {
      return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  };

  const selectedExchange = exchangeOptions.find(ex => ex.value === newAccount.exchange);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Complete Crypto Portfolio</h1>
          <p className="text-slate-300">Track your DeFi wallets and centralized exchange holdings</p>
        </div>

        {/* Controls */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 mb-8 border border-white/20">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <label className="text-white font-medium">Base Currency:</label>
              <select 
                value={baseCurrency}
                onChange={(e) => setBaseCurrency(e.target.value)}
                className="bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="BTC">BTC (₿)</option>
                <option value="ETH">ETH (Ξ)</option>
              </select>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => setHideSmallBalances(!hideSmallBalances)}
                className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors"
              >
                {hideSmallBalances ? <EyeOff size={20} /> : <Eye size={20} />}
                {hideSmallBalances ? 'Show All' : 'Hide Small'}
              </button>
              
              <button
                onClick={() => setShowAddAccount(true)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus size={20} />
                Add Account
              </button>
            </div>
          </div>
        </div>

        {/* Total Portfolio Value */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-8 mb-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Total Portfolio Value</h2>
          <div className="text-4xl font-bold text-white">
            {formatCurrency(totalValue)}
          </div>
          <p className="text-purple-100 mt-2">
            {accounts.filter(a => a.type === 'wallet').length} wallet{accounts.filter(a => a.type === 'wallet').length !== 1 ? 's' : ''} • {' '}
            {accounts.filter(a => a.type === 'exchange').length} exchange{accounts.filter(a => a.type === 'exchange').length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Accounts Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {accounts.map(account => (
            <AccountCard 
              key={account.id}
              account={account}
              baseCurrency={baseCurrency}
              formatCurrency={formatCurrency}
              convertPrice={convertPrice}
              onRemove={() => removeAccount(account.id)}
              onRefresh={() => refreshAccount(account.id)}
              hideSmallBalances={hideSmallBalances}
              loading={loading}
            />
          ))}
        </div>

        {accounts.length === 0 && (
          <div className="text-center py-12">
            <div className="flex justify-center gap-4 mb-4">
              <Wallet size={48} className="text-slate-400" />
              <Building2 size={48} className="text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No Accounts Connected</h3>
            <p className="text-slate-400 mb-6">Add your wallets and exchange accounts to get started</p>
            <button
              onClick={() => setShowAddAccount(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 mx-auto transition-colors"
            >
              <Plus size={20} />
              Add Your First Account
            </button>
          </div>
        )}

        {/* Add Account Modal */}
        {showAddAccount && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-600 max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold text-white mb-4">Add New Account</h3>
              
              {/* Account Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-300 mb-3">Account Type</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setAccountType('wallet')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      accountType === 'wallet'
                        ? 'border-purple-400 bg-purple-400/20 text-white'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <Wallet size={24} className="mx-auto mb-2" />
                    <div className="font-medium">DeFi Wallet</div>
                    <div className="text-xs opacity-80">On-chain address</div>
                  </button>
                  <button
                    onClick={() => {
                      setAccountType('exchange');
                      setShowApiWarning(true);
                    }}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      accountType === 'exchange'
                        ? 'border-purple-400 bg-purple-400/20 text-white'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <Building2 size={24} className="mx-auto mb-2" />
                    <div className="font-medium">Exchange</div>
                    <div className="text-xs opacity-80">CEX API keys</div>
                  </button>
                </div>
              </div>

              {/* API Security Warning */}
              {showApiWarning && accountType === 'exchange' && (
                <div className="mb-4 p-4 bg-amber-500/20 border border-amber-500/30 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertTriangle size={20} className="text-amber-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <div className="text-amber-400 font-medium mb-1">Security Notice</div>
                      <div className="text-amber-200 mb-2">
                        This is a demo. In production, API keys should be:
                      </div>
                      <ul className="text-xs text-amber-200 space-y-1">
                        <li>• Encrypted before storage</li>
                        <li>• Read-only permissions only</li>
                        <li>• Stored securely server-side</li>
                        <li>• Never exposed in client code</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    {accountType === 'wallet' ? 'Wallet' : 'Account'} Name
                  </label>
                  <input
                    type="text"
                    value={newAccount.name}
                    onChange={(e) => setNewAccount(prev => ({ ...prev, name: e.target.value }))}
                    placeholder={accountType === 'wallet' ? 'e.g., Main Wallet' : 'e.g., Trading Account'}
                    className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none"
                  />
                </div>
                
                {accountType === 'wallet' ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Blockchain</label>
                      <select
                        value={newAccount.chain}
                        onChange={(e) => setNewAccount(prev => ({ ...prev, chain: e.target.value }))}
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none"
                      >
                        {chainOptions.map(chain => (
                          <option key={chain.value} value={chain.value}>{chain.label}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Wallet Address</label>
                      <input
                        type="text"
                        value={newAccount.address}
                        onChange={(e) => setNewAccount(prev => ({ ...prev, address: e.target.value }))}
                        placeholder="0x... or bc1... or 3..."
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none font-mono text-sm"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Exchange</label>
                      <select
                        value={newAccount.exchange}
                        onChange={(e) => setNewAccount(prev => ({ ...prev, exchange: e.target.value }))}
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none"
                      >
                        {exchangeOptions.map(exchange => (
                          <option key={exchange.value} value={exchange.value}>{exchange.label}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        <Key size={16} className="inline mr-1" />
                        API Key
                      </label>
                      <input
                        type="password"
                        value={newAccount.apiKey}
                        onChange={(e) => setNewAccount(prev => ({ ...prev, apiKey: e.target.value }))}
                        placeholder="Enter your API key"
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none font-mono text-sm"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        <Key size={16} className="inline mr-1" />
                        API Secret
                      </label>
                      <input
                        type="password"
                        value={newAccount.apiSecret}
                        onChange={(e) => setNewAccount(prev => ({ ...prev, apiSecret: e.target.value }))}
                        placeholder="Enter your API secret"
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none font-mono text-sm"
                      />
                    </div>
                    
                    {selectedExchange?.requiresPassphrase && (
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          <Key size={16} className="inline mr-1" />
                          API Passphrase
                        </label>
                        <input
                          type="password"
                          value={newAccount.apiPassphrase}
                          onChange={(e) => setNewAccount(prev => ({ ...prev, apiPassphrase: e.target.value }))}
                          placeholder="Enter your API passphrase"
                          className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-400 focus:outline-none font-mono text-sm"
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowAddAccount(false);
                    setShowApiWarning(false);
                    setAccountType('wallet');
                  }}
                  className="flex-1 bg-slate-600 hover:bg-slate-700 text-white py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={addAccount}
                  disabled={loading || !newAccount.name || 
                    (accountType === 'wallet' && !newAccount.address) ||
                    (accountType === 'exchange' && (!newAccount.apiKey || !newAccount.apiSecret))}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white py-2 rounded-lg transition-colors"
                >
                  {loading ? 'Adding...' : 'Add Account'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const AccountCard = ({ account, baseCurrency, formatCurrency, convertPrice, onRemove, onRefresh, hideSmallBalances, loading }) => {
  const calculateAccountTotal = () => {
    let total = 0;
    if (account.type === 'wallet') {
      if (account.data?.native) {
        total += convertPrice(account.data.native.balance, account.data.native.symbol, baseCurrency);
      }
      if (account.data?.tokens) {
        account.data.tokens.forEach(token => {
          total += convertPrice(token.balance, token.symbol, baseCurrency);
        });
      }
    } else if (account.type === 'exchange' && Array.isArray(account.data)) {
      account.data.forEach(asset => {
        total += convertPrice(asset.balance, asset.symbol, baseCurrency);
      });
    }
    return total;
  };

  const accountTotal = calculateAccountTotal();
  
  let allAssets = [];
  if (account.type === 'wallet') {
    allAssets = [
      ...(account.data?.native ? [{ ...account.data.native, isNative: true }] : []),
      ...(account.data?.tokens || [])
    ];
  } else if (account.type === 'exchange' && Array.isArray(account.data)) {
    allAssets = account.data;
  }

  const filteredAssets = hideSmallBalances 
    ? allAssets.filter(asset => convertPrice(asset.balance, asset.symbol, baseCurrency) >= 1)
    : allAssets;

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:border-purple-400 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {account.type === 'wallet' ? (
              <Wallet size={16} className="text-purple-400" />
            ) : (
              <Building2 size={16} className="text-green-400" />
            )}
            <h3 className="text-lg font-semibold text-white">{account.name}</h3>
          </div>
          
          {account.type === 'wallet' ? (
            <>
              <p className="text-sm text-slate-400 font-mono">
                {account.address.slice(0, 6)}...{account.address.slice(-4)}
              </p>
              <p className="text-xs text-slate-500 capitalize">{account.chain}</p>
            </>
          ) : (
            <>
              <p className="text-sm text-slate-400 capitalize">{account.exchange}</p>
              <p className="text-xs text-slate-500">API: {account.credentials?.apiKey}</p>
            </>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 text-slate-400 hover:text-white transition-colors disabled:cursor-not-allowed"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={onRemove}
            className="p-2 text-slate-400 hover:text-red-400 transition-colors"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-2xl font-bold text-white">
          {formatCurrency(accountTotal)}
        </div>
        <p className="text-sm text-slate-400">
          Last updated: {new Date(account.lastUpdated).toLocaleTimeString()}
        </p>
      </div>

      <div className="space-y-2">
        {filteredAssets.map((asset, index) => {
          const value = convertPrice(asset.balance, asset.symbol, baseCurrency);
          return (
            <div key={index} className="flex justify-between items-center py-2 px-3 bg-white/5 rounded-lg">
              <div>
                <span className="text-white font-medium">{asset.symbol}</span>
                {asset.isNative && <span className="text-xs text-purple-400 ml-2">Native</span>}
              </div>
              <div className="text-right">
                <div className="text-white font-medium">{asset.balance.toLocaleString()}</div>
                <div className="text-xs text-slate-400">{formatCurrency(value)}</div>
              </div>
            </div>
          );
        })}
      </div>

      {allAssets.length === 0 && (
        <div className="text-center py-4 text-slate-400">
          No assets found
        </div>
      )}
    </div>
  );
};

#export default WalletAggregator;