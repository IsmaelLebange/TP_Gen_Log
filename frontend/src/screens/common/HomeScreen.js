import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
  Alert,
} from 'react-native';
import { useAuth } from '../../hooks/useAuth';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import Button from '../../components/atoms/Button';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const { user, userToken, signOut } = useAuth();

  console.log("🔍 HomeScreen - user:", user);
  console.log("🔍 HomeScreen - userToken:", userToken);
  console.log("🔍 user?.role:", user?.role);

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

  const stats = [
    { label: 'Citoyens enrôlés', value: '1.2M', icon: '👥' },
    { label: 'Documents validés', value: '850K', icon: '📄' },
    { label: 'Agents actifs', value: '2.5K', icon: '👮' },
    { label: 'Provinces couvertes', value: '26', icon: '🗺️' },
  ];

  const actualites = [
    '📢 Lancement officiel du SEIP à Kinshasa',
    '⚙️ Maintenance prévue le 15 mai 2026',
    '📄 Nouveau format de carte d’identité',
    '🤝 Partenariat avec les banques nationales',
  ];

  const isLoggedIn = !!userToken;

  return (
    <View style={styles.container}>
      <Header title="SEIP - RDC" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Bannière */}
        <View style={styles.banner}>
          <Text style={styles.bannerTitle}>Système d’Enrôlement et d’Identification</Text>
          <Text style={styles.bannerSubtitle}>République Démocratique du Congo</Text>
          <Text style={styles.bannerText}>La solution moderne pour l’identification sécurisée des citoyens.</Text>
        </View>

        {/* Chiffres clés */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Chiffres clés</Text>
          <View style={styles.statsGrid}>
            {stats.map((s, i) => (
              <View key={i} style={styles.statCard}>
                <Text style={styles.statIcon}>{s.icon}</Text>
                <Text style={styles.statValue}>{s.value}</Text>
                <Text style={styles.statLabel}>{s.label}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Actualités */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Actualités</Text>
          <View style={styles.newsContainer}>
            {actualites.map((news, i) => (
              <View key={i} style={styles.newsItem}>
                <Text style={styles.newsText}>{news}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Connexion / espace personnel */}
        <View style={styles.authContainer}>
          {!isLoggedIn ? (
            <>
              <Button title="Se connecter" onPress={() => navigation.navigate('Login')} style={styles.authButton} />
              <Button title="Pré-enrôlement citoyen" variant="secondary" onPress={() => navigation.navigate('PreEnrollment')} style={styles.authButton} />
            </>
          ) : (
            <View style={styles.connectedContainer}>
              <Text style={styles.welcomeText}>Bonjour, {user?.prenom} {user?.nom}</Text>
              <Text style={styles.debugText}>✅ Connecté (rôle: {user?.role})</Text>
              
              {/* Les boutons citoyens sont accessibles à tout le monde (admin aussi) */}
              <Button title="Mon espace citoyen" onPress={() => navigation.navigate('User', { screen: 'Dashboard' })} style={styles.dashboardButton} />
              <Button title="Mon profil" onPress={() => navigation.navigate('User', { screen: 'Profile' })} style={styles.dashboardButton} variant="secondary" />
              
              {/* Bouton admin visible uniquement si rôle ADMIN */}
              {user?.role === 'ADMIN' && (
                <Button title="Tableau de bord Admin" onPress={() => navigation.navigate('Admin', { screen: 'AdminDashboard' })} style={styles.dashboardButton} />
              )}
              
              <Button title="Déconnexion" onPress={handleLogout} style={styles.dashboardButton} variant="secondary" />
            </View>
          )}
        </View>
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollContent: { paddingBottom: 40 },
  banner: {
    backgroundColor: COLORS.primary,
    paddingVertical: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    marginBottom: 20,
  },
  bannerTitle: { fontSize: 22, fontWeight: 'bold', color: '#fff', textAlign: 'center', marginBottom: 8 },
  bannerSubtitle: { fontSize: 14, color: '#fff', opacity: 0.9, marginBottom: 10 },
  bannerText: { fontSize: 16, color: '#fff', textAlign: 'center', paddingHorizontal: 20 },
  section: { paddingHorizontal: SIZES.padding, marginBottom: 30 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.primary, marginBottom: 15, borderLeftWidth: 4, borderLeftColor: COLORS.primary, paddingLeft: 10 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  statCard: {
    width: (width - 3 * SIZES.padding) / 2,
    backgroundColor: '#fff',
    borderRadius: SIZES.radius,
    padding: 15,
    marginBottom: 15,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ecf0f1',
  },
  statIcon: { fontSize: 28, marginBottom: 5 },
  statValue: { fontSize: 22, fontWeight: 'bold', color: '#2c3e50' },
  statLabel: { fontSize: 12, color: '#7f8c8d', textAlign: 'center' },
  newsContainer: { backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 10, borderWidth: 1, borderColor: '#ecf0f1' },
  newsItem: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#ecf0f1' },
  newsText: { fontSize: 14, color: '#2c3e50' },
  authContainer: { paddingHorizontal: SIZES.padding, marginBottom: 40 },
  authButton: { marginVertical: 8 },
  connectedContainer: { alignItems: 'center', backgroundColor: '#fff', borderRadius: SIZES.radius, padding: 20, borderWidth: 1, borderColor: '#ecf0f1' },
  welcomeText: { fontSize: 18, fontWeight: 'bold', color: COLORS.primary, marginBottom: 10 },
  debugText: { fontSize: 12, color: 'red', marginBottom: 15 },
  dashboardButton: { width: '100%', marginVertical: 5 },
});