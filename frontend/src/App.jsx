import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import StatusDisplay from './components/StatusDisplay';

const API_URL = 'https://bank2excel-backend-361068788298.us-central1.run.app';

function App() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, processing, completed, failed
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');

  useEffect(() => {
    let interval;
    if (jobId && status === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/status/${jobId}`);
          const data = await res.json();
          setStatus(data.status);
          setProgress(data.progress);
          setMessage(data.message);

          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
          }
        } catch (error) {
          console.error("Error polling status:", error);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setStatus('processing');
      setProgress(0);
      setMessage('Uploading file...');

      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Upload failed');

      const data = await res.json();
      setJobId(data.job_id);

    } catch (error) {
      console.error("Upload error:", error);
      setStatus('failed');
      setMessage('Failed to upload file. Please check the backend connection.');
    }
  };

  const handleDownload = () => {
    if (jobId) {
      window.location.href = `${API_URL}/download/${jobId}`;
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900">
      {/* Navigation */}
      <nav className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 text-white p-1.5 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
            </svg>
          </div>
          <span className="text-xl font-bold text-slate-800">Bank 2 Excel</span>
        </div>

        <div className="hidden md:flex gap-8">
          <a href="#" className="nav-link">Features</a>
          <a href="#" className="nav-link">Pricing</a>
          <a href="#" className="nav-link">Security</a>
        </div>

        <div>
          <button className="btn-outline px-6 py-2 rounded-full text-sm font-semibold">Sign In</button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-grow flex flex-col items-center justify-center px-4 mt-10 mb-20">
        <div className="max-w-7xl w-full grid md:grid-cols-2 gap-12 items-center">

          {/* Left Content */}
          <div className="text-left space-y-6">
            <h1 className="text-5xl md:text-6xl font-bold leading-tight text-slate-900">
              Effortlessly Convert Bank Statements to Excel
            </h1>
            <p className="text-lg text-slate-600 max-w-lg leading-relaxed">
              Accurate, secure, and fast PDF to spreadsheet conversion for accountants and businesses.
            </p>
            <div className="pt-4">
              <button
                onClick={() => document.getElementById('upload-card').scrollIntoView({ behavior: 'smooth' })}
                className="btn-primary text-lg shadow-emerald-200"
              >
                Try for Free
              </button>
            </div>

            {/* Features Icons */}
            <div className="grid grid-cols-3 gap-6 pt-12">
              <div>
                <div className="feature-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-sm mb-1">High Accuracy AI</h3>
                <p className="text-xs text-slate-500">Convert vast PDF statements with high accuracy.</p>
              </div>
              <div>
                <div className="feature-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-sm mb-1">Bank-Grade Security</h3>
                <p className="text-xs text-slate-500">Provides secure encryption and data protection.</p>
              </div>
              <div>
                <div className="feature-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-sm mb-1">Instant Processing</h3>
                <p className="text-xs text-slate-500">Easy-to-use sessions for instant processing.</p>
              </div>
            </div>
          </div>

          {/* Right Content - The Functional Card */}
          <div id="upload-card" className="relative">
            {/* Decorative Elements behind card */}
            <div className="absolute -top-10 -right-10 w-64 h-64 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
            <div className="absolute -bottom-10 -left-10 w-64 h-64 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>

            <div className="glass-card p-8 relative z-10 min-h-[400px] flex flex-col justify-center">
              {status === 'idle' ? (
                <FileUpload onUpload={handleUpload} disabled={false} />
              ) : (
                <StatusDisplay
                  status={status}
                  progress={progress}
                  message={message}
                  onDownload={handleDownload}
                  onReset={() => {
                    setStatus('idle');
                    setJobId(null);
                    setProgress(0);
                    setMessage('');
                  }}
                />
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
