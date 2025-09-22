import { useState, useEffect } from 'react';
import axios from 'axios';
import ConfigForm from './ConfigForm';
import ExecutionLog from './ExecutionLog';
import { PlayIcon, StopIcon, CogIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [controlLoading, setControlLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/api/status');
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBotControl = async (action) => {
    setControlLoading(true);
    try {
      const response = await axios.post('/api/control', { action });
      if (response.data.success) {
        await fetchStatus(); // Refresh status
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert('Failed to control bot: ' + error.message);
    } finally {
      setControlLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Volume Bot Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor and control your trading bot</p>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-3 ${status?.is_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <div>
                <p className="text-sm font-medium text-gray-600">Status</p>
                <p className="text-lg font-semibold">{status?.is_running ? 'Running' : 'Stopped'}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <ChartBarIcon className="w-6 h-6 text-blue-600 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Trades</p>
                <p className="text-lg font-semibold">{status?.total_trades || 0}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3">
                <div className="w-3 h-3 bg-green-600 rounded-full"></div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-lg font-semibold">{status?.success_rate?.toFixed(1) || 0}%</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Volume</p>
                <p className="text-lg font-semibold">{status?.total_volume?.toFixed(4) || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="card mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Bot Control</h3>
              <p className="text-gray-600">Start or stop the trading bot</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => handleBotControl('start')}
                disabled={status?.is_running || controlLoading}
                className={`btn-primary flex items-center ${status?.is_running || controlLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <PlayIcon className="w-4 h-4 mr-2" />
                Start Bot
              </button>
              <button
                onClick={() => handleBotControl('stop')}
                disabled={!status?.is_running || controlLoading}
                className={`btn-danger flex items-center ${!status?.is_running || controlLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <StopIcon className="w-4 h-4 mr-2" />
                Stop Bot
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('config')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'config'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <CogIcon className="w-4 h-4 inline mr-1" />
              Configuration
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'logs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Execution Logs
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Bot Information */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Contract Address</p>
                  <p className="text-sm text-gray-900 font-mono break-all">
                    {status?.config?.contract_address || 'Not configured'}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Trade Amount</p>
                  <p className="text-sm text-gray-900">{status?.config?.trade_amount || 'Not configured'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Min Interval</p>
                  <p className="text-sm text-gray-900">{status?.config?.min_interval_seconds || 0}s</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Max Interval</p>
                  <p className="text-sm text-gray-900">{status?.config?.max_interval_seconds || 0}s</p>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Last Trade Time</span>
                  <span className="text-sm text-gray-900">
                    {status?.last_trade_time 
                      ? new Date(status.last_trade_time).toLocaleString()
                      : 'No trades yet'
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Next Trade Time</span>
                  <span className="text-sm text-gray-900">
                    {status?.next_trade_time 
                      ? new Date(status.next_trade_time).toLocaleString()
                      : 'Not scheduled'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <ConfigForm onConfigUpdate={fetchStatus} />
        )}

        {activeTab === 'logs' && (
          <ExecutionLog />
        )}
      </div>
    </div>
  );
}