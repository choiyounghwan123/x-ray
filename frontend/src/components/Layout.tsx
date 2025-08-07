import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Upload, 
  FileSearch, 
  Info,
  MessageCircle
} from 'lucide-react'
import clsx from 'clsx'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Upload X-Ray', href: '/upload', icon: Upload },
  { name: 'Results', href: '/results', icon: FileSearch },
  { name: 'About', href: '/about', icon: Info },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 hover:bg-white/10 hover:backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">⚡</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Fast Health
              </span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <Link 
                to="/upload" 
                className={clsx(
                  'text-gray-600 hover:text-blue-600 font-medium transition-colors',
                  location.pathname === '/upload' && 'text-blue-600'
                )}
              >
                Upload X-Ray
              </Link>
              <Link 
                to="/results" 
                className={clsx(
                  'text-gray-600 hover:text-blue-600 font-medium transition-colors',
                  location.pathname === '/results' && 'text-blue-600'
                )}
              >
                Results
              </Link>
              <Link 
                to="/about" 
                className={clsx(
                  'text-gray-600 hover:text-blue-600 font-medium transition-colors',
                  location.pathname === '/about' && 'text-blue-600'
                )}
              >
                About
              </Link>
            </div>

            {/* CTA Button */}
            <div>
              <button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-2 rounded-full font-medium transition-all duration-300 shadow-lg hover:shadow-xl">
                <MessageCircle className="w-4 h-4 inline mr-2" />
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="pt-20">
        <main>
          {children}
        </main>
        
        {/* Footer */}
        <footer className="bg-gray-50 border-t border-gray-200 mt-20">
          <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {/* Company Info */}
              <div className="col-span-1 md:col-span-2">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                    <span className="text-white font-bold text-lg">⚡</span>
                  </div>
                  <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Fast Health Solutions
                  </span>
                </div>
                <p className="text-gray-600 mb-4 max-w-md">
                  Revolutionizing medical imaging with AI-powered X-ray analysis for faster, 
                  more accurate diagnostic insights.
                </p>
                <div className="flex space-x-4">
                  <button className="w-10 h-10 bg-blue-100 hover:bg-blue-200 rounded-full flex items-center justify-center transition-colors">
                    <span className="text-blue-600">📧</span>
                  </button>
                  <button className="w-10 h-10 bg-blue-100 hover:bg-blue-200 rounded-full flex items-center justify-center transition-colors">
                    <span className="text-blue-600">📱</span>
                  </button>
                  <button className="w-10 h-10 bg-blue-100 hover:bg-blue-200 rounded-full flex items-center justify-center transition-colors">
                    <span className="text-blue-600">🌐</span>
                  </button>
                </div>
              </div>

              {/* Services */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Services</h3>
                <ul className="space-y-2">
                  <li><Link to="/upload" className="text-gray-600 hover:text-blue-600 transition-colors">X-Ray Analysis</Link></li>
                  <li><Link to="/results" className="text-gray-600 hover:text-blue-600 transition-colors">AI Diagnostics</Link></li>
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Medical Reports</Link></li>
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Consultation</Link></li>
                </ul>
              </div>

              {/* Support */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Support</h3>
                <ul className="space-y-2">
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Help Center</Link></li>
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Privacy Policy</Link></li>
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Terms of Service</Link></li>
                  <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">Contact Us</Link></li>
                </ul>
              </div>
            </div>

            <div className="border-t border-gray-200 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-500 text-sm">
                © 2024 Fast Health Solutions. All rights reserved.
              </p>
              <p className="text-gray-500 text-sm mt-2 md:mt-0">
                Made with ❤️ for better healthcare
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
} 