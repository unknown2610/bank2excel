import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import StatusDisplay from './components/StatusDisplay';
import rptPreview from './assets/rpt_preview.png';
import jkPreview from './assets/jk_preview.png';

const API_URL = 'https://bank2excel-api-631251922410.us-central1.run.app'; // Default to localhost for now as requested

function App() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, processing, completed, failed
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [conversionType, setConversionType] = useState(null); // null, 'jk_bank', 'rpt', 'generic'

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
    formData.append('conversion_type', conversionType || 'generic');

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

  const resetSelection = () => {
    setConversionType(null);
    setStatus('idle');
    setJobId(null);
    setProgress(0);
    setMessage('');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Navigation */}
      <nav className="w-full px-8 py-8 flex justify-between items-center z-50 animate-fade-in">
        <div className="flex items-center gap-2 cursor-pointer group" onClick={resetSelection}>
          <span className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 group-hover:from-indigo-400 group-hover:to-purple-400 transition-all duration-300">
            BANK2EXCEL
          </span>
        </div>
        <div className="flex gap-6">
          {conversionType && (
            <button onClick={resetSelection} className="flex items-center gap-2 text-sm font-bold text-slate-400 hover:text-white transition-colors uppercase tracking-widest bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/5">
              <span className="text-lg">←</span> Home
            </button>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center px-4 relative z-10">

        {!conversionType ? (
          /* Selection Screen */
          <div className="max-w-7xl w-full flex flex-col items-center">
            <div className="text-center mb-16 space-y-4 animate-fade-in">
              <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight">
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 animate-pulse-glow">
                  Convert faster.
                </span><br />
                <span className="text-white">Work smarter.</span>
              </h1>
              <p className="text-slate-400 text-xl max-w-2xl mx-auto font-light">
                Select your document type to launch our specialized AI conversion logic.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full px-4 md:px-0">

              {/* JK Bank Option */}
              <div
                onClick={() => setConversionType('jk_bank')}
                className="group relative h-[360px] glass-card overflow-hidden cursor-pointer card-hover animate-fade-in"
                style={{ animationDelay: '0.1s' }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="h-2/3 w-full relative overflow-hidden">
                  <img
                    src={jkPreview}
                    alt="JK Bank Preview"
                    className="w-full h-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700 ease-out"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
                </div>

                <div className="p-8 absolute bottom-0 w-full z-10">
                  <div className="w-12 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 mb-4 rounded-full" />
                  <h3 className="text-2xl font-bold mb-2 text-white group-hover:text-indigo-400 transition-colors">JK Bank Statement</h3>
                  <p className="text-slate-400 text-sm leading-relaxed group-hover:text-slate-300">
                    Specialized parsing for J&K Bank PDF layouts. Autosorts withdrawals & deposits.
                  </p>
                </div>
              </div>

              {/* RPT Option */}
              <div
                onClick={() => setConversionType('rpt')}
                className="group relative h-[360px] glass-card overflow-hidden cursor-pointer card-hover animate-fade-in"
                style={{ animationDelay: '0.2s' }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="h-2/3 w-full relative overflow-hidden">
                  <img
                    src={rptPreview}
                    alt="RPT Preview"
                    className="w-full h-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700 ease-out"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
                </div>

                <div className="p-8 absolute bottom-0 w-full z-10">
                  <div className="w-12 h-1 bg-gradient-to-r from-emerald-500 to-teal-500 mb-4 rounded-full" />
                  <h3 className="text-2xl font-bold mb-2 text-white group-hover:text-emerald-400 transition-colors">RPT to Excel</h3>
                  <p className="text-slate-400 text-sm leading-relaxed group-hover:text-slate-300">
                    Handle complex fixed-width RPT files. Perfect for legacy banking systems.
                  </p>
                </div>
              </div>

              {/* Generic Option */}
              <div
                onClick={() => setConversionType('generic')}
                className="group relative h-[360px] glass-card overflow-hidden cursor-pointer card-hover animate-fade-in"
                style={{ animationDelay: '0.3s' }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-pink-500/20 to-orange-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="h-2/3 w-full relative overflow-hidden bg-slate-800/50 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-24 w-24 text-slate-600 group-hover:text-pink-500 transition-colors duration-500 group-hover:scale-110 transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
                </div>

                <div className="p-8 absolute bottom-0 w-full z-10">
                  <div className="w-12 h-1 bg-gradient-to-r from-pink-500 to-orange-500 mb-4 rounded-full" />
                  <h3 className="text-2xl font-bold mb-2 text-white group-hover:text-pink-400 transition-colors">Smart Auto-Detect</h3>
                  <p className="text-slate-400 text-sm leading-relaxed group-hover:text-slate-300">
                    General purpose PDF and Image conversion. Best for simple tables.
                  </p>
                </div>
              </div>

            </div>
          </div>
        ) : (
          /* Upload Interface */
          <div className="max-w-4xl w-full flex flex-col items-center animate-fade-in">
            <h2 className="text-4xl font-bold mb-12 text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-500">
              <span className="text-indigo-500 mr-4">Converting:</span>
              {conversionType === 'jk_bank' && "JK Bank Statement"}
              {conversionType === 'rpt' && "RPT File"}
              {conversionType === 'generic' && "General Document"}
            </h2>

            <div className="w-full relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>

              <div className="glass-card p-1 relative bg-slate-900 ring-1 ring-white/10 rounded-2xl">
                <div className="bg-slate-950/50 rounded-xl p-8 min-h-[400px] flex flex-col justify-center">
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
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full py-8 text-center text-slate-500 text-sm font-medium">
        Bank2Excel © 2026. <span className="text-slate-600">AI'ed by Gurpreet (NRO0549648)</span>
      </footer>
    </div>
  );
}

export default App;
