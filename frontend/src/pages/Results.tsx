import { useState } from 'react'
import { Download, Eye, AlertTriangle, CheckCircle, Info, Share2 } from 'lucide-react'

interface AnalysisResult {
  id: string
  imageName: string
  imageUrl: string
  confidence: number
  findings: Array<{
    type: 'normal' | 'abnormal' | 'uncertain'
    description: string
    confidence: number
    location?: string
  }>
  recommendations: string[]
  uploadDate: string
}

export default function Results() {
  const [selectedResult, setSelectedResult] = useState<string | null>(null)

  // Mock data - would come from API
  const analysisResults: AnalysisResult[] = [
    {
      id: '1',
      imageName: 'chest_xray_001.jpg',
      imageUrl: '/api/placeholder/400/300',
      confidence: 94.2,
      findings: [
        {
          type: 'normal',
          description: 'Clear lung fields with no signs of consolidation',
          confidence: 96.1,
          location: 'Bilateral lungs'
        },
        {
          type: 'normal',
          description: 'Normal heart size and shape',
          confidence: 92.3,
          location: 'Cardiac silhouette'
        },
        {
          type: 'uncertain',
          description: 'Possible minor calcification',
          confidence: 67.8,
          location: 'Right upper lobe'
        }
      ],
      recommendations: [
        'No immediate action required based on current findings',
        'Follow-up in 6 months if symptoms persist',
        'Consider CT scan for better visualization of minor calcification'
      ],
      uploadDate: '2024-01-15 14:30'
    },
    {
      id: '2',
      imageName: 'hand_xray_002.jpg',
      imageUrl: '/api/placeholder/400/300',
      confidence: 87.5,
      findings: [
        {
          type: 'abnormal',
          description: 'Possible fracture line detected',
          confidence: 89.2,
          location: 'Fifth metacarpal'
        },
        {
          type: 'normal',
          description: 'No dislocation observed',
          confidence: 94.7,
          location: 'Joints'
        }
      ],
      recommendations: [
        'Immediate orthopedic consultation recommended',
        'Immobilization of affected area',
        'Follow-up X-ray in 2-3 weeks'
      ],
      uploadDate: '2024-01-15 14:25'
    }
  ]

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-400'
    if (confidence >= 70) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getFindingIcon = (type: string) => {
    switch (type) {
      case 'normal': return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'abnormal': return <AlertTriangle className="w-5 h-5 text-red-400" />
      case 'uncertain': return <Info className="w-5 h-5 text-yellow-400" />
      default: return null
    }
  }

  const getFindingBg = (type: string) => {
    switch (type) {
      case 'normal': return 'bg-green-500/10 border-green-500/20'
      case 'abnormal': return 'bg-red-500/10 border-red-500/20'
      case 'uncertain': return 'bg-yellow-500/10 border-yellow-500/20'
      default: return 'bg-gray-500/10 border-gray-500/20'
    }
  }

  return (
    <div className="min-h-screen pt-8 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Analysis Results
          </h1>
          <p className="text-lg text-gray-300">
            AI-powered analysis of your X-ray images with detailed findings and recommendations
          </p>
        </div>

        {/* Results Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {analysisResults.map((result) => (
            <div key={result.id} className="card">
              {/* Image Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-white">{result.imageName}</h3>
                  <p className="text-gray-400 text-sm">Analyzed on {result.uploadDate}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`font-semibold ${getConfidenceColor(result.confidence)}`}>
                    {result.confidence}%
                  </span>
                  <span className="text-gray-400 text-sm">confidence</span>
                </div>
              </div>

              {/* X-ray Image */}
              <div className="relative mb-6 group">
                <div className="aspect-video bg-gray-800 rounded-lg overflow-hidden">
                  <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
                    <span className="text-gray-500">X-ray Image Preview</span>
                  </div>
                </div>
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <button 
                    onClick={() => setSelectedResult(result.id)}
                    className="btn-primary"
                  >
                    <Eye className="w-5 h-5 mr-2" />
                    View Full Image
                  </button>
                </div>
              </div>

              {/* Findings */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-white mb-4">Findings</h4>
                <div className="space-y-3">
                  {result.findings.map((finding, index) => (
                    <div key={index} className={`p-4 rounded-lg border ${getFindingBg(finding.type)}`}>
                      <div className="flex items-start space-x-3">
                        {getFindingIcon(finding.type)}
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-medium text-white">{finding.description}</p>
                            <span className={`text-sm ${getConfidenceColor(finding.confidence)}`}>
                              {finding.confidence}%
                            </span>
                          </div>
                          {finding.location && (
                            <p className="text-sm text-gray-400">Location: {finding.location}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-white mb-4">Recommendations</h4>
                <div className="space-y-2">
                  {result.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-gray-300 text-sm">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3">
                <button className="btn-primary flex-1">
                  <Download className="w-4 h-4 mr-2" />
                  Download Report
                </button>
                <button className="btn-secondary">
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Summary Card */}
        <div className="mt-12 card">
          <h3 className="text-2xl font-semibold text-white mb-6">Analysis Summary</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <h4 className="font-semibold text-white mb-1">Normal Findings</h4>
              <p className="text-green-400 text-2xl font-bold">3</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <h4 className="font-semibold text-white mb-1">Abnormal Findings</h4>
              <p className="text-red-400 text-2xl font-bold">1</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Info className="w-8 h-8 text-yellow-400" />
              </div>
              <h4 className="font-semibold text-white mb-1">Uncertain</h4>
              <p className="text-yellow-400 text-2xl font-bold">1</p>
            </div>
          </div>

          <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex items-start space-x-3">
              <Info className="w-5 h-5 text-blue-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-300 mb-1">Important Notice</h4>
                <p className="text-sm text-gray-300">
                  This AI analysis is for preliminary screening purposes only and should not replace professional medical diagnosis. 
                  Please consult with a qualified radiologist or physician for definitive interpretation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Full Image Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-4xl w-full bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Full Image View</h3>
              <button 
                onClick={() => setSelectedResult(null)}
                className="w-8 h-8 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center transition-colors"
              >
                <span className="text-white text-lg">×</span>
              </button>
            </div>
            <div className="aspect-video bg-gray-800 rounded-lg">
              <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
                <span className="text-gray-500">Full Resolution X-ray Image</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 