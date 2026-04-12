import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../../hooks/useAuth';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import Button from '../../components/atoms/Button';
import LoadingSpinner from '../../components/atoms/LoadingSpinner';
import { fetchUserDocuments } from '../../api/documents';

export default function DashboardScreen({ navigation }) {
  const { user, signOut } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Voulez-vous vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Déconnecter', onPress: async () => { await signOut(); } }
      ]
    );
  };

  const loadData = async () => {
    try {
      const docs = await fetchUserDocuments();
      setDocuments(docs);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger vos documents');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { loadData(); }, []));

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) return <LoadingSpinner />;

  const pendingDocs = documents.filter(d => d.statut === 'EN_ATTENTE').length;
  const validatedDocs = documents.filter(d => d.statut === 'VALIDE').length;

  return (
    <View style={styles.container}>
      <Header title="Tableau de bord citoyen" showBack onBack={() => navigation.goBack()} />
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.card}>
          <Text style={styles.label}>Nom complet</Text>
          <Text style={styles.value}>{user?.prenom} {user?.nom}</Text>

          <Text style={styles.label}>NIN</Text>
          <Text style={styles.value}>{user?.nin}</Text>

          <Text style={styles.label}>Statut validation</Text>
          <Text style={[styles.value, user?.is_validated ? styles.valid : styles.pending]}>
            {user?.is_validated ? '✅ Compte validé' : '⏳ En attente de validation'}
          </Text>

          <Text style={styles.label}>Documents</Text>
          <Text style={styles.value}>En attente : {pendingDocs} | Validés : {validatedDocs}</Text>
        </View>

        <View style={styles.actions}>
          <Button title="Mes documents" onPress={() => navigation.navigate('DocumentUpload')} />
          <Button title="Ma carte d'identité" onPress={() => navigation.navigate('QRScreen')} />
          <Button title="Mon profil" variant="secondary" onPress={() => navigation.navigate('Profile')} />
          <Button title="Déconnexion" variant="secondary" onPress={handleLogout} />
        </View>
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: SIZES.padding, paddingBottom: 80 },
  card: {
    backgroundColor: '#fff',
    borderRadius: SIZES.radius,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#eee',
  },
  label: { fontSize: 14, color: '#7f8c8d', marginBottom: 2 },
  value: { fontSize: 16, fontWeight: '500', color: '#2c3e50', marginBottom: 12 },
  valid: { color: '#27ae60' },
  pending: { color: '#e67e22' },
  actions: { gap: 10 },
});