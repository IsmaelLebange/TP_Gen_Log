import React, { useContext } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AuthContext } from '../../store/AuthContext';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';

export default function HomeScreen({ navigation }) {
  const { user, signOut } = useContext(AuthContext);

  const menuItems = [
    { 
      title: 'Nouvel Enrôlement', 
      icon: '👤', 
      route: 'EnrollmentForm', 
      desc: 'Enregistrer un nouveau citoyen' 
    },
    { 
      title: 'Biométrie', 
      icon: '🖐️', 
      route: 'Biometric', 
      desc: 'Capturer empreintes et iris' 
    },
    { 
      title: 'Documents', 
      icon: '📄', 
      route: 'DocumentUpload', 
      desc: 'Scanner les pièces justificatives' 
    },
    { 
      title: 'Statistiques', 
      icon: '📊', 
      route: 'Statistics', 
      desc: 'Voir les rapports d\'enrôlement' 
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <Header title="SEIP - ACCUEIL AGENT" />
      
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.welcomeSection}>
          <Text style={styles.welcomeText}>Bienvenue, {user?.prenom || 'Agent'}</Text>
          <Text style={styles.roleText}>Rôle : {user?.role || 'Opérateur'}</Text>
        </View>

        <View style={styles.grid}>
          {menuItems.map((item, index) => (
            <TouchableOpacity 
              key={index} 
              style={styles.card}
              onPress={() => navigation.navigate(item.route)}
            >
              <Text style={styles.icon}>{item.icon}</Text>
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardDesc}>{item.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity style={styles.logoutBtn} onPress={signOut}>
          <Text style={styles.logoutText}>Se déconnecter</Text>
        </TouchableOpacity>
      </ScrollView>

      <Footer />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: SIZES.padding },
  welcomeSection: { marginBottom: 25, paddingBottom: 15, borderBottomWidth: 1, borderBottomColor: '#ddd' },
  welcomeText: { fontSize: 22, fontWeight: 'bold', color: COLORS.primary },
  roleText: { fontSize: 14, color: '#666', marginTop: 5 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  card: { 
    width: '48%', 
    backgroundColor: '#fff', 
    padding: 15, 
    borderRadius: 10, 
    marginBottom: 15,
    elevation: 3, // Ombre Android
    shadowColor: '#000', // Ombre iOS
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
  },
  icon: { fontSize: 30, marginBottom: 10 },
  cardTitle: { fontSize: 16, fontWeight: 'bold', color: COLORS.secondary },
  cardDesc: { fontSize: 12, color: '#777', marginTop: 5 },
  logoutBtn: { marginTop: 20, padding: 15, alignItems: 'center', backgroundColor: '#fee', borderRadius: 8 },
  logoutText: { color: '#d32f2f', fontWeight: 'bold' }
});