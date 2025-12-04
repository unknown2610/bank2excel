import React from 'react';

const StatusDisplay = ({ status, progress, message, onDownload }) => {
    return (
        <div className="glass-panel p-8 mt-8 w-full max-w-2xl mx-auto">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold capitalize">{status === 'processing' ? 'Converting...' : status}</h3>
                <span className="text-blue-400 font-mono">{progress}%</span>
            </div>

            <div className="w-full bg-slate-700 rounded-full h-2.5 mb-6 overflow-hidden">
                <div
                    className="bg-gradient-to-r from-blue-500 to-violet-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            <p className="text-slate-300 text-center mb-6">{message}</p>

            {status === 'completed' && (
                <div className="text-center">
                    <button onClick={onDownload} className="btn-primary">
                        Download Excel File
                    </button>
                </div>
            )}

            {status === 'failed' && (
                <div className="text-center text-red-400">
                    <p>Conversion failed. Please try again.</p>
                </div>
            )}
        </div>
    );
};

export default StatusDisplay;
