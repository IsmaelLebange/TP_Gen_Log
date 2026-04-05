import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

export const loginAgent = async (login, password) => {
  try {
    const response = await apiClient.post(ENDPOINTS.login, {
      login: login,
      password: password,
    });
    
    // Django Rest Framework retourne souvent { access: "...", refresh: "..." }
    // Vérifie bien si ton controller renvoie "access" ou "token"
    return response.data; 
  } catch (error) {
    console.error("Erreur API Login:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Serveur injoignable");
  }
};