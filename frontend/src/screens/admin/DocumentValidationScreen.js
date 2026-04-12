import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, RefreshControl, Modal, TextInput,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import Button from '../../components/atoms/Button';
import { fetchPendingDocuments, validateDocument, rejectDocument } from '../../api/admin';
import { formatDate } from '../../utils/formatDate';

export default function DocumentValidationScreen({ navigation }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [rejectModalVisible, setRejectModalVisible] = useState(false);
  const [rejectComment, setRejectComment] = useState('');

  const fetchPendingDocs = async () => {
    try {
      const data = await fetchPendingDocuments();
      setDocuments(data);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger les documents');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { fetchPendingDocs(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    fetchPendingDocs();
  };

  const handleValidate = async (docId) => {
    Alert.alert('Confirmation', 'Valider ce document ?', [
      { text: 'Annuler', style: 'cancel' },
      {
        text: 'Valider',
        onPress: async () => {
          try {
            await validateDocument(docId);
            Alert.alert('Succès', 'Document validé');
            fetchPendingDocs();
          } catch (error) {
            Alert.alert('Erreur', error.error || 'Échec de la validation');
          }
        },
      },
    ]);
  };

  const handleReject = async () => {
    if (!rejectComment.trim()) {
      Alert.alert('Erreur', 'Veuillez entrer un commentaire de rejet');
      return;
    }
    try {
      await rejectDocument(selectedDoc.id, rejectComment);
      Alert.alert('Succès', 'Document rejeté');
      setRejectModalVisible(false);
      setRejectComment('');
      fetchPendingDocs();
    } catch (error) {
      Alert.alert('Erreur', error.error || 'Échec du rejet');
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.docType}>{item.type}</Text>
        <Text style={styles.docNumber}>{item.numero}</Text>
      </View>
      <Text style={styles.userInfo}>👤 Utilisateur ID: {item.user_id}</Text>
      <Text style={styles.dateInfo}>📅 Émis le: {formatDate(item.date_emission)}</Text>
      {item.date_expiration && <Text style={styles.dateInfo}>⏳ Expire le: {formatDate(item.date_expiration)}</Text>}
      <View style={styles.buttons}>
        <TouchableOpacity style={[styles.btn, styles.btnValidate]} onPress={() => handleValidate(item.id)}>
          <Text style={styles.btnText}>✓ Valider</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnReject]} onPress={() => { setSelectedDoc(item); setRejectModalVisible(true); }}>
          <Text style={styles.btnText}>✗ Rejeter</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (loading) return <LoadingSpinner />;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.background }}>
      <Header title="Validation des documents" showBack onBack={() => navigation.goBack()} />
      <FlatList
        data={documents}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucun document en attente</Text>}
      />
      <Footer />

      <Modal visible={rejectModalVisible} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Motif du rejet</Text>
            <TextInput style={styles.textArea} placeholder="Expliquez pourquoi ce document est rejeté..." value={rejectComment} onChangeText={setRejectComment} multiline numberOfLines={4} />
            <View style={styles.modalButtons}>
              <Button title="Confirmer rejet" onPress={handleReject} style={{ flex: 1 }} />
              <Button title="Annuler" variant="secondary" onPress={() => setRejectModalVisible(false)} style={{ flex: 1 }} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  list: { padding: SIZES.padding, paddingBottom: 80 },
  card: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 15, marginBottom: 12, borderWidth: 1, borderColor: '#eee' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  docType: { fontWeight: 'bold', fontSize: 16, color: COLORS.primary },
  docNumber: { color: '#7f8c8d' },
  userInfo: { fontSize: 14, marginBottom: 4 },
  dateInfo: { fontSize: 12, color: '#95a5a6', marginBottom: 2 },
  buttons: { flexDirection: 'row', justifyContent: 'flex-end', gap: 10, marginTop: 12 },
  btn: { paddingHorizontal: 20, paddingVertical: 8, borderRadius: 8 },
  btnValidate: { backgroundColor: '#27ae60' },
  btnReject: { backgroundColor: '#e74c3c' },
  btnText: { color: '#fff', fontWeight: 'bold' },
  empty: { textAlign: 'center', marginTop: 50, color: '#7f8c8d' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 20, width: '90%' },
  modalTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: COLORS.primary },
  textArea: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16, minHeight: 100, textAlignVertical: 'top' },
  modalButtons: { flexDirection: 'row', gap: 10, marginTop: 10 },
});