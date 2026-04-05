import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { COLORS } from '../../constants/theme';

export default function Label({ children, style }) {
  return <Text style={[styles.label, style]}>{children}</Text>;
}

const styles = StyleSheet.create({
  label: { fontSize: 14, fontWeight: '600', color: COLORS.gray, marginBottom: 5, marginLeft: 5 }
});