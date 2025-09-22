import { useState, useEffect } from 'react';
import axios from 'axios';

export default function ConfigForm({ onConfigUpdate }) {
  const [config, setConfig] = useState({
    rpc_url: 'https://rpc.ankr.com/eth',
    private_key: '',
    contract_address: '',
    trade_amount: 0.01,
    min_interval_seconds: 300,
    max_interval_seconds: 1800
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/config');
      if (response.data && !response.data.message) {
        setConfig(prev => ({
          ...prev,
          contract_address: response.data.contract_address || '',
          trade_amount: response.data.trade_amount || 0.01,
          min_interval_seconds: response.data.min_interval_seconds || 300,
          max_interval_seconds: response.data.max_interval_seconds || 1800
        }));
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await axios.post('/api/config', config);
      if (response.data.success) {
        alert('Configuration saved successfully!');
        if (onConfigUpdate) {
          await onConfigUpdate();
        }
      } else {
        alert('Failed to save configuration');
      }
    } catch (error) {
      alert('Error saving configuration: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  if (loading) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Bot Configuration</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* RPC URL */}
        <div>
          <label className="label">RPC URL</label>
          <input
            type="url"
            name="rpc_url"
            value={config.rpc_url}
            onChange={handleInputChange}
            className="input-field"
            placeholder="https://rpc.ankr.com/eth"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Ethereum RPC endpoint for blockchain interaction
          </p>
        </div>

        {/* Private Key */}
        <div>
          <label className="label">Private Key</label>
          <input
            type="password"
            name="private_key"
            value={config.private_key}
            onChange={handleInputChange}
            className="input-field"
            placeholder="0x..."
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Private key of the wallet to use for trading (starts with 0x)
          </p>
        </div>

        {/* Contract Address */}
        <div>
          <label className="label">Contract Address</label>
          <input
            type="text"
            name="contract_address"
            value={config.contract_address}
            onChange={handleInputChange}
            className="input-field"
            placeholder="0x..."
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            ERC-20 token contract address to trade (starts with 0x)
          </p>
        </div>

        {/* Trade Amount */}
        <div>
          <label className="label">Trade Amount</label>
          <input
            type="number"
            name="trade_amount"
            value={config.trade_amount}
            onChange={handleInputChange}
            className="input-field"
            step="0.000001"
            min="0.000001"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Amount of tokens to trade in each transaction
          </p>
        </div>

        {/* Time Intervals */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label">Min Interval (seconds)</label>
            <input
              type="number"
              name="min_interval_seconds"
              value={config.min_interval_seconds}
              onChange={handleInputChange}
              className="input-field"
              min="60"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Minimum time between trades
            </p>
          </div>

          <div>
            <label className="label">Max Interval (seconds)</label>
            <input
              type="number"
              name="max_interval_seconds"
              value={config.max_interval_seconds}
              onChange={handleInputChange}
              className="input-field"
              min="60"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum time between trades
            </p>
          </div>
        </div>

        {/* Security Warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Security Notice</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  Never share your private key with anyone. This bot will use your private key to execute trades.
                  Make sure you're using a dedicated wallet with limited funds for trading.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className={`btn-primary ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </form>
    </div>
  );
}