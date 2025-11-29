import React, { useState } from 'react';
import { FileSpreadsheet, UploadCloud } from 'lucide-react';

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
            className={`relative rounded-2xl p-10 text-center transition-all border-2 border-dashed 
                ${dragActive ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-brand-400'} 
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
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
                accept=".pdf,.jpg,.jpeg,.png"
                disabled={disabled}
            />
            <label htmlFor="file-upload" className="cursor-pointer w-full h-full flex flex-col items-center justify-center">
                <div className="bg-brand-50 p-4 rounded-full mb-4">
                    <FileSpreadsheet className="w-10 h-10 text-brand-600" />
                </div>
                <div className="bg-white px-4 py-2 rounded-lg shadow-sm border border-slate-100 flex items-center gap-3 mb-4">
                    <div className="bg-red-100 p-1.5 rounded">
                        <span className="text-xs font-bold text-red-600">PDF</span>
                    </div>
                    <ArrowRightIcon />
                    <div className="bg-green-100 p-1.5 rounded">
                        <span className="text-xs font-bold text-green-600">XLS</span>
                    </div>
                </div>

                <p className="text-xl font-semibold text-slate-900 mb-2">Drag & drop your statement</p>
                <p className="text-slate-500 text-sm mb-6">Supports PDF (up to 2000 pages) and Images</p>

                <button className="btn-primary w-full" disabled={disabled}>
                    Select File
                </button>
            </label>
        </div>
    );
};

const ArrowRightIcon = () => (
    <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
    </svg>
);

export default FileUpload;
