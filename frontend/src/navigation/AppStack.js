import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import AdminDashboardScreen from '../screens/admin/AdminDashboardScreen';
import EnrollmentFormScreen from '../screens/enrollment/EnrollmentFormScreen';

const Stack = createStackNavigator();

export default function AppStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Dashboard" component={AdminDashboardScreen} options={{ title: 'Tableau de Bord SEIP' }} />
      <Stack.Screen name="NewEnrollment" component={EnrollmentFormScreen} options={{ title: 'Nouvel Enrôlement' }} />
    </Stack.Navigator>
  );
}