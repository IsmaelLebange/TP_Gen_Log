import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useAuth } from '../hooks/useAuth';
import AuthStack from './AuthStack';
import AppStack from './AppStack';
import { View, ActivityIndicator, Platform } from 'react-native';
import { navigationRef } from '../utils/navigationRef';

// Configuration du linking pour le web uniquement
const linking = {
  // On utilise '/' pour que le navigateur prenne l'URL de base dynamique
  prefixes: ['/', 'http://localhost:8081'],
  config: {
    screens: {
      Home: 'accueil',
      Login: 'connexion',
      PreEnrollment: 'pre-enrollement',
      AdminDashboard: 'admin',
      Dashboard: 'mon-compte',
      QRScreen: 'ma-carte',
      DocumentUpload: 'mes-documents',
      // Ajoute d'autres routes si nécessaire
    },
  },
};

export default function Navigation() {
  const { userToken, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#007FFF" />
      </View>
    );
  }

  return (
    <NavigationContainer
      ref={navigationRef}
      linking={Platform.OS === 'web' ? linking : undefined}
    >
      {userToken ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
}