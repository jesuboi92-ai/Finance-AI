import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FiHome, FiTruck, FiUsers, FiBarChart3, FiLogOut, FiMenu } from 'react-icons/fi'
import { useAuthStore } from '@/stores/authStore'

export const Sidebar: React.FC = () => {
  const location = useLocation()
  const logout = useAuthStore((state) => state.logout)
  const [isOpen, setIsOpen] = React.useState(false)

  const menuItems = [
    { label: 'Dashboard', path: '/', icon: FiHome },
    { label: 'Warehouse', path: '/warehouse', icon: FiHome },
    { label: 'Transport', path: '/transport', icon: FiTruck },
    { label: 'Customers', path: '/customers', icon: FiUsers },
    { label: 'Management', path: '/management', icon: FiBarChart3 },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-blue-600 text-white"
        onClick={() => setIsOpen(!isOpen)}
      >
        <FiMenu size={24} />
      </button>

      <aside
        className={`fixed left-0 top-0 h-screen w-64 bg-slate-900 text-white p-6 transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-blue-400">Logistics SaaS</h1>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <button
          onClick={() => {
            logout()
            setIsOpen(false)
          }}
          className="mt-auto flex items-center gap-3 px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-800 transition-colors w-full"
        >
          <FiLogOut size={20} />
          <span>Logout</span>
        </button>
      </aside>
    </>
  )
}
