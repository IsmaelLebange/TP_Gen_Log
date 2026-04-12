import React, { useState } from "react";
import { View, StyleSheet, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../../hooks/useAuth";
import { loginAgent } from "../../api/auth";
import { COLORS, SIZES } from "../../constants/theme";
import Button from "../../components/atoms/Button";
import FormField from "../../components/molecules/FormField";
import Header from "../../components/organisms/Header";
import Footer from "../../components/organisms/Footer";

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();

  const handleLogin = async () => {
    if (!username || !password) return Alert.alert("Attention", "Tous les champs sont requis.");
    setLoading(true);
    try {
      const data = await loginAgent(username, password);
      if (data?.access_token && data?.user) {
        await signIn(data.access_token, data.user);
        // Navigation gérée par le changement d'état dans Navigation.js
      } else {
        Alert.alert("Erreur", "Données de connexion invalides.");
      }
    } catch (err) {
      Alert.alert("Erreur", err.error || err.message || "Accès refusé.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Header title="SEIP - AUTHENTIFICATION" />
      <View style={styles.content}>
        <View style={styles.form}>
          <FormField label="Identifiant Agent" placeholder="Email ou NIN" value={username} onChangeText={setUsername} />
          <FormField label="Mot de passe" placeholder="••••••••" secureTextEntry value={password} onChangeText={setPassword} />
          <Button title="S'AUTHENTIFIER" onPress={handleLogin} loading={loading} />
        </View>
        <Button title="Pré-enrôlement Citoyen" variant="secondary" onPress={() => navigation.navigate("PreEnrollment")} />
      </View>
      <Footer />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { flex: 1, padding: SIZES.padding, justifyContent: "center" },
  form: { marginBottom: 30 },
});