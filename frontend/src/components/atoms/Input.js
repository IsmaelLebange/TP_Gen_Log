import React from 'react';
import { TextInput, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';

export default function Input({ placeholder, value, onChangeText, secureTextEntry, ...props }) {
  // On s'assure que value est TOUJOURS une string, jamais null ou undefined
  const safeValue = value ? String(value) : "";
  
  // On force le booléen pour secureTextEntry
  const isSecure = !!secureTextEntry;

  return (
    <TextInput
      style={styles.input}
      placeholder={placeholder}
      placeholderTextColor={COLORS.gray || '#999'}
      onChangeText={onChangeText}
      {...props} // On met props ici
      value={safeValue} // On écrase avec la valeur sécurisée
      secureTextEntry={isSecure} // On écrase avec le booléen pur
    />
  );
}

const styles = StyleSheet.create({
  input: {
    width: '100%',
    height: 55,
    backgroundColor: '#fff',
    borderRadius: SIZES.radius,
    paddingHorizontal: 15,
    borderWidth: 1,
    // Sécurité au cas où COLORS.lightGray est indéfini
    borderColor: COLORS.lightGray || '#E0E0E0', 
    marginBottom: 15,
    fontSize: 16,
    color: COLORS.text,
    // Ajout d'une ombre légère pour le style "Elite"
    elevation: 2, 
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
});