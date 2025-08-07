import { Brain, Shield, Zap, Users, Award, Heart } from 'lucide-react'

export default function About() {
  return (
    <div className="min-h-screen pt-8 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            About Fast Health Solutions
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Revolutionizing medical imaging with AI-powered X-ray analysis 
            for faster, more accurate diagnostic insights
          </p>
        </div>

        {/* Mission Statement */}
        <div className="card mb-16 text-center">
          <div className="max-w-4xl mx-auto">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Heart className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-6">Our Mission</h2>
            <p className="text-lg text-gray-300 leading-relaxed">
              We believe that every second matters in critical medical situations. Our advanced AI technology 
              provides rapid, accurate X-ray analysis to support healthcare professionals in delivering 
              life-saving care with unprecedented speed and precision.
            </p>
          </div>
        </div>

        {/* Key Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            Why Choose Our Platform?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Advanced AI Technology</h3>
              <p className="text-gray-300">
                Our deep learning models are trained on millions of X-ray images, 
                providing state-of-the-art accuracy in medical image analysis.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Lightning Fast Results</h3>
              <p className="text-gray-300">
                Get comprehensive analysis results in seconds, not hours. 
                Our optimized algorithms deliver rapid insights for urgent cases.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">HIPAA Compliant</h3>
              <p className="text-gray-300">
                Your medical data is protected with enterprise-grade security. 
                We maintain the highest standards of privacy and compliance.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Expert Validation</h3>
              <p className="text-gray-300">
                Our AI models are developed and validated by board-certified radiologists 
                and medical imaging experts.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Clinically Proven</h3>
              <p className="text-gray-300">
                Our technology has been tested in real clinical settings, 
                demonstrating improved diagnostic accuracy and workflow efficiency.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Patient-Centered</h3>
              <p className="text-gray-300">
                Designed with patient care in mind, helping healthcare providers 
                deliver faster, more compassionate treatment.
              </p>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="card mb-16">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">1</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Upload X-Ray</h3>
              <p className="text-gray-300">
                Securely upload your X-ray images in JPEG, PNG, or DICOM format
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">2</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">AI Analysis</h3>
              <p className="text-gray-300">
                Our advanced AI analyzes the images and identifies potential findings
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">3</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Get Results</h3>
              <p className="text-gray-300">
                Receive detailed analysis reports with confidence scores and recommendations
              </p>
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="card">
          <div className="text-center">
            <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-yellow-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-4">Important Medical Disclaimer</h3>
            <p className="text-gray-300 max-w-3xl mx-auto">
              This AI-powered analysis tool is designed to assist healthcare professionals and is not intended 
              to replace clinical judgment or professional medical diagnosis. All results should be reviewed 
              by qualified medical personnel. This service is for screening and educational purposes only.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 