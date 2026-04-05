
import React, { createContext, useReducer, useEffect, useMemo } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(
    (prevState, action) => {
      switch (action.type) {
        case 'RESTORE_TOKEN':
          return { ...prevState, userToken: action.token, isLoading: false };
        case 'SIGN_IN':
          return { ...prevState, userToken: action.token, isLoading: false };
        case 'SIGN_OUT':
          return { ...prevState, userToken: null, isLoading: false };
      }
    },
    { isLoading: true, userToken: null }
  );

  useEffect(() => {
    const bootstrapAsync = async () => {
      let userToken = null;
      try {
        userToken = await AsyncStorage.getItem('userToken');
      } catch (e) {
        console.log("Erreur de restauration");
      }
      // CRUCIAL : On dispatch toujours pour passer isLoading à false
      dispatch({ type: 'RESTORE_TOKEN', token: userToken });
    };
    bootstrapAsync();
  }, []);

  const authContext = useMemo(() => ({
    signIn: async (token) => {
      await AsyncStorage.setItem('userToken', token);
      dispatch({ type: 'SIGN_IN', token: token });
    },
    signOut: async () => {
      await AsyncStorage.removeItem('userToken');
      dispatch({ type: 'SIGN_OUT' });
    },
  }), []);

  return (
    <AuthContext.Provider value={{ ...authContext, ...state }}>
      {children}
    </AuthContext.Provider>
  );
};