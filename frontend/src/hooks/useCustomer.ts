import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '@/services/api'

interface Customer {
  id: string
  customer_name: string
  email: string
  phone: string
  city: string
  is_active: boolean
}

interface Order {
  id: string
  order_number: string
  status: string
  total_amount: number
  delivery_date?: string
}

export const useCustomers = () => {
  return useQuery(
    'customers',
    () => api.get('/customer/customers').then(r => r.data),
    { refetchInterval: 60000 }
  )
}

export const useCreateCustomer = () => {
  const queryClient = useQueryClient()
  return useMutation(
    (customer: Partial<Customer>) => api.post('/customer/customers', customer),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('customers')
      },
    }
  )
}

export const useOrders = (status?: string) => {
  return useQuery(
    ['orders', status],
    () => api.get('/customer/orders', { params: { status } }).then(r => r.data),
    { refetchInterval: 30000 }
  )
}

export const useCreateOrder = () => {
  const queryClient = useQueryClient()
  return useMutation(
    (order: Partial<Order>) => api.post('/customer/orders', order),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders')
      },
    }
  )
}
