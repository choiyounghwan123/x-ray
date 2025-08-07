import { useState, useCallback } from 'react'
import { Upload as UploadIcon, FileImage, AlertCircle, CheckCircle, X } from 'lucide-react'

interface UploadedFile {
  file: File
  preview: string
  id: string
}

export default function Upload() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      handleFiles(files)
    }
  }

  const handleFiles = (files: File[]) => {
    const imageFiles = files.filter(file => file.type.startsWith('image/'))
    
    imageFiles.forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const newFile: UploadedFile = {
          file,
          preview: e.target?.result as string,
          id: Math.random().toString(36).substr(2, 9)
        }
        setUploadedFiles(prev => [...prev, newFile])
      }
      reader.readAsDataURL(file)
    })
  }

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id))
  }

  const analyzeImages = async () => {
    setIsAnalyzing(true)
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 3000))
    setIsAnalyzing(false)
    // Navigate to results page (would be implemented with router)
    alert('Analysis complete! Redirecting to results...')
  }

  return (
    <div className="min-h-screen pt-8 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Upload Your X-Ray Images
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Upload one or more X-ray images for AI-powered analysis. 
            Supported formats: JPEG, PNG, DICOM
          </p>
        </div>

        {/* Upload Area */}
        <div className="card mb-8">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
              isDragging 
                ? 'border-pink-400 bg-pink-400/10' 
                : 'border-white/30 hover:border-white/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-orange-500 rounded-full flex items-center justify-center">
                <UploadIcon className="w-8 h-8 text-white" />
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  Drag and drop your X-ray images here
                </h3>
                <p className="text-gray-300 mb-4">or click to browse files</p>
                
                <label htmlFor="file-upload" className="btn-primary cursor-pointer inline-flex items-center">
                  <FileImage className="w-5 h-5 mr-2" />
                  Choose Files
                </label>
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileInput}
                  className="hidden"
                />
              </div>
            </div>
          </div>

          {/* File Requirements */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-300 mb-1">Upload Requirements</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Maximum file size: 10MB per image</li>
                  <li>• Supported formats: JPEG, PNG, DICOM</li>
                  <li>• High resolution images provide better analysis</li>
                  <li>• Multiple images can be analyzed simultaneously</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Uploaded Files */}
        {uploadedFiles.length > 0 && (
          <div className="card mb-8">
            <h3 className="text-xl font-semibold text-white mb-6">Uploaded Images</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uploadedFiles.map((uploadedFile) => (
                <div key={uploadedFile.id} className="relative group">
                  <div className="glass-effect rounded-lg p-4">
                    <img
                      src={uploadedFile.preview}
                      alt="X-ray preview"
                      className="w-full h-32 object-cover rounded-lg mb-3"
                    />
                    <p className="text-sm text-gray-300 truncate">
                      {uploadedFile.file.name}
                    </p>
                    <p className="text-xs text-gray-400">
                      {(uploadedFile.file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  
                  <button
                    onClick={() => removeFile(uploadedFile.id)}
                    className="absolute top-2 right-2 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              ))}
            </div>

            {/* Analysis Button */}
            <div className="mt-8 text-center">
              <button
                onClick={analyzeImages}
                disabled={isAnalyzing}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Start AI Analysis
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Privacy Notice */}
        <div className="card">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h4 className="font-medium text-green-300 mb-2">Privacy & Security</h4>
              <p className="text-sm text-gray-300">
                Your medical images are processed securely and are not stored permanently on our servers. 
                All data is encrypted during transmission and analysis. We comply with HIPAA and GDPR regulations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 