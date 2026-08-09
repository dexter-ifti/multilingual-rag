import axios from "axios";

import type {
  ChatResponse,
  Document,
  PageResponse,
  TranslationResponse,
} from "../types/api";

const api = axios.create({
  baseURL: "http://localhost:8000",
});


export async function getDocuments(): Promise<Document[]> {
  const response = await api.get("/documents");

  return response.data.documents;
}


export async function uploadDocuments(
  files: File[],
): Promise<Document[]> {

  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  const response = await api.post(
    "/documents/upload",
    formData,
  );

  return response.data.documents;
}


export async function askQuestion(
  question: string,
): Promise<ChatResponse> {

  const response = await api.post(
    "/chat",
    {
      question,
    },
  );

  return response.data;
}


export async function getPage(
  documentId: string,
  pageNumber: number,
): Promise<PageResponse> {

  const response = await api.get(
    `/documents/${documentId}/pages/${pageNumber}`,
  );

  return response.data;
}


export async function translatePage(
  documentId: string,
  pageNumber: number,
): Promise<TranslationResponse> {

  const response = await api.post(
    `/documents/${documentId}/pages/${pageNumber}/translate`,
  );

  return response.data;
}


export function getPdfUrl(
  documentId: string,
): string {

  return (
    `http://localhost:8000` +
    `/documents/${documentId}/file`
  );
}