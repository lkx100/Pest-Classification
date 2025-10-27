import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedFile(file)
      setResult(null)
      setError(null)
      
      // Create preview URL
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select an image first')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Prediction failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to classify image')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🐛 Pest Classification</h1>
        <p>Upload an image to classify pest type</p>
      </header>

      <main className="main">
        <div className="upload-section">
          <input
            type="file"
            id="file-input"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="file-label">
            {selectedFile ? '📷 Change Image' : '📷 Select Image'}
          </label>
          
          {selectedFile && (
            <span className="file-name">{selectedFile.name}</span>
          )}
        </div>

        {preview && (
          <div className="preview-section">
            <img src={preview} alt="Preview" className="preview-image" />
          </div>
        )}

        {selectedFile && !loading && !result && (
          <button onClick={handleSubmit} className="submit-btn">
            Classify Image
          </button>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing image...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>❌ {error}</p>
            <button onClick={handleReset} className="reset-btn">
              Try Again
            </button>
          </div>
        )}

        {result && (
          <div className="result">
            <h2>Classification Result</h2>
            <div className="result-label">
              <strong>Prediction:</strong> {result.label}
            </div>
            <div className="probabilities">
              <h3>Confidence Scores:</h3>
              {result.probabilities.map((prob, index) => {
                const labels = ['Semilooper', 'Spodoptera', 'Healthy Leaf']
                const percentage = (prob * 100).toFixed(2)
                return (
                  <div key={index} className="prob-item">
                    <span className="prob-label">{labels[index]}:</span>
                    <div className="prob-bar-container">
                      <div 
                        className="prob-bar" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="prob-value">{percentage}%</span>
                  </div>
                )
              })}
            </div>
            <button onClick={handleReset} className="reset-btn">
              Classify Another Image
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
