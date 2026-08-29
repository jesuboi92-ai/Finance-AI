import React from 'react'
import { useDashboard, useMetrics, useAnomalies } from '@/hooks/useManagement'
import { Loader } from '@/components/Alert'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export const DashboardPage: React.FC = () => {
  const { data: dashboard, isLoading: dashboardLoading } = useDashboard()
  const { data: metrics, isLoading: metricsLoading } = useMetrics()
  const { data: anomalies } = useAnomalies()

  if (dashboardLoading || metricsLoading) {
    return <Loader />
  }

  const metricCards = [
    {
      label: 'Warehouse Items',
      value: dashboard?.warehouse_items_count || 0,
      color: 'bg-blue-100 text-blue-800',
    },
    {
      label: 'Pending Tasks',
      value: dashboard?.pending_tasks || 0,
      color: 'bg-yellow-100 text-yellow-800',
    },
    {
      label: 'Active Shipments',
      value: dashboard?.active_shipments || 0,
      color: 'bg-green-100 text-green-800',
    },
    {
      label: 'Critical Issues',
      value: dashboard?.critical_anomalies || 0,
      color: 'bg-red-100 text-red-800',
    },
  ]

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your logistics overview.</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((card, index) => (
          <div key={index} className={`p-6 rounded-lg ${card.color}`}>
            <p className="text-sm font-medium opacity-75">{card.label}</p>
            <p className="text-3xl font-bold mt-2">{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Performance Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Performance Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics?.slice(0, 7) || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="metric_value" stroke="#3B82F6" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Anomalies */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Anomalies</h2>
          <div className="space-y-3">
            {dashboard?.recent_anomalies?.slice(0, 5).map((anomaly: any, index: number) => (
              <div key={index} className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                <p className="font-semibold text-red-800">{anomaly.type}</p>
                <p className="text-sm text-red-700">{anomaly.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
