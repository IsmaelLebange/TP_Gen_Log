import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { useAuth } from "../../hooks/useAuth";
import { COLORS, SIZES } from "../../constants/theme";
import Header from "../../components/organisms/Header";
import Footer from "../../components/organisms/Footer";
import LoadingSpinner from "../../components/atoms/LoadingSpinner";
import { fetchDashboardStats } from "../../api/admin";

export default function AdminDashboardScreen({ navigation }) {
  const { signOut } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const handleLogout = () => {
    Alert.alert(
      "Déconnexion",
      "Voulez-vous vous déconnecter ?",
      [
        { text: "Annuler", style: "cancel" },
        {
          text: "Déconnecter",
          onPress: async () => {
            await signOut();
          },
        },
      ],
      { cancelable: true },
    );
  };

  const fetchStats = async () => {
    try {
      const data = await fetchDashboardStats();
      setStats(data);
    } catch (error) {
      Alert.alert("Erreur", "Impossible de charger les statistiques");
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

  const handleCardPress = (cardTitle) => {
    switch (cardTitle) {
      case "Citoyens enrôlés":
        navigation.navigate("Statistics");
        break;
      case "Documents en attente":
        navigation.navigate("DocumentValidation");
        break;
      case "Validations aujourd'hui":
        navigation.navigate("AuditLog");
        break;
      case "Agents actifs":
        navigation.navigate("Statistics");
        break;
      default:
        break;
    }
  };

  if (loading) return <LoadingSpinner />;

  const cards = [
    { title: "Citoyens enrôlés", value: stats?.total_citoyens || 0, icon: "👥", color: COLORS.primary },
    { title: "Documents en attente", value: stats?.pending_documents || 0, icon: "📄", color: "#e67e22" },
    { title: "Validations aujourd'hui", value: stats?.today_validations || 0, icon: "✅", color: "#27ae60" },
    { title: "Agents actifs", value: stats?.active_agents || 0, icon: "👮", color: "#3498db" },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.background }}>
      <Header
        title="Tableau de bord Admin"
        rightElement={
          <View style={{ flexDirection: 'row', gap: 10 }}>
            <TouchableOpacity onPress={() => navigation.navigate('Home')}>
              <Text style={{ fontSize: 24, color: COLORS.primary }}>🏠</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={handleLogout}>
              <Text style={{ fontSize: 24, color: COLORS.primary }}>🚪</Text>
            </TouchableOpacity>
          </View>
        }
      />
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.cardsGrid}>
          {cards.map((card, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.card, { borderTopColor: card.color }]}
              onPress={() => handleCardPress(card.title)}
              activeOpacity={0.7}
            >
              <Text style={styles.cardIcon}>{card.icon}</Text>
              <Text style={styles.cardValue}>{card.value}</Text>
              <Text style={styles.cardTitle}>{card.title}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.sectionTitle}>Actions rapides</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate("DocumentValidation")}>
            <Text style={styles.actionIcon}>📋</Text>
            <Text style={styles.actionText}>Valider documents</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate("AuditLog")}>
            <Text style={styles.actionIcon}>🔍</Text>
            <Text style={styles.actionText}>Consulter logs</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: SIZES.padding, paddingBottom: 80 },
  cardsGrid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between", marginBottom: 30 },
  card: {
    width: "48%",
    backgroundColor: "#fff",
    borderRadius: SIZES.radius,
    padding: 15,
    marginBottom: 15,
    borderTopWidth: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardIcon: { fontSize: 28, marginBottom: 8 },
  cardValue: { fontSize: 24, fontWeight: "bold", color: "#2c3e50" },
  cardTitle: { fontSize: 14, color: "#7f8c8d", marginTop: 4 },
  sectionTitle: { fontSize: 18, fontWeight: "bold", color: COLORS.primary, marginBottom: 15 },
  actionsGrid: { flexDirection: "row", gap: 15 },
  actionButton: {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: SIZES.radius,
    padding: 20,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#eee",
  },
  actionIcon: { fontSize: 32, marginBottom: 8 },
  actionText: { fontSize: 14, fontWeight: "600", color: COLORS.primary },
});