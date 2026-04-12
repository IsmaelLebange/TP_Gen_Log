import React, { createContext, useReducer, useEffect, useMemo } from 'react';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { eventBus } from '../utils/eventBus';

export const AuthContext = createContext();

const initialState = { isLoading: true, userToken: null, user: null };

const authReducer = (state, action) => {
  switch (action.type) {
    case 'RESTORE_TOKEN':
      return { ...state, userToken: action.token, user: action.user, isLoading: false };
    case 'SIGN_IN':
      return { ...state, userToken: action.token, user: action.user, isLoading: false };
    case 'SIGN_OUT':
      return { ...state, userToken: null, user: null, isLoading: false };
    default:
      return state;
  }
};

const storage = Platform.OS === 'web' ? localStorage : AsyncStorage;

const getItem = async (key) => {
  if (Platform.OS === 'web') return storage.getItem(key);
  return await storage.getItem(key);
};

const setItem = async (key, value) => {
  if (Platform.OS === 'web') storage.setItem(key, value);
  else await storage.setItem(key, value);
};

const removeItem = async (key) => {
  if (Platform.OS === 'web') storage.removeItem(key);
  else await storage.removeItem(key);
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const bootstrapAsync = async () => {
      let userToken = null, user = null;
      try {
        const token = await getItem('userToken');
        const userData = await getItem('userData');
        if (token && userData) {
          userToken = token;
          user = JSON.parse(userData);
        }
      } catch (e) { console.log("Erreur restauration", e); }
      dispatch({ type: 'RESTORE_TOKEN', token: userToken, user });
    };
    bootstrapAsync();
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => {
      dispatch({ type: 'SIGN_OUT' });
    };
    eventBus.on('unauthorized', handleUnauthorized);
    return () => eventBus.off('unauthorized', handleUnauthorized);
  }, []);

  const authContext = useMemo(() => ({
    signIn: async (token, user) => {
      await setItem('userToken', token);
      await setItem('userData', JSON.stringify(user));
      dispatch({ type: 'SIGN_IN', token, user });
    },
    signOut: async () => {
      await removeItem('userToken');
      await removeItem('userData');
      dispatch({ type: 'SIGN_OUT' });
    },
  }), []);

  return (
    <AuthContext.Provider value={{ ...authContext, ...state }}>
      {children}
    </AuthContext.Provider>
  );
};