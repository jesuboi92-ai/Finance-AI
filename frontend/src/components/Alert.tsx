import React from 'react'
import { FiAlertCircle, FiCheckCircle, FiInfo } from 'react-icons/fi'
import toast from 'react-hot-toast'

interface AlertProps {
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  title?: string
}

export const Alert: React.FC<AlertProps> = ({ type, message, title }) => {
  const bgColor = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    info: 'bg-blue-50 border-blue-200',
    warning: 'bg-yellow-50 border-yellow-200',
  }[type]

  const textColor = {
    success: 'text-green-800',
    error: 'text-red-800',
    info: 'text-blue-800',
    warning: 'text-yellow-800',
  }[type]

  const Icon =
    type === 'success' ? (
      <FiCheckCircle />
    ) : type === 'error' ? (
      <FiAlertCircle />
    ) : (
      <FiInfo />
    )

  return (
    <div className={`border rounded-lg p-4 ${bgColor}`}>
      <div className={`flex items-center gap-2 ${textColor}`}>
        {Icon}
        {title && <h3 className="font-semibold">{title}</h3>}
      </div>
      <p className={`mt-1 ${textColor}`}>{message}</p>
    </div>
  )
}

export const showToast = (type: 'success' | 'error' | 'info', message: string) => {
  toast[type](message, {
    position: 'bottom-right',
    duration: 4000,
  })
}
