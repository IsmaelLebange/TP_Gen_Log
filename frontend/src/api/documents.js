import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

// Récupérer tous les documents de l'utilisateur connecté
export const fetchUserDocuments = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.documents);
    return response.data;
  } catch (error) {
    console.error("Erreur fetch documents:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement documents");
  }
};

// Récupérer un document spécifique
export const fetchDocumentById = async (docId) => {
  try {
    const response = await apiClient.get(`${ENDPOINTS.documents}?id=${docId}`);
    return response.data;
  } catch (error) {
    console.error("Erreur fetch document:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Document introuvable");
  }
};

// Upload d'un nouveau document (multipart/form-data)
export const uploadDocument = async (formData) => {
  try {
    const response = await apiClient.post(ENDPOINTS.documents, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error("Erreur upload document:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Échec de l'upload");
  }
};

// Supprimer un document
export const deleteDocument = async (docId) => {
  try {
    const response = await apiClient.delete(`${ENDPOINTS.documents}?id=${docId}`);
    return response.data;
  } catch (error) {
    console.error("Erreur suppression document:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Échec de la suppression");
  }
};