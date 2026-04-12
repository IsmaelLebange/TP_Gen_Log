import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, Alert, RefreshControl, Modal,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import Button from '../../components/atoms/Button';
import { fetchAuditLogs } from '../../api/admin';
import { formatDate } from '../../utils/formatDate';

export default function AuditLogScreen({ navigation }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [filters, setFilters] = useState({ user_id: '', action: '', hours: '', query: '' });
  const [tempFilters, setTempFilters] = useState({
      user_id: "",
      action: "",
      hours: "",
      query: "",
      province: "",
      territoire: "",
      secteur: "",
    });

  const fetchLogs = async (filterParams = {}) => {
    try {
      const data = await fetchAuditLogs(filterParams);
      setLogs(data);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger les logs');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { fetchLogs(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    fetchLogs(filters);
  };

  const applyFilters = () => {
    setFilters(tempFilters);
    fetchLogs(tempFilters);
    setFilterModalVisible(false);
  };

  const resetFilters = () => {
    setTempFilters({ user_id: '', action: '', hours: '', query: '' });
    setFilters({});
    fetchLogs({});
    setFilterModalVisible(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.logItem}>
      <View style={styles.logHeader}>
        <Text style={styles.logAction}>{item.action}</Text>
        <Text style={styles.logDate}>{formatDate(item.created_at)}</Text>
      </View>
      <Text style={styles.logEntity}>📌 {item.entity_type} - ID: {item.entity_id}</Text>
      <Text style={styles.logUser}>👤 Utilisateur: {item.user_email || 'N/A'} (ID: {item.user_id})</Text>
      <Text style={styles.logIp}>🌐 IP: {item.ip_address}</Text>
    </View>
  );

  if (loading) return <LoadingSpinner />;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.background }}>
      <Header title="Journal d'audit" showBack onBack={() => navigation.goBack()} />
      <View style={styles.filterBar}>
        <TouchableOpacity style={styles.filterButton} onPress={() => setFilterModalVisible(true)}>
          <Text style={styles.filterButtonText}>🔍 Filtrer</Text>
        </TouchableOpacity>
        {(filters.user_id || filters.action || filters.hours || filters.query) && (
          <TouchableOpacity style={styles.clearButton} onPress={resetFilters}>
            <Text style={styles.clearButtonText}>✖ Réinitialiser</Text>
          </TouchableOpacity>
        )}
      </View>
      <FlatList
        data={logs}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucun log trouvé</Text>}
      />
      <Footer />

      <Modal visible={filterModalVisible} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Filtrer les logs</Text>
            <TextInput style={styles.input} placeholder="ID utilisateur" value={tempFilters.user_id} onChangeText={(text) => setTempFilters({ ...tempFilters, user_id: text })} keyboardType="numeric" />
            <TextInput style={styles.input} placeholder="Action (ex: LOGIN, CREATE)" value={tempFilters.action} onChangeText={(text) => setTempFilters({ ...tempFilters, action: text })} />
            <TextInput style={styles.input} placeholder="Heures (1-168)" value={tempFilters.hours} onChangeText={(text) => setTempFilters({ ...tempFilters, hours: text })} keyboardType="numeric" />
            <TextInput style={styles.input} placeholder="Recherche textuelle" value={tempFilters.query} onChangeText={(text) => setTempFilters({ ...tempFilters, query: text })} />
            <View style={styles.modalButtons}>
              <Button title="Appliquer" onPress={applyFilters} style={{ flex: 1 }} />
              <Button title="Annuler" variant="secondary" onPress={() => setFilterModalVisible(false)} style={{ flex: 1 }} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  filterBar: { flexDirection: 'row', padding: SIZES.padding, gap: 10 },
  filterButton: { backgroundColor: COLORS.primary, paddingHorizontal: 15, paddingVertical: 8, borderRadius: 20 },
  filterButtonText: { color: '#fff', fontWeight: '600' },
  clearButton: { backgroundColor: '#e74c3c', paddingHorizontal: 15, paddingVertical: 8, borderRadius: 20 },
  clearButtonText: { color: '#fff', fontWeight: '600' },
  list: { padding: SIZES.padding, paddingBottom: 80 },
  logItem: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 15, marginBottom: 12, borderWidth: 1, borderColor: '#eee' },
  logHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  logAction: { fontWeight: 'bold', color: COLORS.primary, fontSize: 16 },
  logDate: { color: '#7f8c8d', fontSize: 12 },
  logEntity: { fontSize: 14, marginBottom: 4 },
  logUser: { fontSize: 14, marginBottom: 4 },
  logIp: { fontSize: 12, color: '#95a5a6' },
  empty: { textAlign: 'center', marginTop: 50, color: '#7f8c8d' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 20, width: '90%' },
  modalTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: COLORS.primary },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16 },
  modalButtons: { flexDirection: 'row', gap: 10, marginTop: 10 },
});