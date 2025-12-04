import React, { useCallback, useState } from 'react';

const FileUpload = ({ onUpload, disabled }) => {
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onUpload(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            onUpload(e.target.files[0]);
        }
    };

    return (
        <div
            className={`glass-panel p-10 text-center transition-all border-2 border-dashed ${dragActive ? 'border-blue-500 bg-slate-800' : 'border-slate-600'} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
        >
            <input
                type="file"
                id="file-upload"
                className="hidden"
                onChange={handleChange}
                accept=".pdf,.jpg,.jpeg,.png,.rpt"
                disabled={disabled}
            />
            <label htmlFor="file-upload" className="cursor-pointer w-full h-full flex flex-col items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-blue-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-xl font-semibold mb-2">Drag & Drop your Bank Statement</p>
                <p className="text-slate-400 text-sm">Supports PDF, RPT, and Images (JPEG/PNG)</p>
                <button className="mt-6 btn-primary" disabled={disabled}>
                    Browse Files
                </button>
            </label>
        </div>
    );
};

export default FileUpload;
