import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';

// Imports des écrans
import LoginScreen from '../screens/auth/LoginScreen';
import EnrollmentFormScreen from '../screens/enrollment/EnrollmentFormScreen';
import BiometricScreen from '../screens/enrollment/BiometricScreen'; // <--- IMPORTANT

const Stack = createStackNavigator();

export default function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen 
        name="PreEnrollment" 
        component={EnrollmentFormScreen} 
        options={{ headerShown: true, title: 'Infos Citoyen' }} 
      />
      <Stack.Screen 
        name="BiometricScreen" 
        component={BiometricScreen} 
        options={{ headerShown: true, title: 'Capture Biométrique' }} 
      />
    </Stack.Navigator>
  );
}