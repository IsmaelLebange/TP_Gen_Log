import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';

import AdminDashboardScreen from '../screens/admin/AdminDashboardScreen';
import AuditLogScreen from '../screens/admin/AuditLogScreen';
import DocumentValidationScreen from '../screens/admin/DocumentValidationScreen';
import StatisticsScreen from '../screens/admin/StatisticsScreen';

// Écrans citoyens (pour admin)
import EnrollmentFormScreen from '../screens/enrollment/EnrollmentFormScreen';
import QRScreen from '../screens/citizen/QRScreen';
import BiometricScreen from '../screens/enrollment/BiometricScreen';
import SuccessScreen from '../screens/enrollment/SuccessScreen';
import DocumentUploadScreen from '../screens/enrollment/DocumentUploadScreen';

const Stack = createStackNavigator();

export default function AdminStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="AdminDashboard" component={AdminDashboardScreen} />
      <Stack.Screen name="AuditLog" component={AuditLogScreen} />
      <Stack.Screen name="DocumentValidation" component={DocumentValidationScreen} />
      <Stack.Screen name="Statistics" component={StatisticsScreen} />
      {/* Écrans citoyens */}
      <Stack.Screen name="EnrollmentForm" component={EnrollmentFormScreen} />
      <Stack.Screen name="QRScreen" component={QRScreen} />
      <Stack.Screen name="BiometricScreen" component={BiometricScreen} />
      <Stack.Screen name="SuccessScreen" component={SuccessScreen} />
      <Stack.Screen name="DocumentUpload" component={DocumentUploadScreen} />
    </Stack.Navigator>
  );
}