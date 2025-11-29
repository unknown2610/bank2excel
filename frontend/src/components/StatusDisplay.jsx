import React from 'react';
import { Loader2, CheckCircle, XCircle, FileSpreadsheet } from 'lucide-react';

const StatusDisplay = ({ status, progress, message, onDownload }) => {
    return (
        <div className="w-full max-w-md mx-auto text-center">
            <div className="mb-6 flex justify-center">
                {status === 'processing' && <Loader2 className="w-16 h-16 text-brand-500 animate-spin" />}
                {status === 'completed' && <CheckCircle className="w-16 h-16 text-green-500" />}
                {status === 'failed' && <XCircle className="w-16 h-16 text-red-500" />}
            </div>

            <h3 className="text-2xl font-bold text-slate-900 mb-2 capitalize">
                {status === 'processing' ? 'Processing...' : status}
            </h3>

            <p className="text-slate-500 mb-8">{message}</p>

            {status === 'processing' && (
                <div className="w-full bg-slate-100 rounded-full h-3 mb-2 overflow-hidden">
                    <div
                        className="bg-brand-500 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                    ></div>
                    <p className="text-right text-xs text-slate-400 mt-1">{progress}%</p>
                </div>
            )}

            {status === 'completed' && (
                <div className="animate-fade-in">
                    <button onClick={onDownload} className="btn-primary w-full flex items-center justify-center gap-2">
                        <FileSpreadsheet className="w-5 h-5" />
                        Download Excel File
                    </button>
                </div>
            )}

            {status === 'failed' && (
                <div className="text-red-500 bg-red-50 p-4 rounded-xl border border-red-100">
                    <p>Something went wrong. Please try again.</p>
                </div>
            )}
        </div>
    );
};

export default StatusDisplay;
