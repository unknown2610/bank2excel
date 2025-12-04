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
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400 mb-4">
            Bank2Excel
          </h1>
          <p className="text-slate-400 text-lg">
            Convert massive Bank Statements to Excel in seconds.
          </p>
        </header>

        <main>
          {status === 'idle' && (
            <FileUpload onUpload={handleUpload} disabled={false} />
          )}

          {(status === 'processing' || status === 'completed' || status === 'failed') && (
            <>
              <StatusDisplay
                status={status}
                progress={progress}
                message={message}
                onDownload={handleDownload}
              />
              {status !== 'processing' && (
                <div className="text-center mt-8">
                  <button
                    onClick={() => {
                      setStatus('idle');
                      setJobId(null);
                      setProgress(0);
                      setMessage('');
                    }}
                    className="text-slate-400 hover:text-white underline"
                  >
                    Convert Another File
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
