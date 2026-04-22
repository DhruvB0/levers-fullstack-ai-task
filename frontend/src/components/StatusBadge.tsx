'use client';

import { useEffect, useState } from 'react';

import { checkHealth } from '@/lib/api';

export default function StatusBadge() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      const result = await checkHealth();
      if (!cancelled) setOnline(result);
    };

    poll();
    const interval = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (online === null) return null;

  return (
    <div
      className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
        online
          ? 'bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-400'
          : 'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-400'
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${online ? 'bg-green-500' : 'bg-red-500'}`}
      />
      {online ? 'Backend online' : 'Backend offline'}
    </div>
  );
}
