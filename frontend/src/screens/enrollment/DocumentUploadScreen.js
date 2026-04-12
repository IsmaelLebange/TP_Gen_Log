import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import * as DocumentPicker from 'expo-document-picker';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import Button from '../../components/atoms/Button';
import DocumentCard from '../../components/molecules/DocumentCard';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import { fetchUserDocuments, uploadDocument, deleteDocument } from '../../api/documents';
import { formatDate } from '../../utils/formatDate';

export default function DocumentUploadScreen({ navigation }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedType, setSelectedType] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentNumber, setDocumentNumber] = useState('');
  const [issueDate, setIssueDate] = useState('');
  const [expiryDate, setExpiryDate] = useState('');

  const documentTypes = [
    { label: 'Carte d\'identité (CNI)', value: 'CNI' },
    { label: 'Passeport', value: 'PAS' },
    { label: 'Permis de conduire', value: 'PER' },
    { label: 'Acte de naissance', value: 'ACT' },
    { label: 'Justificatif de domicile', value: 'DOM' },
  ];

  const loadDocuments = async () => {
    try {
      const data = await fetchUserDocuments();
      setDocuments(data);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger vos documents');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { loadDocuments(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    loadDocuments();
  };

  const pickDocument = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: ['application/pdf', 'image/jpeg', 'image/png'],
      copyToCacheDirectory: true,
    });
    if (result.canceled === false && result.assets && result.assets[0]) {
      const file = result.assets[0];
      setSelectedFile({
        uri: file.uri,
        name: file.name,
        type: file.mimeType,
      });
      setModalVisible(true);
    }
  };

  const handleUpload = async () => {
    if (!selectedType) {
      Alert.alert('Erreur', 'Veuillez sélectionner un type de document');
      return;
    }
    if (!selectedFile) {
      Alert.alert('Erreur', 'Veuillez sélectionner un fichier');
      return;
    }
    if (!documentNumber) {
      Alert.alert('Erreur', 'Numéro de document requis');
      return;
    }
    if (!issueDate) {
      Alert.alert('Erreur', 'Date d\'émission requise');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('type', selectedType);
    formData.append('numero', documentNumber);
    formData.append('date_emission', issueDate);
    if (expiryDate) formData.append('date_expiration', expiryDate);
    formData.append('fichier', {
      uri: selectedFile.uri,
      name: selectedFile.name,
      type: selectedFile.type,
    });

    try {
      await uploadDocument(formData);
      Alert.alert('Succès', 'Document envoyé. En attente de validation.');
      setModalVisible(false);
      resetForm();
      loadDocuments();
    } catch (error) {
      Alert.alert('Erreur', error.message || 'Échec de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setSelectedType('');
    setSelectedFile(null);
    setDocumentNumber('');
    setIssueDate('');
    setExpiryDate('');
  };

  const handleDelete = (docId) => {
    Alert.alert(
      'Confirmation',
      'Supprimer ce document ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          onPress: async () => {
            try {
              await deleteDocument(docId);
              Alert.alert('Succès', 'Document supprimé');
              loadDocuments();
            } catch (error) {
              Alert.alert('Erreur', error.message || 'Échec de la suppression');
            }
          },
        },
      ]
    );
  };

  const getStatusText = (statut) => {
    switch (statut) {
      case 'EN_ATTENTE': return '⏳ En attente';
      case 'VALIDE': return '✅ Validé';
      case 'REJETE': return '❌ Rejeté';
      default: return statut;
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <View style={styles.container}>
      <Header title="Mes justificatifs" showBack onBack={() => navigation.goBack()} />
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.buttonContainer}>
          <Button title="Ajouter un justificatif" onPress={pickDocument} />
        </View>

        <Text style={styles.infoText}>
          Les documents fournis seront vérifiés par un agent. Une fois validés, vous pourrez obtenir votre carte d'identité nationale.
        </Text>

        {documents.length === 0 ? (
          <Text style={styles.emptyText}>Aucun document uploadé</Text>
        ) : (
          documents.map((doc) => (
            <DocumentCard
              key={doc.id}
              title={`${doc.type} - ${doc.numero}`}
              status={getStatusText(doc.statut)}
              onPress={() => handleDelete(doc.id)}
            />
          ))
        )}
      </ScrollView>
      <Footer />

      {/* Modal d'upload */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Ajouter un justificatif</Text>

            <Text style={styles.label}>Type de document</Text>
            <View style={styles.pickerBox}>
              {documentTypes.map((type) => (
                <TouchableOpacity
                  key={type.value}
                  style={[
                    styles.typeOption,
                    selectedType === type.value && styles.typeOptionSelected,
                  ]}
                  onPress={() => setSelectedType(type.value)}
                >
                  <Text style={selectedType === type.value ? styles.typeTextSelected : styles.typeText}>
                    {type.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.label}>Numéro du document</Text>
            <TextInput
              style={styles.input}
              placeholder="Ex: 123456789"
              value={documentNumber}
              onChangeText={setDocumentNumber}
            />

            <Text style={styles.label}>Date d'émission (YYYY-MM-DD)</Text>
            <TextInput
              style={styles.input}
              placeholder="2024-01-01"
              value={issueDate}
              onChangeText={setIssueDate}
            />

            <Text style={styles.label}>Date d'expiration (optionnel)</Text>
            <TextInput
              style={styles.input}
              placeholder="YYYY-MM-DD"
              value={expiryDate}
              onChangeText={setExpiryDate}
            />

            <Text style={styles.label}>Fichier sélectionné</Text>
            <Text style={styles.fileName}>{selectedFile?.name || 'Aucun fichier'}</Text>

            <View style={styles.modalButtons}>
              <Button title="Annuler" variant="secondary" onPress={() => setModalVisible(false)} style={{ flex: 1 }} />
              <Button title={uploading ? "Upload..." : "Envoyer"} onPress={handleUpload} loading={uploading} style={{ flex: 1 }} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollContent: { padding: SIZES.padding, paddingBottom: 80 },
  buttonContainer: { marginBottom: 20 },
  infoText: { fontSize: 14, color: '#7f8c8d', marginBottom: 20, textAlign: 'center' },
  emptyText: { textAlign: 'center', marginTop: 50, color: '#7f8c8d', fontSize: 16 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 20, width: '90%', maxHeight: '80%' },
  modalTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.primary, marginBottom: 20, textAlign: 'center' },
  label: { fontSize: 14, fontWeight: '600', color: '#2c3e50', marginBottom: 5, marginTop: 10 },
  pickerBox: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 10 },
  typeOption: { paddingVertical: 8, paddingHorizontal: 12, borderRadius: 20, backgroundColor: '#ecf0f1', marginRight: 8, marginBottom: 8 },
  typeOptionSelected: { backgroundColor: COLORS.primary },
  typeText: { color: '#2c3e50' },
  typeTextSelected: { color: '#fff' },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, fontSize: 16, marginBottom: 10 },
  fileName: { fontSize: 14, color: '#7f8c8d', marginBottom: 15, fontStyle: 'italic' },
  modalButtons: { flexDirection: 'row', gap: 10, marginTop: 10 },
});