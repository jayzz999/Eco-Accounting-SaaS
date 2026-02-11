'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Upload,
  Shield,
  Coins,
  Settings,
  Leaf,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload Bills', href: '/dashboard/bills/upload', icon: Upload },
  { name: 'Bills', href: '/dashboard/bills', icon: FileText },
  { name: 'Emissions', href: '/dashboard/emissions', icon: BarChart3 },
  { name: 'Reports', href: '/dashboard/reports', icon: FileText },
  { name: 'Compliance', href: '/dashboard/compliance', icon: Shield },
  { name: 'Carbon Credits', href: '/dashboard/carbon-credits', icon: Coins },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-64 flex-col bg-gray-900">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 px-6 border-b border-gray-800">
        <Leaf className="h-8 w-8 text-green-500" />
        <span className="text-xl font-bold text-white">EcoAccounting</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-800 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
            U
          </div>
          <div className="flex-1">
            <div className="text-sm font-medium text-white">User</div>
            <div className="text-xs text-gray-400">user@company.com</div>
          </div>
        </div>
      </div>
    </div>
  )
}
