import type { Model } from '@/types';

// Models that disable streaming and require special UI treatment.
export const THINKING_MODELS = new Set<Model>(['o1-mini', 'o3-mini']);

// File types accepted for document ingestion — must stay in sync with backend ALLOWED_EXTENSIONS.
export const ACCEPTED_FILE_TYPES = '.md,.csv';
