import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, Alert, TextInput, TouchableOpacity, Image, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as ImagePicker from 'expo-image-picker';
import { useAuth } from '../../hooks/useAuth';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import Button from '../../components/atoms/Button';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import { fetchUserProfile, updateUserProfile, addBiometricPhoto } from '../../api/profile';
import { MEDIA_BASE_URL } from '../../constants/config';

export default function ProfileScreen({ navigation }) {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [tempValue, setTempValue] = useState('');

  const loadProfile = async () => {
    try {
      const data = await fetchUserProfile();
      setProfile(data);
      if (data.photo_url) {
        console.log('URL photo reçue (relative) :', data.photo_url);
        console.log('URL complète :', `${MEDIA_BASE_URL}${data.photo_url}`);
      } else {
        console.log('Aucune photo_url dans le profil');
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger le profil');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { loadProfile(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    loadProfile();
  };

  const authenticate = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    if (!hasHardware) {
      Alert.alert('Biométrie indisponible', 'Contactez un agent.');
      return false;
    }
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();
    if (!isEnrolled) {
      Alert.alert('Aucune donnée biométrique', 'Contactez un agent.');
      return false;
    }
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Confirmez votre identité',
      fallbackLabel: 'Code PIN',
    });
    if (!result.success) {
      Alert.alert('Authentification échouée', 'Opération annulée.');
      return false;
    }
    return true;
  };

  // Règles d'édition
  const isFieldEditable = (fieldKey, currentValue) => {
    if (fieldKey === 'telephone' || fieldKey === 'adresse') return true;
    if (fieldKey === 'nom_pere' || fieldKey === 'nom_mere') {
      return !currentValue || currentValue.trim() === '';
    }
    if (fieldKey === 'sexe' || fieldKey === 'lieu_naissance') {
      return !currentValue || currentValue.trim() === '';
    }
    return false;
  };

  const handleUpdateField = async (field, value) => {
    const currentValue = getCurrentValue(field);
    if (!isFieldEditable(field, currentValue)) {
      Alert.alert('Opération non autorisée', 'Ce champ ne peut pas être modifié.');
      return;
    }
    const ok = await authenticate();
    if (!ok) return;

    setLoading(true);
    try {
      await updateUserProfile({ [field]: value });
      await loadProfile();
      Alert.alert('Succès', `${getFieldLabel(field)} mis à jour.`);
      setEditingField(null);
      setTempValue('');
    } catch (error) {
      Alert.alert('Erreur', error.message || 'Échec de la mise à jour');
    } finally {
      setLoading(false);
    }
  };

  const handleAddPhoto = async () => {
    if (profile?.photo_url) {
      Alert.alert('Photo déjà existante', 'Vous ne pouvez pas remplacer la photo. Contactez un agent.');
      return;
    }
    const ok = await authenticate();
    if (!ok) return;

    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission refusée', 'Activez la caméra.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      base64: true,
      quality: 0.7,
    });
    if (!result.canceled && result.assets[0].base64) {
      setLoading(true);
      try {
        const mimeType = result.assets[0].mimeType || 'image/jpeg';
        const base64WithPrefix = `data:${mimeType};base64,${result.assets[0].base64}`;
        await addBiometricPhoto(base64WithPrefix);
        await loadProfile();
        Alert.alert('Succès', 'Photo ajoutée.');
      } catch (error) {
        console.log("Erreur ajout photo", error);
        Alert.alert('Erreur', 'Impossible d’ajouter la photo');
      } finally {
        setLoading(false);
      }
    }
  };

  const getFieldLabel = (field) => {
    const labels = {
      telephone: 'Téléphone',
      adresse: 'Adresse',
      nom_pere: 'Nom du père',
      nom_mere: 'Nom de la mère',
      sexe: 'Sexe',
      lieu_naissance: 'Lieu de naissance'
    };
    return labels[field] || field;
  };

  const getCurrentValue = (field) => {
    if (!profile) return '';
    switch (field) {
      case 'telephone': return profile.telephone || '';
      case 'adresse': return profile.adresse?.full || '';
      case 'nom_pere': return profile.nom_pere || '';
      case 'nom_mere': return profile.nom_mere || '';
      case 'sexe': return profile.sexe || '';
      case 'lieu_naissance': return profile.lieu_naissance || '';
      default: return '';
    }
  };

  const renderField = (label, value, fieldKey, icon) => {
    const isEmpty = !value || value.trim() === '';
    const editable = isFieldEditable(fieldKey, value);
    // Afficher le crayon si modifiable ET (soit vide, soit c'est telephone/adresse)
    const showEditButton = editable && (isEmpty || fieldKey === 'telephone' || fieldKey === 'adresse');

    return (
      <View style={styles.fieldContainer}>
        <View style={styles.fieldHeader}>
          <Text style={styles.fieldIcon}>{icon}</Text>
          <Text style={styles.fieldLabel}>{label}</Text>
        </View>
        {editingField === fieldKey ? (
          <View>
            <TextInput style={styles.input} value={tempValue} onChangeText={setTempValue} placeholder={`Nouveau ${label.toLowerCase()}`} />
            <View style={styles.editButtons}>
              <TouchableOpacity style={[styles.editButton, styles.cancelButton]} onPress={() => setEditingField(null)}>
                <Text style={styles.cancelButtonText}>Annuler</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.editButton, styles.saveButton]} onPress={() => handleUpdateField(fieldKey, tempValue)}>
                <Text style={styles.saveButtonText}>Confirmer</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <View style={styles.fieldValueRow}>
            <Text style={[styles.fieldValue, isEmpty && styles.fieldValueEmpty]}>
              {isEmpty ? 'Non renseigné' : value}
            </Text>
            {showEditButton && (
              <TouchableOpacity onPress={() => { setEditingField(fieldKey); setTempValue(getCurrentValue(fieldKey)); }}>
                <Text style={styles.editIcon}>✏️</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>
    );
  };

  if (loading) return <LoadingSpinner />;
  if (!profile) return <LoadingSpinner />;

  return (
    <View style={styles.container}>
      <Header title="Mon profil" showBack onBack={() => navigation.goBack()} />
      <ScrollView contentContainerStyle={styles.scrollContent} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        {/* Photo */}
        <View style={styles.photoSection}>
          {profile.photo_url ? (
            <Image source={{ uri: `${MEDIA_BASE_URL}${profile.photo_url}` }} style={styles.photo} />
          ) : (
            <TouchableOpacity onPress={handleAddPhoto} style={styles.photoPlaceholder}>
              <Text style={styles.photoIcon}>📷 Ajouter photo</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Identité */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Identité</Text>
          <View style={styles.card}>
            <View style={styles.row}><Text style={styles.label}>Nom :</Text><Text style={styles.value}>{profile.nom || ''}</Text></View>
            <View style={styles.row}><Text style={styles.label}>Postnom :</Text><Text style={styles.value}>{profile.postnom || '—'}</Text></View>
            <View style={styles.row}><Text style={styles.label}>Prénom :</Text><Text style={styles.value}>{profile.prenom || '—'}</Text></View>
            {renderField('Sexe', profile.sexe, 'sexe', '⚥')}
            <View style={styles.row}><Text style={styles.label}>Date naissance :</Text><Text style={styles.value}>{profile.date_naissance ? new Date(profile.date_naissance).toLocaleDateString('fr-FR') : '—'}</Text></View>
            {renderField('Lieu de naissance', profile.lieu_naissance, 'lieu_naissance', '📍')}
            <View style={styles.row}><Text style={styles.label}>Origine :</Text><Text style={styles.value}>{profile.origine?.full || '—'}</Text></View>
          </View>
        </View>

        {/* Contact */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact</Text>
          <View style={styles.card}>
            {renderField('Téléphone', profile.telephone, 'telephone', '📞')}
            {renderField('Adresse', profile.adresse?.full, 'adresse', '🏠')}
            <View style={styles.row}><Text style={styles.label}>Email :</Text><Text style={styles.value}>{profile.email}</Text></View>
          </View>
        </View>

        {/* Parents */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Parents</Text>
          <View style={styles.card}>
            {renderField('Nom du père', profile.nom_pere, 'nom_pere', '👨')}
            {renderField('Nom de la mère', profile.nom_mere, 'nom_mere', '👩')}
          </View>
        </View>

        {/* Infos admin */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informations administratives</Text>
          <View style={styles.card}>
            <View style={styles.row}><Text style={styles.label}>NIN :</Text><Text style={styles.value}>{profile.nin}</Text></View>
            <View style={styles.row}><Text style={styles.label}>Statut validation :</Text><Text style={[styles.value, profile.is_validated ? styles.valid : styles.pending]}>{profile.is_validated ? '✅ Validé' : '⏳ En attente'}</Text></View>
          </View>
        </View>
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollContent: { padding: SIZES.padding, paddingBottom: 80 },
  photoSection: { alignItems: 'center', marginBottom: 20 },
  photo: { width: 100, height: 100, borderRadius: 50, borderWidth: 2, borderColor: COLORS.primary },
  photoPlaceholder: { width: 100, height: 100, borderRadius: 50, backgroundColor: '#ecf0f1', justifyContent: 'center', alignItems: 'center' },
  photoIcon: { fontSize: 16, color: '#95a5a6', textAlign: 'center' },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: COLORS.primary, marginBottom: 10, borderLeftWidth: 4, borderLeftColor: COLORS.primary, paddingLeft: 10 },
  card: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 15, borderWidth: 1, borderColor: '#eee' },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  label: { fontSize: 14, color: '#7f8c8d', fontWeight: '500' },
  value: { fontSize: 14, fontWeight: '500', color: '#2c3e50', flex: 1, textAlign: 'right' },
  valid: { color: '#27ae60' },
  pending: { color: '#e67e22' },
  fieldContainer: { marginBottom: 15, borderBottomWidth: 1, borderBottomColor: '#ecf0f1', paddingBottom: 10 },
  fieldHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  fieldIcon: { fontSize: 16, marginRight: 8 },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: '#2c3e50' },
  fieldValueRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  fieldValue: { fontSize: 14, color: '#2c3e50', flex: 1 },
  fieldValueEmpty: { color: '#e74c3c', fontStyle: 'italic' },
  editIcon: { fontSize: 16, paddingHorizontal: 8 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, fontSize: 14, marginTop: 8, marginBottom: 10 },
  editButtons: { flexDirection: 'row', justifyContent: 'flex-end', gap: 10, marginTop: 5 },
  editButton: { paddingVertical: 6, paddingHorizontal: 15, borderRadius: 6 },
  saveButton: { backgroundColor: COLORS.primary },
  saveButtonText: { color: '#fff', fontWeight: '600', fontSize: 12 },
  cancelButton: { backgroundColor: '#ecf0f1' },
  cancelButtonText: { color: '#7f8c8d', fontWeight: '600', fontSize: 12 },
});