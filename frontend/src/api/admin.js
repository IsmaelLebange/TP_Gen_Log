import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

// Statistiques
export const fetchDashboardStats = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.stats);
    return response.data;
  } catch (error) {
    console.error("Erreur stats:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement statistiques");
  }
};

// Audit logs
export const fetchAuditLogs = async (params = {}) => {
  try {
    const response = await apiClient.get(ENDPOINTS.audit, { params });
    return response.data;
  } catch (error) {
    console.error("Erreur audit:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement logs");
  }
};

// Documents en attente
export const fetchPendingDocuments = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.validation, { params: { action: 'pending' } });
    return response.data;
  } catch (error) {
    console.error("Erreur documents pending:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement documents");
  }
};

// Documents par utilisateur
export const fetchDocumentsByUser = async (userId) => {
  try {
    const response = await apiClient.get(ENDPOINTS.validation, { params: { action: 'user', user_id: userId } });
    return response.data;
  } catch (error) {
    console.error("Erreur documents user:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement documents");
  }
};

// Valider un document
export const validateDocument = async (docId) => {
  try {
    const response = await apiClient.post(`${ENDPOINTS.validation}?action=validate&doc_id=${docId}`);
    return response.data;
  } catch (error) {
    console.error("Erreur validation:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur validation");
  }
};

// Rejeter un document
export const rejectDocument = async (docId, commentaire) => {
  try {
    const response = await apiClient.post(`${ENDPOINTS.validation}?action=reject&doc_id=${docId}`, { commentaire });
    return response.data;
  } catch (error) {
    console.error("Erreur rejet:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur rejet");
  }
};