export type Role = 'user' | 'assistant';

export type Model = 'gpt-4o-mini' | 'o1-mini';

export interface Message {
  id: string;
  role: Role;
  content: string;
  sources?: string[];
  isStreaming?: boolean;
}

export interface ChatRequest {
  query: string;
  model: Model;
  stream: boolean;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  rag_used: boolean;
}

export interface IngestResponse {
  filename: string;
  chunks_created: number;
  message: string;
}
