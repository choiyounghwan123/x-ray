import { Link } from 'react-router-dom'
import { Upload, Zap, Shield, Clock } from 'lucide-react'

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="relative min-h-screen flex items-center justify-center">
        {/* Background Medical Imagery */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute left-10 top-20 w-32 h-48 medical-gradient rounded-lg transform rotate-12"></div>
          <div className="absolute right-20 top-40 w-24 h-36 medical-gradient rounded-lg transform -rotate-6"></div>
          <div className="absolute left-1/4 bottom-20 w-28 h-40 medical-gradient rounded-lg transform rotate-45"></div>
          <div className="absolute right-1/3 bottom-32 w-20 h-32 medical-gradient rounded-lg transform -rotate-12"></div>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Main Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="block text-gray-800">Fast Health Solutions</span>
            <span className="block text-gradient">for Everyone</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Delivering cutting-edge treatments, life-saving interventions, and 
            compassionate care with precision and dedication—because every 
            second matters in critical situations
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Link 
              to="/upload" 
              className="btn-primary inline-flex items-center justify-center min-w-[180px]"
            >
              Upload X-Ray
            </Link>
            <button className="btn-secondary inline-flex items-center justify-center min-w-[180px]">
              Learn More
            </button>
          </div>

          {/* Feature Tags */}
          <div className="flex flex-wrap justify-center gap-12 text-sm">
            <div className="text-center">
              <div className="text-gray-500 mb-1">(Expert doctors)</div>
            </div>
            <div className="text-center">
              <div className="text-gray-500 mb-1">(Fast diagnostics)</div>
            </div>
            <div className="text-center">
              <div className="text-gray-500 mb-1">(Trusted experts)</div>
            </div>
          </div>
        </div>

        {/* Floating X-ray Elements */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Left hand X-ray */}
          <div className="absolute left-8 top-1/2 transform -translate-y-1/2 opacity-20">
            <div className="w-24 h-32 bg-gradient-to-b from-blue-200 via-purple-200 to-pink-200 rounded-lg shadow-lg"></div>
          </div>
          
          {/* Right spine X-ray */}
          <div className="absolute right-8 top-1/3 transform -translate-y-1/2 opacity-20">
            <div className="w-20 h-48 bg-gradient-to-b from-indigo-200 via-blue-200 to-purple-200 rounded-lg shadow-lg"></div>
          </div>

          {/* Top skull X-ray */}
          <div className="absolute top-20 left-1/2 transform -translate-x-1/2 opacity-15">
            <div className="w-32 h-32 bg-gradient-to-br from-cyan-200 via-blue-200 to-indigo-200 rounded-full shadow-lg"></div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-800 mb-16">
            Advanced AI-Powered X-Ray Analysis
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">Easy Upload</h3>
              <p className="text-gray-600">Simply upload your X-ray images in any standard format for instant analysis</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">AI Analysis</h3>
              <p className="text-gray-600">Our advanced AI models provide accurate and rapid diagnostic insights</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">Secure Results</h3>
              <p className="text-gray-600">Your medical data is protected with enterprise-grade security</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 