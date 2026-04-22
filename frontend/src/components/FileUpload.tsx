'use client';

import { useRef, useState } from 'react';

import { uploadDocument } from '@/lib/api';

type UploadState = 'idle' | 'uploading' | 'success' | 'error';

export default function FileUpload() {
  const [state, setState] = useState<UploadState>('idle');
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setState('uploading');
    setMessage('');
    try {
      const result = await uploadDocument(file);
      setState('success');
      setMessage(`✓ ${result.filename} — ${result.chunks_created} chunks ingested`);
    } catch (err) {
      setState('error');
      setMessage(err instanceof Error ? err.message : 'Upload failed');
    }
    setTimeout(() => {
      setState('idle');
      setMessage('');
    }, 4000);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-lg border-2 border-dashed px-4 py-3 text-center text-xs transition-colors ${
          isDragging
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-200 text-gray-400 hover:border-gray-300 hover:bg-gray-50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".md,.csv"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
            e.target.value = '';
          }}
        />
        {state === 'uploading' ? (
          <span className="text-blue-600">Uploading…</span>
        ) : (
          <span>Drop a .md or .csv file to ingest, or click to browse</span>
        )}
      </div>
      {message && (
        <p
          className={`mt-1.5 text-xs ${
            state === 'error' ? 'text-red-600' : 'text-green-600'
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
}
