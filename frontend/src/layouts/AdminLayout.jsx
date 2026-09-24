import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, Clock, ShieldCheck, FileText, Menu, Bell, Search } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workers', icon: Users, label: 'Workers' },
  { to: '/attendance', icon: Clock, label: 'Attendance' },
  { to: '/ppe', icon: ShieldCheck, label: 'PPE Monitoring' },
  { to: '/reports', icon: FileText, label: 'Reports' },
];

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden text-slate-900">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 flex flex-col`}
      >
        <div className="flex items-center justify-center h-16 border-b border-slate-800 px-4">
          <ShieldCheck className="h-8 w-8 text-blue-500 mr-2" />
          <span className="text-xl font-bold tracking-tight">AI-PPE Admin</span>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full bg-slate-700 flex items-center justify-center font-bold text-lg">
              A
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">Site Admin</p>
              <p className="text-xs text-slate-400">admin@construction.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 z-30 shadow-sm">
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 hover:text-gray-700 focus:outline-none lg:hidden p-2 rounded-md hover:bg-gray-100"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="hidden sm:flex items-center bg-gray-100 rounded-full px-4 py-2 ml-4">
              <Search className="h-4 w-4 text-gray-400" />
              <input 
                type="text" 
                placeholder="Search..." 
                className="bg-transparent border-none focus:ring-0 text-sm ml-2 outline-none w-64 text-gray-700"
              />
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-400 hover:text-gray-500 transition-colors">
              <Bell className="h-6 w-6" />
              <span className="absolute top-1.5 right-1.5 block h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-white"></span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-4 lg:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
