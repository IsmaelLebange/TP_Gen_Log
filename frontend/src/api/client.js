import axios from 'axios';
import { BASE_URL } from '../constants/config';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { eventBus } from '../utils/eventBus';

const storage = Platform.OS === 'web' ? localStorage : AsyncStorage;

const getItem = async (key) => {
  if (Platform.OS === 'web') return storage.getItem(key);
  return await storage.getItem(key);
};

const removeItem = async (key) => {
  if (Platform.OS === 'web') storage.removeItem(key);
  else await storage.removeItem(key);
};

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 50000,
});

apiClient.interceptors.request.use(async (config) => {
  const token = await getItem('userToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await removeItem('userToken');
      await removeItem('userData');
      eventBus.emit('unauthorized');
      if (Platform.OS === 'web') window.location.href = '/';
      return Promise.reject(new Error('Session expirée'));
    }
    return Promise.reject(error);
  }
);

const publicClient = axios.create({
  baseURL: BASE_URL,
  timeout: 50000,
});

export { apiClient, publicClient };
export default apiClient;