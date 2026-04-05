import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';

export default function DocumentCard({ title, status, onPress }) {
  const isUploaded = status === 'uploaded';

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View>
        <Text style={styles.title}>{title}</Text>
        <Text style={[styles.status, { color: isUploaded ? COLORS.success : COLORS.danger }]}>
          {isUploaded ? '✅ Document chargé' : '❌ Manquant'}
        </Text>
      </View>
      <Text style={styles.actionText}>{isUploaded ? 'Modifier' : 'Ajouter'}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.white,
    padding: 15,
    borderRadius: SIZES.radius,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#eee',
  },
  title: { fontSize: 16, fontWeight: 'bold', color: COLORS.black },
  status: { fontSize: 12, marginTop: 4 },
  actionText: { color: COLORS.primary, fontWeight: '600' }
});