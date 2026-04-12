import { useContext } from 'react';
import { AuthContext } from '../store/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth ne peut être utilisé qu\'à l\'intérieur d\'un AuthProvider');
  }
  return context;
};