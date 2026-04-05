import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; // ← correction ici
import { COLORS, SIZES } from '../../constants/theme';

export default function Header({ title, showBack = false, onBack, rightElement }) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.left}>
          {showBack && (
            <TouchableOpacity onPress={onBack} style={styles.backButton}>
              <Text style={styles.backText}>←</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.center}>
          <Text style={styles.title}>{title || "SEIP - RDC"}</Text>
        </View>

        <View style={styles.right}>
          {rightElement}
        </View>
      </View>
      {/* Barre décorative aux couleurs du drapeau */}
      <View style={styles.flagBar}>
        <View style={[styles.flagSection, { backgroundColor: '#007FFF' }]} />
        <View style={[styles.flagSection, { backgroundColor: '#F7D618', flex: 0.2 }]} />
        <View style={[styles.flagSection, { backgroundColor: '#CE1021' }]} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: COLORS.white, elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 2 },
  container: { height: 60, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: SIZES.padding },
  left: { width: 40 },
  center: { flex: 1, alignItems: 'center' },
  right: { width: 40, alignItems: 'flex-end' },
  title: { fontSize: 18, fontWeight: 'bold', color: COLORS.primary, letterSpacing: 1 },
  backText: { fontSize: 24, color: COLORS.primary, fontWeight: 'bold' },
  flagBar: { height: 3, flexDirection: 'row' },
  flagSection: { flex: 1, height: '100%' }
});