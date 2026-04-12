import React, { useState, useEffect } from "react";
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  Text,
  TouchableOpacity,
  Platform,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import DateTimePicker from "@react-native-community/datetimepicker"; // Installation: npx expo install @react-native-community/datetimepicker

import { COLORS, SIZES } from "../../constants/theme";
import { loadDivisions } from "../../services/divisionService";

import Button from "../../components/atoms/Button";
import FormField from "../../components/molecules/FormField";
import Label from "../../components/atoms/Label";
import LoadingSpinner from "../../components/atoms/LoadingSpinner";
import Header from "../../components/organisms/Header";
import Footer from "../../components/organisms/Footer";

export default function EnrollmentFormScreen({ navigation }) {
  const [db, setDb] = useState({});
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState(1);

  // États pour le DatePicker
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [dateObj, setDateObj] = useState(new Date(2000, 0, 1)); // Par défaut an 2000

  const [form, setForm] = useState({
    email: "",
    mot_de_passe: "",
    password_confirm: "",
    nom: "",
    postnom: "",
    prenom: "",
    sexe: "", // Par défaut, on force à choisir un sexe
    date_naissance: "", // Sera stocké en YYYY-MM-DD
    lieu_naissance: "",
    province_origine: "",
    territoire_origine: "",
    secteur_origine: "",
    nom_du_pere: "",
    nom_de_la_mere: "",
    adresse_province: "",
    adresse_commune: "",
    adresse_quartier: "",
    adresse_avenue: "",
    adresse_numero: "",
    telephone: "",
  });

  useEffect(() => {
    loadDivisions().then((data) => {
      setDb(data);
      setLoading(false);
    });
  }, []);

  // Gestion du changement de date
  const onDateChange = (event, selectedDate) => {
    const currentDate = selectedDate || dateObj;
    setShowDatePicker(Platform.OS === "ios");
    setDateObj(currentDate);

    // Formatage pour l'état du formulaire (YYYY-MM-DD)
    const year = currentDate.getFullYear();
    const month = (currentDate.getMonth() + 1).toString().padStart(2, "0");
    const day = currentDate.getDate().toString().padStart(2, "0");
    setForm({ ...form, date_naissance: `${year}-${month}-${day}` });
  };

  const handleNext = () => {
    if (step === 1) {
      if (!form.nom || !form.prenom || !form.date_naissance || !form.lieu_naissance)
        return Alert.alert(
          "Erreur",
          "Remplis les informations d'identité (Nom, Prénom et Date de naissance)",
        );
      if (!form.sexe) return Alert.alert("Erreur", "Le sexe est obligatoire");
    }
    if (step === 2) {
      if (
        !form.province_origine ||
        !form.territoire_origine ||
        !form.secteur_origine
      )
        return Alert.alert("Erreur", "L'origine complète est obligatoire");
    }
    setStep(step + 1);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.background }}>
      <Header
        title={`Enrôlement - Étape ${step}/3`}
        showBack
        onBack={() => (step > 1 ? setStep(step - 1) : navigation.goBack())}
      />

      <ScrollView
        style={styles.container}
        contentContainerStyle={{ paddingBottom: 50 }}
      >
        {/* ÉTAPE 1 : IDENTITÉ & SEXE */}
        {step === 1 && (
          <View>
            <FormField
              label="Nom"
              placeholder="Nom"
              value={form.nom}
              onChangeText={(v) => setForm({ ...form, nom: v })}
            />
            <FormField
              label="Postnom"
              placeholder="Postnom"
              value={form.postnom}
              onChangeText={(v) => setForm({ ...form, postnom: v })}
            />
            <FormField
              label="Prénom"
              placeholder="Prénom"
              value={form.prenom}
              onChangeText={(v) => setForm({ ...form, prenom: v })}
            />

            <Label>Sexe</Label>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={form.sexe}
                onValueChange={(v) => setForm({ ...form, sexe: v })}
              >
                <Picker.Item label="Sélectionnez le sexe" value="" />
                <Picker.Item label="Masculin" value="Masculin" />
                <Picker.Item label="Féminin" value="Féminin" />
              </Picker>
            </View>
            <FormField
              label="Lieu de naissance"
              placeholder="Ex: Kinshasa"
              value={form.lieu_naissance}
              onChangeText={(v) => setForm({ ...form, lieu_naissance: v })}
            />

            {/* REMPLACEMENT DU TEXTFIELD PAR LE DATEPICKER */}
            <Label>Date de naissance</Label>
            <TouchableOpacity
              style={styles.dateSelector}
              onPress={() => setShowDatePicker(true)}
            >
              <Text
                style={
                  form.date_naissance ? styles.dateText : styles.datePlaceholder
                }
              >
                {form.date_naissance
                  ? form.date_naissance
                  : "Sélectionner la date"}
              </Text>
            </TouchableOpacity>

            {showDatePicker && (
              <DateTimePicker
                value={dateObj}
                mode="date"
                display={Platform.OS === "ios" ? "spinner" : "default"}
                maximumDate={new Date()}
                onChange={onDateChange}
              />
            )}

            <Button
              title="SUIVANT"
              onPress={handleNext}
              style={styles.btnMargin}
            />
          </View>
        )}

        {/* ÉTAPE 2 : ORIGINE */}
        {step === 2 && (
          <View>
            <FormField
              label="Nom du Père"
              value={form.nom_du_pere}
              onChangeText={(v) => setForm({ ...form, nom_du_pere: v })}
            />
            <FormField
              label="Nom de la Mère"
              value={form.nom_de_la_mere}
              onChangeText={(v) => setForm({ ...form, nom_de_la_mere: v })}
            />

            <Label>Province d'origine</Label>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={form.province_origine}
                onValueChange={(v) =>
                  setForm({
                    ...form,
                    province_origine: v,
                    territoire_origine: "",
                    secteur_origine: "",
                  })
                }
              >
                <Picker.Item label="Choisir Province" value="" />
                {Object.keys(db || {}).map((p) => (
                  <Picker.Item key={p} label={p} value={p} />
                ))}
              </Picker>
            </View>

            <Label>Territoire d'origine</Label>
            <View style={styles.pickerBox}>
              <Picker
                enabled={!!form.province_origine}
                selectedValue={form.territoire_origine}
                onValueChange={(v) =>
                  setForm({
                    ...form,
                    territoire_origine: v,
                    secteur_origine: "",
                  })
                }
              >
                <Picker.Item label="Choisir Territoire" value="" />
                {form.province_origine &&
                  db[form.province_origine] &&
                  Object.keys(db[form.province_origine]).map((t) => (
                    <Picker.Item key={t} label={t} value={t} />
                  ))}
              </Picker>
            </View>

            <Label>Secteur / Chefferie</Label>
            <View style={styles.pickerBox}>
              <Picker
                enabled={!!form.territoire_origine}
                selectedValue={form.secteur_origine}
                onValueChange={(v) => setForm({ ...form, secteur_origine: v })}
              >
                <Picker.Item label="Choisir Secteur" value="" />
                {form.territoire_origine &&
                  db[form.province_origine]?.[form.territoire_origine]?.map(
                    (s) => <Picker.Item key={s} label={s} value={s} />,
                  )}
              </Picker>
            </View>

            <View style={styles.row}>
              <Button
                title="RETOUR"
                variant="secondary"
                onPress={() => setStep(1)}
                style={{ flex: 1 }}
              />
              <Button
                title="SUIVANT"
                onPress={handleNext}
                style={{ flex: 1 }}
              />
            </View>
          </View>
        )}

        {/* ÉTAPE 3 : ADRESSE & SÉCURITÉ */}
        {step === 3 && (
          <View>
            <Text style={styles.sectionTitle}>Adresse Résidentielle</Text>
            <FormField
              label="Province"
              placeholder="Ex: Kinshasa"
              value={form.adresse_province}
              onChangeText={(v) => setForm({ ...form, adresse_province: v })}
            />
            <FormField
              label="Commune"
              placeholder="Ex: Gombe"
              value={form.adresse_commune}
              onChangeText={(v) => setForm({ ...form, adresse_commune: v })}
            />
            <FormField
              label="Quartier"
              placeholder="Ex: Golf"
              value={form.adresse_quartier}
              onChangeText={(v) => setForm({ ...form, adresse_quartier: v })}
            />
            <View style={styles.row}>
              <View style={{ flex: 2 }}>
                <FormField
                  label="Avenue"
                  value={form.adresse_avenue}
                  onChangeText={(v) => setForm({ ...form, adresse_avenue: v })}
                />
              </View>
              <View style={{ flex: 1 }}>
                <FormField
                  label="N°"
                  value={form.adresse_numero}
                  onChangeText={(v) => setForm({ ...form, adresse_numero: v })}
                />
              </View>
            </View>

            <Text style={styles.sectionTitle}>Sécurité</Text>
            <FormField
              label="Email"
              keyboardType="email-address"
              value={form.email}
              onChangeText={(v) => setForm({ ...form, email: v })}
            />
            <FormField
              label="Téléphone"
              keyboardType="phone-pad"
              value={form.telephone}
              onChangeText={(v) => setForm({ ...form, telephone: v })}
            />
            <FormField
              label="Mot de passe"
              secureTextEntry
              value={form.mot_de_passe}
              onChangeText={(v) => setForm({ ...form, mot_de_passe: v })}
            />
            <FormField
              label="Confirmer"
              secureTextEntry
              value={form.password_confirm}
              onChangeText={(v) => setForm({ ...form, password_confirm: v })}
            />

            <View style={styles.row}>
              <Button
                title="RETOUR"
                variant="secondary"
                onPress={() => setStep(2)}
                style={{ flex: 1 }}
              />
              <Button
                title="BIOMÉTRIE"
                onPress={() => {
                  if (form.mot_de_passe !== form.password_confirm)
                    return Alert.alert("Erreur", "Mots de passe différents");
                  navigation.navigate("BiometricScreen", {
                    enrollmentData: form,
                  });
                }}
                style={{ flex: 1 }}
              />
            </View>
          </View>
        )}
        <Footer />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: SIZES.padding },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: COLORS.primary,
    marginVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  pickerBox: {
    backgroundColor: "#fff",
    borderRadius: SIZES.radius,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "#ddd",
    justifyContent: "center",
    minHeight: 55,
  },
  dateSelector: {
    backgroundColor: "#fff",
    borderRadius: SIZES.radius,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "#ddd",
    height: 55,
    justifyContent: "center",
    paddingHorizontal: 15,
  },
  dateText: { color: "#2c3e50", fontSize: 16 },
  datePlaceholder: { color: "#bdc3c7", fontSize: 16 },
  row: { flexDirection: "row", gap: 10, marginTop: 10 },
  btnMargin: { marginTop: 20 },
});
