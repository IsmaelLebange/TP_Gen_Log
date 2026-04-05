import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

export const createEnrollment = async (formData) => {
  try {
    const response = await apiClient.post(ENDPOINTS.enrollment, formData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : new Error("Erreur lors de l'enrôlement");
  }
};

export const createCompleteEnrollment = async (fullData) => {
  try {
    const response = await apiClient.post(ENDPOINTS.enrollmentComplete, fullData);
    return response.data;
  } catch (error) {
    console.error("Erreur Enrôlement Complet:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur serveur lors de l'enrôlement");
  }
};