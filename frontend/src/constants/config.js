export const BASE_URL = 'http://10.201.22.103:8001/api';
export const MEDIA_BASE_URL = BASE_URL.replace('/api', '');

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
