import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import { fetchDashboardStats } from '../../api/admin';

export default function StatisticsScreen({ navigation }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const data = await fetchDashboardStats();
      setStats(data);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger les statistiques');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { fetchStats(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    fetchStats();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.background }}>
      <Header title="Statistiques" showBack onBack={() => navigation.goBack()} />
      <ScrollView contentContainerStyle={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Vue d'ensemble</Text>
          <View style={styles.statCard}><Text style={styles.statLabel}>Total citoyens enrôlés</Text><Text style={styles.statValue}>{stats?.total_citoyens || 0}</Text></View>
          <View style={styles.statCard}><Text style={styles.statLabel}>Documents en attente</Text><Text style={styles.statValue}>{stats?.pending_documents || 0}</Text></View>
          <View style={styles.statCard}><Text style={styles.statLabel}>Validations aujourd'hui</Text><Text style={styles.statValue}>{stats?.today_validations || 0}</Text></View>
        </View>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👥 Utilisateurs</Text>
          <View style={styles.statCard}><Text style={styles.statLabel}>Agents actifs</Text><Text style={styles.statValue}>{stats?.active_agents || 0}</Text></View>
          <View style={styles.statCard}><Text style={styles.statLabel}>Administrateurs</Text><Text style={styles.statValue}>{stats?.admin_count || 0}</Text></View>
        </View>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📈 Répartition par province</Text>
          {stats?.province_stats?.map((prov, idx) => (
            <View key={idx} style={styles.provinceRow}>
              <Text style={styles.provinceName}>{prov.nom}</Text>
              <View style={styles.progressBar}><View style={[styles.progressFill, { width: `${prov.percentage || 0}%` }]} /></View>
              <Text style={styles.provinceCount}>{prov.count}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: SIZES.padding, paddingBottom: 80 },
  section: { marginBottom: 25 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: COLORS.primary, marginBottom: 15, borderBottomWidth: 1, borderBottomColor: '#eee', paddingBottom: 5 },
  statCard: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 15, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderWidth: 1, borderColor: '#eee' },
  statLabel: { fontSize: 14, color: '#7f8c8d' },
  statValue: { fontSize: 24, fontWeight: 'bold', color: '#2c3e50' },
  provinceRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  provinceName: { width: 100, fontSize: 14, fontWeight: '500' },
  progressBar: { flex: 1, height: 8, backgroundColor: '#ecf0f1', borderRadius: 4, marginHorizontal: 10, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: COLORS.primary, borderRadius: 4 },
  provinceCount: { width: 40, textAlign: 'right', fontSize: 14, fontWeight: 'bold' },
});