import React, { useState } from 'react';

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
            className={`w-full h-full min-h-[300px] flex flex-col items-center justify-center text-center transition-all border-2 border-dashed rounded-2xl p-8
            ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-slate-50/50'} 
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400 hover:bg-white'}`}
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
                <div className="bg-white p-4 rounded-full shadow-md mb-6">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                </div>
                <p className="text-xl font-bold text-slate-800 mb-2">Upload Bank Statement</p>
                <p className="text-slate-500 text-sm mb-6 max-w-xs mx-auto">
                    Drag & Drop PDF, RPT, or Image files here to start conversion
                </p>
                <span className="px-6 py-2 bg-white border border-slate-300 rounded-full text-slate-700 font-medium shadow-sm hover:shadow-md transition-all">
                    Browse Files
                </span>
            </label>
        </div>
    );
};

export default FileUpload;
