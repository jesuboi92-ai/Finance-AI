import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '@/services/api'

interface Shipment {
  id: string
  shipment_number: string
  status: string
  vehicle_id?: string
  delay_risk: boolean
  actual_delivery?: string
  created_at: string
}

export const useShipments = (status?: string) => {
  return useQuery(
    ['shipments', status],
    () => api.get('/transport/shipments', { params: { status } }).then(r => r.data),
    { refetchInterval: 30000 }
  )
}

export const useCreateShipment = () => {
  const queryClient = useQueryClient()
  return useMutation(
    (shipment: Partial<Shipment>) => api.post('/transport/shipments', shipment),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('shipments')
      },
    }
  )
}

export const useShipmentTracking = (shipmentId: string) => {
  return useQuery(
    ['shipment-tracking', shipmentId],
    () => api.get(`/transport/shipments/${shipmentId}/tracking`).then(r => r.data),
    { refetchInterval: 10000 }
  )
}
