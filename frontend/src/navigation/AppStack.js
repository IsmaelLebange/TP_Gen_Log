import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { useAuth } from '../hooks/useAuth';
import AdminStack from './AdminStack';
import UserStack from './UserStack';
import AuthStack from './AuthStack';
import HomeScreen from '../screens/common/HomeScreen';

const Stack = createStackNavigator();

export default function AppStack() {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  if (!user) {
    return <AuthStack />;
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Admin" component={AdminStack} />
      <Stack.Screen name="User" component={UserStack} />
    </Stack.Navigator>
  );
}