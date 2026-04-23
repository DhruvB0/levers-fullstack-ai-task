'use client';

import { useEffect, useState } from 'react';

import { deleteDocument, listDocuments } from '@/lib/api';
import type { DocumentInfo } from '@/types';

interface Props {
  refreshTrigger: number;
}

export default function DocumentList({ refreshTrigger }: Props) {
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listDocuments()
      .then((data) => { if (!cancelled) setDocs(data); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [refreshTrigger]);

  const handleDelete = async (filename: string) => {
    setDeleting(filename);
    try {
      await deleteDocument(filename);
      const data = await listDocuments();
      setDocs(data);
    } catch {
      // deletion failed — list stays unchanged
    } finally {
      setDeleting(null);
    }
  };

  if (docs.length === 0) return null;

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-2">
      <p className="mb-1.5 text-xs font-medium text-gray-500 dark:text-gray-400">
        Knowledge base · {docs.length} {docs.length === 1 ? 'file' : 'files'}
      </p>
      <div className="flex max-h-28 flex-col gap-1 overflow-y-auto">
        {docs.map((doc) => (
          <div
            key={doc.filename}
            className="flex items-center justify-between rounded-md bg-gray-50 dark:bg-gray-900 px-2.5 py-1"
          >
            <div className="min-w-0 flex-1">
              <span className="block truncate text-xs text-gray-700 dark:text-gray-300">
                {doc.filename}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {doc.chunk_count} {doc.chunk_count === 1 ? 'chunk' : 'chunks'}
              </span>
            </div>
            <button
              onClick={() => handleDelete(doc.filename)}
              disabled={deleting === doc.filename}
              className="ml-2 flex h-5 w-5 shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950 dark:hover:text-red-400 disabled:opacity-40 transition-colors"
              aria-label={`Delete ${doc.filename}`}
            >
              {deleting === doc.filename ? (
                <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
              ) : (
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
