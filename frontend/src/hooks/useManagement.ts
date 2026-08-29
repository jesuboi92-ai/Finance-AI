import { useQuery } from 'react-query'
import api from '@/services/api'

interface DashboardMetrics {
  warehouse_items_count: number
  pending_tasks: number
  active_shipments: number
  critical_anomalies: number
  pending_communications: number
  key_metrics: Record<string, number>
  recent_anomalies: any[]
}

export const useDashboard = () => {
  return useQuery(
    'dashboard',
    () => api.get('/management/dashboard').then(r => r.data),
    { refetchInterval: 60000 }
  )
}

export const useMetrics = (category?: string) => {
  return useQuery(
    ['metrics', category],
    () => api.get('/management/metrics', { params: { category } }).then(r => r.data),
    { refetchInterval: 60000 }
  )
}

export const useAnomalies = () => {
  return useQuery(
    'anomalies',
    () => api.get('/management/anomalies').then(r => r.data),
    { refetchInterval: 60000 }
  )
}
