import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '@/services/api'

interface Task {
  id: string
  task_type: string
  status: string
  priority: string
  description: string
  assigned_to?: string
  due_date: string
  created_at: string
}

export const useWarehouseTasks = (status?: string) => {
  return useQuery(
    ['warehouse-tasks', status],
    () => api.get('/warehouse/tasks', { params: { status } }).then(r => r.data),
    { refetchInterval: 30000 }
  )
}

export const useCreateTask = () => {
  const queryClient = useQueryClient()
  return useMutation(
    (task: Partial<Task>) => api.post('/warehouse/tasks', task),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('warehouse-tasks')
      },
    }
  )
}

export const useWarehouseAnomalies = () => {
  return useQuery(
    'warehouse-anomalies',
    () => api.get('/warehouse/anomalies').then(r => r.data),
    { refetchInterval: 60000 }
  )
}
