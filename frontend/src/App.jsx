import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import StatusDisplay from './components/StatusDisplay';
import { Shield, Zap, CheckCircle, ArrowRight } from 'lucide-react';

const API_URL = "https://bank2excel-backend-361068788298.us-central1.run.app/";

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

  const resetUpload = () => {
    setStatus('idle');
    setJobId(null);
    setProgress(0);
    setMessage('');
  };

  return (
    <div className="min-h-screen bg-brand-50 font-sans text-slate-900">
      {/* Navbar */}
      <nav className="container mx-auto px-6 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="bg-brand-600 p-2 rounded-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <span className="text-xl font-bold text-slate-900">Bank 2 Excel</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="nav-link">Features</a>
          <a href="#pricing" className="nav-link">Pricing</a>
          <a href="#security" className="nav-link">Security</a>
        </div>
        <button className="px-6 py-2 rounded-full border border-slate-200 hover:border-slate-400 font-medium transition-colors">
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <header className="container mx-auto px-6 pt-16 pb-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="max-w-2xl">
            <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6 text-slate-900">
              Effortlessly Convert Bank Statements to Excel
            </h1>
            <p className="text-xl text-slate-600 mb-8 leading-relaxed">
              Accurate, secure, and fast PDF to spreadsheet conversion for accountants and businesses.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="btn-primary flex items-center justify-center gap-2">
                Try for Free <ArrowRight className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-16 grid grid-cols-3 gap-8">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-5 h-5 text-brand-600" />
                  <h3 className="font-semibold">High Accuracy AI</h3>
                </div>
                <p className="text-sm text-slate-500">Convert vast PDF statements with high accuracy.</p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-brand-600" />
                  <h3 className="font-semibold">Bank-Grade Security</h3>
                </div>
                <p className="text-sm text-slate-500">Provides secure root and collected data.</p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-brand-600" />
                  <h3 className="font-semibold">Instant Processing</h3>
                </div>
                <p className="text-sm text-slate-500">Easy-to-event sessions to instant processing.</p>
              </div>
            </div>
          </div>

          {/* Right Side - Upload Component / Graphic */}
          <div className="relative">
            {/* Decorative elements */}
            <div className="absolute -top-10 -right-10 w-72 h-72 bg-brand-500/10 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-accent-500/10 rounded-full blur-3xl"></div>

            <div className="relative glass-panel p-8">
              {status === 'idle' ? (
                <FileUpload onUpload={handleUpload} disabled={false} />
              ) : (
                <div className="py-8">
                  <StatusDisplay
                    status={status}
                    progress={progress}
                    message={message}
                    onDownload={handleDownload}
                  />
                  {status !== 'processing' && (
                    <div className="text-center mt-6">
                      <button
                        onClick={resetUpload}
                        className="text-brand-600 hover:text-brand-700 font-medium hover:underline"
                      >
                        Convert Another File
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
