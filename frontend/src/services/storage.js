import AsyncStorage from '@react-native-async-storage/async-storage';

export const saveToken = async (token) => {
  try {
    await AsyncStorage.setItem('@auth_token', token);
  } catch (e) {
    console.error("Erreur sauvegarde token", e);
  }
};

export const getToken = async () => {
  return await AsyncStorage.getItem('@auth_token');
};

export const clearStorage = async () => {
  await AsyncStorage.clear();
};