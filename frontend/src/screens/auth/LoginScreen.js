import React, { useState, useContext } from "react";
import { View, StyleSheet, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { AuthContext } from "../../store/AuthContext";
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
  const authContext = useContext(AuthContext);
  const signIn = authContext ? authContext.signIn : null;

  const handleLogin = async () => {
    if (!username || !password) {
      return Alert.alert("Attention", "Veuillez remplir tous les champs.");
    }
    setLoading(true);
    try {
      const data = await loginAgent(username, password);
      // On vérifie 'access_token' car c'est ce que renvoie ton service maintenant
      if (data && data.access_token && signIn) {
        // On passe tout l'objet data ou juste le token selon ton AuthContext
        await signIn(data.access_token, data.user);
        // Pas besoin de navigation.navigate('Home') si ton index.js switch de stack tout seul
      } else {
        Alert.alert("Erreur", "Données de connexion invalides.");
      }
    } catch (err) {
      Alert.alert("Erreur", err.message || "Accès refusé.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Header title="SEIP - AUTHENTIFICATION" />
      <View style={styles.content}>
        <View style={styles.form}>
          <FormField
            label="Identifiant Agent"
            placeholder="Entrez votre ID"
            value={username}
            onChangeText={setUsername}
          />
          <FormField
            label="Mot de passe"
            placeholder="••••••••"
            secureTextEntry={true}
            value={password}
            onChangeText={setPassword}
          />
          <Button
            title="S'AUTHENTIFIER"
            onPress={handleLogin}
            loading={loading}
          />
        </View>
        <Button
          title="Pré-enrôlement Citoyen"
          variant="secondary"
          onPress={() => navigation.navigate("PreEnrollment")}
        />
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
