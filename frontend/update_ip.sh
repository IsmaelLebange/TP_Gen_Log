#!/bin/bash
IP=$(hostname -I | awk '{print $1}')
echo "🚀 Configuration SEIP - IP : $IP"

cat <<EOT > src/constants/config.js
export const BASE_URL = 'http://$IP:8001/api';

export const ENDPOINTS = {
    // Routes Main (Authentification) -> /api/main_auth/...
    login: '/main_auth/login/',
    register: '/main_auth/register/',
    logout: '/main_auth/logout/',
    tokenRefresh: '/main_token/refresh/',
    tokenVerify: '/main_token/verify/',
    partnerVerify: '/main_verify/',
    
    // Routes Citoyen (Enrôlement) -> /api/citoyen_enrollment/...
    enrollment: '/citoyen_enrollment/',
    enrollmentComplete: '/citoyen_enrollment/complete/',
    biometric: '/citoyen_biometric/',
    documents: '/citoyen_documents/',
    qr: '/citoyen_qr/',
    credential: '/citoyen_credential/',
    passwordReset: '/citoyen_password-reset/',
    
    // Routes Admin (Audit & Stats) -> /api/admin_validation/...
    validation: '/admin_validation/',
    stats: '/admin_stats/',
    audit: '/admin_audit/',
};
EOT
echo "✅ src/constants/config.js généré avec succès."
