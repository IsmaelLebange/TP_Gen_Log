import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

export const fetchQRCode = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.qr);
    return response.data; // { nin, qr_code, owner }
  } catch (error) {
    console.error("Erreur QR:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Impossible de récupérer le QR code");
  }
};