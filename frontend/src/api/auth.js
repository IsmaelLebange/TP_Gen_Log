import { publicClient } from './client';
import { ENDPOINTS } from '../constants/config';

export const loginAgent = async (login, password) => {
  try {
    const response = await publicClient.post(ENDPOINTS.login, {
      login: login,
      password: password,
    });
    return response.data;
  } catch (error) {
    console.error("Erreur API Login:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Serveur injoignable");
  }
};