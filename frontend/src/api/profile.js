import apiClient from './client';
import { ENDPOINTS } from '../constants/config';

export const fetchUserProfile = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.profile);
    return response.data;
  } catch (error) {
    console.error("Erreur fetch profil:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur chargement profil");
  }
};

export const updateUserProfile = async (data) => {
  try {
    const response = await apiClient.patch(ENDPOINTS.profile, data);
    return response.data;
  } catch (error) {
    console.error("Erreur mise à jour profil:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur mise à jour");
  }
};

export const addBiometricPhoto = async (base64Image) => {
  try {
    const response = await apiClient.post(ENDPOINTS.biometricPhoto, { image_base64: base64Image });
    return response.data;
  } catch (error) {
    console.error("Erreur ajout photo:", error.response?.data || error.message);
    throw error.response ? error.response.data : new Error("Erreur ajout photo");
  }
};