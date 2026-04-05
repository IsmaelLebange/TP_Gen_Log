import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';

export default function Footer() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>© 2026 Office National d'Identification</Text>
      <Text style={styles.subText}>République Démocratique du Congo</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: SIZES.padding,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    marginTop: 20,
  },
  text: { fontSize: 12, color: COLORS.gray, fontWeight: '600' },
  subText: { fontSize: 10, color: COLORS.gray, marginTop: 2, textTransform: 'uppercase' }
});