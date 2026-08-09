export interface Document {
  document_id: string;
  file_name: string;
  page_count: number;
}

export interface Source {
  document_id: string;
  file_name: string;
  page_number: number;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface PageResponse {
  document_id: string;
  page_number: number;
  text: string;
}

export interface TranslationResponse {
  document_id: string;
  page_number: number;
  original_text: string;
  translation: string;
}