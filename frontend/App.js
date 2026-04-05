import React from 'react';
import { AuthProvider } from './src/store/AuthContext';
import Navigation from './src/navigation/index';

export default function App() {
  return (
    <AuthProvider>
      <Navigation />
    </AuthProvider>
  );
}