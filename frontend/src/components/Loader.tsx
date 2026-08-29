import React from 'react'

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg'
}

export const Loader: React.FC<LoaderProps> = ({ size = 'md' }) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size]

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClass} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}
      ></div>
    </div>
  )
}

export const FullPageLoader: React.FC = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-8 rounded-lg">
        <Loader size="lg" />
        <p className="mt-4 text-center text-gray-600">Loading...</p>
      </div>
    </div>
  )
}
