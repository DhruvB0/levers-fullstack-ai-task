'use client';

import type { Model } from '@/types';

interface Props {
  model: Model;
  setModel: (model: Model) => void;
  streamingEnabled: boolean;
  setStreamingEnabled: (enabled: boolean) => void;
}

export default function ControlBar({
  model,
  setModel,
  streamingEnabled,
  setStreamingEnabled,
}: Props) {
  return (
    <div className="flex items-center gap-4 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-2">
      <div className="flex items-center gap-2">
        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Model</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value as Model)}
          className="rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 px-2 py-1 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="gpt-4o-mini">gpt-4o-mini (fast)</option>
          <option value="o1-mini">o1-mini (thinking)</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Streaming</label>
        <button
          onClick={() => setStreamingEnabled(!streamingEnabled)}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
            streamingEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
          }`}
          role="switch"
          aria-checked={streamingEnabled}
        >
          <span
            className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
              streamingEnabled ? 'translate-x-4' : 'translate-x-1'
            }`}
          />
        </button>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {streamingEnabled ? 'On' : 'Off'}
        </span>
      </div>
    </div>
  );
}
