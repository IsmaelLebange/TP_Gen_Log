import client from './client';
import { ENDPOINTS } from '../constants/config';

// On s'assure que les 3 paramètres sont bien définis
export const enrollBiometric = async (type, imageBase64, citoyenId) => {
    return client.post(`${ENDPOINTS.biometric}?action=enroll`, {
        type: type,
        image: imageBase64,
        citoyen_id: citoyenId, // Le backend attend citoyen_id (avec underscore)
    });
};

export const getBiometricStatus = async () => {
    return client.get(`${ENDPOINTS.biometric}?action=status`);
};