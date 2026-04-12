import React, { useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera"; 
import * as LocalAuthentication from "expo-local-authentication";
import * as FileSystem from "expo-file-system/legacy";
import * as ImageManipulator from "expo-image-manipulator";
import { COLORS } from "../../constants/theme";
import client from "../../api/client";
import { ENDPOINTS } from "../../constants/config";
import Button from "../../components/atoms/Button";

export default function BiometricScreen({ route, navigation }) {
  const { enrollmentData } = route.params;

  const [permission, requestPermission] = useCameraPermissions();
  const [photoUri, setPhotoUri] = useState(null);
  const [fingerprintDone, setFingerprintDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [facing, setFacing] = useState("front"); 
  const [flash, setFlash] = useState("off"); 
  const cameraRef = useRef(null);

  // 1. Validation Empreinte (Locale)
  const handleFingerprint = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    if (!hasHardware) {
      return Alert.alert("Erreur", "Capteur d'empreinte non détecté sur ce HP/Téléphone.");
    }
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: "Validation biométrique SEIP",
    });
    if (result.success) {
      setFingerprintDone(true);
      Alert.alert("Succès", "Empreinte validée.");
    }
  };

  // 2. Traitement Image (Crop & Resize)
  const resizeAndCrop = async (uri) => {
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [{ resize: { width: 800 } }], // Resize simple pour garder le ratio
      { compress: 0.7, format: ImageManipulator.SaveFormat.JPEG }
    );
    return result.uri;
  };

  // 3. Capture
  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
        });
        const resizedUri = await resizeAndCrop(photo.uri);
        setPhotoUri(resizedUri);
      } catch (e) {
        Alert.alert("Erreur", "Impossible de prendre la photo.");
      }
    }
  };

  // 4. Envoi Final à Django
  const handleFinalSubmit = async () => {
    if (!photoUri || !fingerprintDone) {
      return Alert.alert("Attention", "Photo et Empreinte obligatoires !");
    }

    setLoading(true);
    try {
      const base64Content = await FileSystem.readAsStringAsync(photoUri, {
        encoding: FileSystem.EncodingType ? FileSystem.EncodingType.Base64 : 'base64',
      });

      const finalPayload = {
        ...enrollmentData,
        biometric_image: `data:image/jpeg;base64,${base64Content}`,
        biometric_type: "face",
      };

      const response = await client.post(ENDPOINTS.enrollmentComplete, finalPayload);
      
      Alert.alert(
        "Félicitations",
        `Citoyen enrôlé ! NIN : ${response.data.nin || 'Généré'}`,
        [{ text: "Terminer", onPress: () => navigation.navigate("SuccessScreen") }]
      );
    } catch (error) {
      console.error("Erreur Envoi:", error.response?.data || error.message);
      Alert.alert("Erreur Serveur", "Vérifie ton IP dans config.js ou ta console Django.");
    } finally {
      setLoading(false);
    }
  };

  if (!permission) return <View style={styles.center}><ActivityIndicator size="large" color={COLORS.primary} /></View>;
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.textInfo}>L'accès caméra est requis pour le SEIP.</Text>
        <Button title="Autoriser la caméra" onPress={requestPermission} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!photoUri ? (
        <View style={{ flex: 1 }}>
          <CameraView
            style={StyleSheet.absoluteFillObject}
            facing={facing}
            flash={flash}
            ref={cameraRef}
          />
          
          <View style={styles.overlay}>
            {/* Guide Visage */}
            <View style={styles.faceGuide} />
            
            {/* Contrôles Haut */}
            <View style={styles.topControls}>
              <TouchableOpacity
                style={styles.iconBtn}
                onPress={() => setFacing(prev => prev === "front" ? "back" : "front")}
              >
                <Text style={styles.iconText}>🔄</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.iconBtn}
                onPress={() => setFlash(prev => prev === "off" ? "on" : "off")}
              >
                <Text style={styles.iconText}>{flash === "on" ? "⚡" : "🌑"}</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.guideText}>Cadrez le visage du citoyen</Text>

            {/* Bouton Capture */}
            <TouchableOpacity style={styles.snap} onPress={takePicture}>
              <View style={styles.snapInner} />
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.reviewContainer}>
          <Text style={styles.title}>Vérification Biométrique</Text>
          
          <View style={styles.cropWrapper}>
            <Image source={{ uri: photoUri }} style={styles.preview} />
          </View>

          <TouchableOpacity
            style={[styles.fingerprintBtn, fingerprintDone && styles.btnSuccess]}
            onPress={handleFingerprint}
            disabled={loading}
          >
            <Text style={styles.btnText}>
              {fingerprintDone ? "✓ EMPREINTE CAPTURÉE" : "CAPTURER L'EMPREINTE"}
            </Text>
          </TouchableOpacity>

          <View style={styles.row}>
            <TouchableOpacity
              style={styles.btnRetry}
              onPress={() => { setPhotoUri(null); setFingerprintDone(false); }}
              disabled={loading}
            >
              <Text style={styles.btnRetryText}>REPRENDRE</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.btnConfirm, (!fingerprintDone || loading) && styles.btnDisabled]}
              onPress={handleFinalSubmit}
              disabled={!fingerprintDone || loading}
            >
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnConfirmText}>ENRÔLER</Text>}
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  textInfo: { color: "#fff", marginBottom: 20, textAlign: 'center' },
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "center", alignItems: "center" },
  topControls: { position: 'absolute', top: 50, flexDirection: 'row', justifyContent: 'space-between', width: '80%' },
  iconBtn: { width: 50, height: 50, borderRadius: 25, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: 'center', alignItems: 'center' },
  iconText: { fontSize: 22, color: '#fff' },
  faceGuide: { width: 260, height: 320, borderWidth: 2, borderColor: "rgba(255,255,255,0.8)", borderRadius: 130, borderStyle: "dashed" },
  guideText: { color: "#fff", marginTop: 20, backgroundColor: "rgba(0,0,0,0.7)", padding: 8, borderRadius: 5 },
  snap: { position: "absolute", bottom: 50, width: 80, height: 80, borderRadius: 40, backgroundColor: "rgba(255,255,255,0.3)", justifyContent: 'center', alignItems: 'center' },
  snapInner: { width: 65, height: 65, borderRadius: 32.5, backgroundColor: "#fff" },
  reviewContainer: { flex: 1, backgroundColor: "#F5F7FA", padding: 25, alignItems: "center", justifyContent: "center" },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 20, color: COLORS.primary },
  cropWrapper: { width: 200, height: 200, borderRadius: 100, overflow: "hidden", borderWidth: 4, borderColor: COLORS.primary, marginBottom: 30 },
  preview: { width: "100%", height: "130%", top: -10 },
  fingerprintBtn: { width: "100%", padding: 18, backgroundColor: "#2C3E50", borderRadius: 12, alignItems: "center", marginBottom: 20 },
  btnSuccess: { backgroundColor: "#27AE60" },
  btnText: { color: "#fff", fontWeight: "bold" },
  row: { flexDirection: "row", gap: 15 },
  btnRetry: { flex: 1, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: "#BDC3C7", alignItems: "center" },
  btnRetryText: { color: "#7F8C8D", fontWeight: "600" },
  btnConfirm: { flex: 1, padding: 16, borderRadius: 12, backgroundColor: COLORS.primary, alignItems: "center" },
  btnConfirmText: { color: "#fff", fontWeight: "bold" },
  btnDisabled: { backgroundColor: "#BDC3C7" },
});