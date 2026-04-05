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
import * as ImageManipulator from 'expo-image-manipulator';
import { COLORS } from "../../constants/theme";
import client from "../../api/client";
import { ENDPOINTS } from "../../constants/config";
import Button from "../../components/atoms/Button";

export default function BiometricScreen({ route, navigation }) {
  // On récupère les données civiles de l'écran précédent
  const { enrollmentData } = route.params;
  
  const [permission, requestPermission] = useCameraPermissions();
  const [photoUri, setPhotoUri] = useState(null);
  const [fingerprintDone, setFingerprintDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const cameraRef = useRef(null);

  // 1. Validation Empreinte (Locale au téléphone)
  const handleFingerprint = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    if (!hasHardware) {
      return Alert.alert("Erreur", "Capteur d'empreinte non détecté.");
    }
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: "Validation biométrique SEIP",
    });
    if (result.success) {
      setFingerprintDone(true);
      Alert.alert("Succès", "Empreinte validée localement.");
    }
  };

  

const resizeAndCrop = async (uri) => {
  const result = await ImageManipulator.manipulateAsync(
    uri,
    [{ resize: { width: 800, height: 600 } }], // redimensionnement
    { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
  );
  return result.uri;
};

  // 2. Capture de la photo
  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8, // On compresse un peu pour le réseau
        skipProcessing: false, // On veut que l'image soit traitée pour la redimension
      });
const resizedUri = await resizeAndCrop(photo.uri); // On redimensionne et recadre l'image avant de l'envoyer
setPhotoUri(resizedUri);
    }
  };

  // 3. LE GRAND FINAL : Envoi Atomique (Civil + Bio)
  const handleFinalSubmit = async () => {
    if (!photoUri || !fingerprintDone) {
      return Alert.alert("Attention", "La photo et l'empreinte sont obligatoires.");
    }

    setLoading(true);
    try {
      console.log("🚀 Conversion de la photo...");
      const base64Content = await FileSystem.readAsStringAsync(photoUri, {
        encoding: "base64",
      });
      const dataUri = `data:image/jpeg;base64,${base64Content}`;

      // On prépare le paquet complet pour le EnrollmentCompleteController
      const finalPayload = {
        ...enrollmentData,        // Nom, Prénom, Email, etc.
        biometric_image: dataUri, // La photo face
        biometric_type: "face"    // Type par défaut
      };

      console.log("📡 Envoi de l'enrôlement complet à :", ENDPOINTS.enrollmentComplete);
      
      const response = await client.post(ENDPOINTS.enrollmentComplete, finalPayload);

      console.log("✅ Réponse Serveur :", response.data);

      Alert.alert(
        "Félicitations", 
        `Citoyen ${response.data.prenom} enrôlé avec succès !\nNIN : ${response.data.nin}`,
        [{ text: "OK", onPress: () => navigation.navigate("SuccessScreen") }]
      );

    } catch (error) {
      console.log("❌ Erreur Enrôlement :", error.response?.data || error.message);
      
      // Si Django renvoie une erreur (ex: Email déjà pris ou Visage non détecté)
      const serverError = error.response?.data?.error || "Une erreur est survenue.";
      Alert.alert("Erreur", JSON.stringify(serverError));
      
    } finally {
      setLoading(false);
    }
  };

  // --- RENDU UI ---

  if (!permission) return <View style={styles.center}><ActivityIndicator size="large" /></View>;
  
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.textInfo}>L'accès caméra est requis.</Text>
        <Button title="Autoriser" onPress={requestPermission} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!photoUri ? (
        <View style={{ flex: 1 }}>
          <CameraView style={StyleSheet.absoluteFillObject} facing="front" ref={cameraRef} />
          <View style={styles.overlay}>
            <View style={styles.faceGuide} />
            <Text style={styles.guideText}>Cadrez votre visage</Text>
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
              {fingerprintDone ? "✓ EMPREINTE VALIDÉE" : "CAPTURER L'EMPREINTE"}
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
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnConfirmText}>FINALISER</Text>}
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
  textInfo: { color: "#fff", marginBottom: 20 },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, color: COLORS.primary },
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "center", alignItems: "center" },
  faceGuide: { width: 260, height: 320, borderWidth: 3, borderColor: "#fff", borderRadius: 130, borderStyle: "dashed" },
  guideText: { color: "#fff", marginTop: 20, backgroundColor: "rgba(0,0,0,0.6)", padding: 10, borderRadius: 5 },
  snap: { position: "absolute", bottom: 50, width: 75, height: 75, borderRadius: 40, backgroundColor: "#fff", padding: 5 },
  snapInner: { flex: 1, borderRadius: 35, backgroundColor: COLORS.primary },
  reviewContainer: { flex: 1, backgroundColor: "#f8f9fa", padding: 25, alignItems: "center", justifyContent: "center" },
  cropWrapper: { width: 220, height: 220, borderRadius: 110, overflow: "hidden", borderWidth: 4, borderColor: COLORS.primary, marginBottom: 30 },
  preview: { width: "100%", height: "140%", top: -20 },
  fingerprintBtn: { width: "100%", padding: 20, backgroundColor: "#34495e", borderRadius: 15, alignItems: "center", marginBottom: 25 },
  btnSuccess: { backgroundColor: "#27ae60" },
  btnText: { color: "#fff", fontWeight: "bold", fontSize: 16 },
  row: { flexDirection: "row", gap: 15 },
  btnRetry: { flex: 1, padding: 18, borderRadius: 15, borderWidth: 1, borderColor: "#dcdde1", alignItems: "center", backgroundColor: "#fff" },
  btnRetryText: { color: "#7f8c8d", fontWeight: "600" },
  btnConfirm: { flex: 1, padding: 18, borderRadius: 15, backgroundColor: COLORS.primary, alignItems: "center" },
  btnConfirmText: { color: "#fff", fontWeight: "bold" },
  btnDisabled: { backgroundColor: "#bdc3c7" },
});