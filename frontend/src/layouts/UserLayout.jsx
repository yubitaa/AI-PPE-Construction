import { NavLink, Outlet } from 'react-router-dom';
import { Camera, ShieldAlert } from 'lucide-react';

export default function UserLayout() {
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-800">
      {/* Top Navbar */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <Camera className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900">AI-PPE</span>
          </div>
          
          <nav className="flex space-x-1 bg-slate-100 p-1 rounded-lg">
            <NavLink
              to="/user/clock-in"
              className={({ isActive }) =>
                `px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                  isActive
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`
              }
            >
              Clock In
            </NavLink>
            <NavLink
              to="/user/ppe-monitoring"
              className={({ isActive }) =>
                `px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                  isActive
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`
              }
            >
              PPE Status
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Main Content Area (Mobile optimized) */}
      <main className="flex-1 flex flex-col max-w-md mx-auto w-full p-4">
        <Outlet />
      </main>

      {/* Footer Alert if needed */}
      <footer className="bg-white border-t border-gray-200 p-4 pb-safe text-center">
        <div className="max-w-md mx-auto flex items-center justify-center text-xs text-slate-500">
          <ShieldAlert className="h-4 w-4 mr-1.5" />
          Ensure all PPE is visible to the camera
        </div>
      </footer>
    </div>
  );
}
