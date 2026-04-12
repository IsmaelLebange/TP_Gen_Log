import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS } from '../../constants/theme';

export default function SuccessScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>✅</Text>
      <Text style={styles.title}>Enrôlement réussi !</Text>
      <Text style={styles.message}>Le citoyen a été enregistré avec succès.</Text>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('Home')} // ou 'EnrollmentForm'
      >
        <Text style={styles.buttonText}>Retour à l'accueil</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', padding: 20 },
  emoji: { fontSize: 64, marginBottom: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: COLORS.primary, marginBottom: 10 },
  message: { fontSize: 16, textAlign: 'center', marginBottom: 30, color: '#555' },
  button: { backgroundColor: COLORS.primary, paddingHorizontal: 30, paddingVertical: 12, borderRadius: 8 },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});