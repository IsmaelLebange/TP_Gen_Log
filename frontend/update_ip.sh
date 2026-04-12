#!/bin/bash

# On récupère l'IP que Expo utilise actuellement pour le serveur Metro
# On cherche l'IP dans les logs ou via la commande expo
IP=$(npx expo start --offline --dry-run 2>&1 | grep -oE 'exp://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | cut -d'/' -f3 | cut -d':' -f1 | head -n 1)

# Si Expo ne répond pas (projet éteint), on prend l'IP de la route par défaut (la plus fiable sur Linux)
if [ -z "$IP" ]; then
    IP=$(ip route get 1 | awk '{print $(NF-2);exit}')
fi

echo "🚀 Synchronisation SEIP - IP Réseau : $IP"

# Nettoyage et réécriture forcée
cat <<EOT > src/constants/config.js
export const BASE_URL = 'http://$IP:8001/api';

export const ENDPOINTS = {
    login: '/main_auth/login/',
    register: '/main_auth/register/',
    logout: '/main_auth/logout/',
    tokenRefresh: '/main_token/refresh/',
    tokenVerify: '/main_token/verify/',
    partnerVerify: '/main_verify/',
    
    enrollment: '/citoyen_enrollment/',
    enrollmentComplete: '/citoyen_enrollment/complete/',
    biometric: '/citoyen_biometric/',
    biometricPhoto: '/citoyen_biometric/?action=photo',
    biometricVerifyPhoto: '/citoyen_biometric/?action=verify',
    documents: '/citoyen_documents/',
    qr: '/citoyen_qr/',
    credential: '/citoyen_credential/',
    passwordReset: '/citoyen_password-reset/',
    
    validation: '/admin_validation/',
    stats: '/admin_stats/',
    audit: '/admin_audit/',
    profile: '/citoyen_profile/',
};
EOT

echo "✅ Config synchronisée sur http://$IP:8001/api"