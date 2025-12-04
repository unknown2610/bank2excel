import React from 'react';

const StatusDisplay = ({ status, progress, message, onDownload, onReset }) => {
    const isProcessing = status === 'processing';
    const isCompleted = status === 'completed';
    const isFailed = status === 'failed';

    return (
        <div className="w-full text-center">
            <h2 className="text-2xl font-bold mb-6 text-slate-800">
                {isProcessing && 'Converting...'}
                {isCompleted && 'Success!'}
                {isFailed && 'Failed'}
            </h2>

            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-3 mb-4 overflow-hidden">
                <div
                    className={`h-3 rounded-full transition-all duration-500 ${isFailed ? 'bg-red-500' : 'bg-blue-600'
                        }`}
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            <div className="flex justify-between text-xs text-slate-500 mb-8 font-medium">
                <span>{progress}%</span>
                <span>{isProcessing ? 'Processing...' : isCompleted ? 'Done' : 'Error'}</span>
            </div>

            <p className="text-slate-600 mb-8 min-h-[1.5rem] font-medium">{message}</p>

            {isCompleted && (
                <button
                    onClick={onDownload}
                    className="w-full btn-primary flex items-center justify-center gap-2 mb-4"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Excel
                </button>
            )}

            {isFailed && (
                <div className="text-red-500 text-sm mb-6 bg-red-50 p-3 rounded-lg border border-red-100">
                    Conversion failed. Please try again.
                </div>
            )}

            {!isProcessing && (
                <button
                    onClick={onReset}
                    className="text-slate-500 hover:text-slate-800 underline text-sm font-medium transition-colors"
                >
                    Convert Another File
                </button>
            )}
        </div>
    );
};

export default StatusDisplay;
