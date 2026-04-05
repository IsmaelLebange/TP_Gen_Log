import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert } from 'react-native';
import { Camera, CameraView, useCameraPermissions } from 'expo-camera';
import { COLORS } from '../../constants/theme';

export default function BiometricCapture({ onCapture }) {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef(null);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={{ textAlign: 'center', marginBottom: 10 }}>
          L'accès à la caméra est nécessaire pour la biométrie.
        </Text>
        <TouchableOpacity onPress={requestPermission} style={styles.btn}>
          <Text style={{ color: '#fff' }}>Autoriser la caméra</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
          base64: false,
          skipProcessing: false,
        });
        onCapture(photo.uri); // Envoie l'URI réelle du fichier temporaire
      } catch (e) {
        Alert.alert("Erreur", "Impossible de prendre la photo");
      }
    }
  };

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing="front" ref={cameraRef}>
        <View style={styles.overlay}>
          {/* Guide visuel pour le visage */}
          <View style={styles.faceOval} />
          <Text style={styles.instruction}>Placez votre visage dans le cadre</Text>
        </View>
      </CameraView>
      
      <TouchableOpacity style={styles.captureCircle} onPress={takePicture}>
        <View style={styles.innerCircle} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', borderRadius: 20, overflow: 'hidden' },
  camera: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  btn: { backgroundColor: COLORS.primary, padding: 15, borderRadius: 10 },
  overlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.2)' },
  faceOval: {
    width: 280,
    height: 380,
    borderWidth: 2,
    borderColor: COLORS.primary || '#007AFF',
    borderRadius: 150,
    borderStyle: 'dashed',
  },
  instruction: { color: '#fff', marginTop: 20, fontWeight: 'bold', backgroundColor: 'rgba(0,0,0,0.5)', padding: 5 },
  captureCircle: {
    position: 'absolute',
    bottom: 30,
    alignSelf: 'center',
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  innerCircle: { width: 60, height: 60, borderRadius: 30, backgroundColor: '#fff' }
});