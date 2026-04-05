import React from 'react';
import { View, StyleSheet } from 'react-native';
import Label from '../atoms/Label';
import Input from '../atoms/Input';

export default function FormField({ label, placeholder, value, onChangeText, ...props }) {
  return (
    <View style={styles.container}>
      {label && <Label>{label}</Label>}
      <Input 
        placeholder={placeholder} 
        value={value} 
        onChangeText={onChangeText} 
        {...props} // Attention : vérifie que dans EnrollmentFormScreen tu n'envoies pas de bêtises ici
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 10,
    width: '100%',
  }
});