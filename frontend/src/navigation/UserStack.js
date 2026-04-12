import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import DashboardScreen from '../screens/citizen/DashboardScreen';
import ProfileScreen from '../screens/citizen/ProfileScreen';
import QRScreen from '../screens/citizen/QRScreen';
import DocumentUploadScreen from '../screens/enrollment/DocumentUploadScreen';
import EnrollmentFormScreen from '../screens/enrollment/EnrollmentFormScreen';
import BiometricScreen from '../screens/enrollment/BiometricScreen';
import SuccessScreen from '../screens/enrollment/SuccessScreen';

const Stack = createStackNavigator();

export default function UserStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Dashboard" component={DashboardScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
      <Stack.Screen name="QRScreen" component={QRScreen} />
      <Stack.Screen name="DocumentUpload" component={DocumentUploadScreen} />
      <Stack.Screen name="EnrollmentForm" component={EnrollmentFormScreen} />
      <Stack.Screen name="BiometricScreen" component={BiometricScreen} />
      <Stack.Screen name="SuccessScreen" component={SuccessScreen} />
    </Stack.Navigator>
  );
}