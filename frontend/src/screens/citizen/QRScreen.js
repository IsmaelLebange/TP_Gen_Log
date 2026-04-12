import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, ActivityIndicator, RefreshControl, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SIZES } from '../../constants/theme';
import Header from '../../components/organisms/Header';
import Footer from '../../components/organisms/Footer';
import Button from '../../components/atoms/Button';
import { fetchQRCode } from '../../api/qr';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { MEDIA_BASE_URL } from '../../constants/config';

export default function QRScreen({ navigation }) {
  const [qrData, setQrData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadQR = async () => {
    try {
      const data = await fetchQRCode();
      setQrData(data);
    } catch (err) {
      Alert.alert('Erreur', 'Impossible de charger la carte d’identité');
      console.log(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(useCallback(() => { loadQR(); }, []));

  const generatePDF = async () => {
    if (!qrData) return;

    const {
      nin,
      qr_code,
      nom,
      prenom,
      postnom,
      sexe,
      date_naissance,
      lieu_origine,
      adresse,
      nom_pere,
      nom_mere,
      photo_url,
    } = qrData;

    const formattedDate = date_naissance
      ? new Date(date_naissance).toLocaleDateString('fr-FR')
      : 'Non renseignée';

    let qrSrc = qr_code;
    if (!qrSrc.startsWith('data:image')) {
      qrSrc = `data:image/png;base64,${qrSrc}`;
    }

    const photoUrlFull = photo_url ? `${MEDIA_BASE_URL}${photo_url}` : null;
    const photoHtml = photoUrlFull
      ? `<img src="${photoUrlFull}" style="width:100%; height:100%; object-fit:cover; border-radius:4px;" />`
      : '<div class="photoIcon">👤</div>';

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Carte d'identité</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
            background: #E1E8EE;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Helvetica', 'Arial', sans-serif;
            padding: 20px;
          }
          .idCard {
            width: 100%;
            max-width: 800px;
            background: #F0F7FF;
            border-radius: 8px;
            border: 1px solid #AAB;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          }
          .header { text-align: center; border-bottom: 2px solid #CE1021; margin-bottom: 10px; padding-bottom: 5px; }
          .countryName { font-size: 18px; font-weight: bold; color: #003399; }
          .cardType { font-size: 14px; font-weight: bold; color: #CE1021; }
          .ninBar { margin-bottom: 10px; text-align: left; padding-left: 5px; }
          .ninText { font-size: 14px; font-weight: bold; color: #CE1021; }
          .mainBody { display: flex; flex-direction: row; flex-wrap: wrap; }
          .leftCol { width: 25%; padding-right: 10px; }
          .photoBox { width: 100%; aspect-ratio: 1; background: #DDD; border-radius: 4px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
          .photoIcon { font-size: 50px; }
          .parentsBox { margin-top: 10px; }
          .parentLabel { font-size: 10px; color: #555; margin-bottom: 2px; }
          .parentValue { font-size: 12px; font-weight: bold; margin-bottom: 6px; }
          .midCol { flex: 1; padding: 0 10px; }
          .infoField { margin-bottom: 8px; }
          .label { font-size: 10px; color: #444; display: inline-block; width: 90px; }
          .value { font-size: 11px; font-weight: bold; color: #000; text-transform: uppercase; display: inline-block; }
          .rightCol { width: 25%; text-align: center; }
          .qrWrapper { margin-bottom: 15px; display: flex; justify-content: center; }
          .qrImg { width: 100px; height: 100px; }
          .dateLabel { font-size: 9px; color: #444; }
          .dateValue { font-size: 11px; font-weight: bold; }
          .sigText { font-size: 8px; font-style: italic; margin-top: 5px; }
          @media (max-width: 600px) {
            .leftCol, .rightCol { width: 100%; margin-bottom: 15px; }
            .midCol { width: 100%; }
            .photoBox { width: 150px; margin: 0 auto; }
            .qrWrapper { margin-top: 15px; }
          }
        </style>
      </head>
      <body>
        <div class="idCard">
          <div class="header">
            <div class="countryName">RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</div>
            <div class="cardType">CARTE D'IDENTITÉ</div>
          </div>
          <div class="ninBar">
            <div class="ninText">NIN : ${nin || ''}</div>
          </div>
          <div class="mainBody">
            <div class="leftCol">
              <div class="photoBox">
                ${photoHtml}
              </div>
              <div class="parentsBox">
                <div class="parentLabel">Nom du père :</div>
                <div class="parentValue">${nom_pere || 'Non renseigné'}</div>
                <div class="parentLabel">Nom de la mère :</div>
                <div class="parentValue">${nom_mere || 'Non renseigné'}</div>
              </div>
            </div>
            <div class="midCol">
              <div class="infoField"><span class="label">Nom :</span><span class="value">${nom || ''}</span></div>
              <div class="infoField"><span class="label">Postnom/Prénom :</span><span class="value">${postnom || ''} ${prenom || ''}</span></div>
              <div class="infoField"><span class="label">Date / Lieu naiss. :</span><span class="value">${formattedDate} ${lieu_origine || ''}</span></div>
              <div class="infoField"><span class="label">Sexe :</span><span class="value">${sexe === 'MASCULIN' ? 'M' : sexe === 'FEMININ' ? 'F' : ''}</span></div>
              <div class="infoField"><span class="label">Adresse :</span><span class="value">${adresse || 'Non renseignée'}</span></div>
              <div class="infoField"><span class="label">Origine :</span><span class="value">${lieu_origine || 'Non renseignée'}</span></div>
            </div>
            <div class="rightCol">
              <div class="qrWrapper">
                <img src="${qrSrc}" class="qrImg" />
              </div>
              <div class="dateLabel">Fait à Kinshasa, le</div>
              <div class="dateValue">${new Date().toLocaleDateString('fr-FR')}</div>
              <div class="sigText">Le Délégué du Gouvernement</div>
            </div>
          </div>
        </div>
      </body>
      </html>
    `;

    try {
      const { uri } = await Print.printToFileAsync({ html: htmlContent });
      await Sharing.shareAsync(uri);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de générer le PDF');
    }
  };

  if (loading) return <ActivityIndicator size="large" color={COLORS.primary} style={{ flex: 1 }} />;

  const {
    nin,
    qr_code,
    nom,
    prenom,
    postnom,
    sexe,
    date_naissance,
    lieu_naissance,
    lieu_origine,
    adresse,
    nom_pere,
    nom_mere,
    photo_url,
  } = qrData || {};

  const formattedDate = date_naissance
    ? new Date(date_naissance).toLocaleDateString('fr-FR')
    : 'Non renseignée';

  const postnomPrenom = `${postnom ? postnom + ' ' : ''}${prenom || ''}`.trim();
  const photoFullUrl = photo_url ? `${MEDIA_BASE_URL}${photo_url}` : null;

  return (
    <View style={{ flex: 1, backgroundColor: '#E1E8EE' }}>
      <Header title="Carte d'Identité Nationale" showBack onBack={() => navigation.goBack()} />
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadQR} />}
      >
        <View style={styles.idCard}>
          <View style={styles.header}>
            <Text style={styles.countryName}>RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</Text>
            <Text style={styles.cardType}>CARTE D'IDENTITÉ</Text>
          </View>
          <View style={styles.ninBar}>
            <Text style={styles.ninText}>NIN : {nin || 'Non renseigné'}</Text>
          </View>
          <View style={styles.mainBody}>
            <View style={styles.leftCol}>
              <View style={styles.photoBox}>
                {photoFullUrl ? (
                  <Image source={{ uri: photoFullUrl }} style={styles.photo} />
                ) : (
                  <Text style={styles.photoIcon}>👤</Text>
                )}
              </View>
              <View style={styles.parentsBox}>
                <Text style={styles.parentLabel}>Nom du père :</Text>
                <Text style={styles.parentValue}>{nom_pere || 'Non renseigné'}</Text>
                <Text style={styles.parentLabel}>Nom de la mère :</Text>
                <Text style={styles.parentValue}>{nom_mere || 'Non renseigné'}</Text>
              </View>
            </View>
            <View style={styles.midCol}>
              <View style={styles.infoField}><Text style={styles.label}>Nom :</Text><Text style={styles.value}>{nom || ''}</Text></View>
              <View style={styles.infoField}><Text style={styles.label}>Postnom/Prénom :</Text><Text style={styles.value}>{postnomPrenom}</Text></View>
              <View style={styles.infoField}><Text style={styles.label}>Date / Lieu naiss. :</Text><Text style={styles.value}>{formattedDate} {lieu_naissance || ''}</Text></View>
              <View style={styles.infoField}><Text style={styles.label}>Sexe :</Text><Text style={styles.value}>{sexe === 'MASCULIN' ? 'M' : sexe === 'FEMININ' ? 'F' : ''}</Text></View>
              <View style={styles.infoField}><Text style={styles.label}>Adresse :</Text><Text style={styles.value}>{adresse || 'Non renseignée'}</Text></View>
              <View style={styles.infoField}><Text style={styles.label}>Origine :</Text><Text style={styles.value}>{lieu_origine || 'Non renseignée'}</Text></View>
            </View>
            <View style={styles.rightCol}>
              <View style={styles.qrWrapper}>
                {qr_code && (
                  <Image
                    source={{ uri: qr_code.startsWith('data:') ? qr_code : `data:image/png;base64,${qr_code}` }}
                    style={styles.qrImg}
                  />
                )}
              </View>
              <View style={styles.deliveryBox}>
                <Text style={styles.dateLabel}>Fait à Kinshasa, le</Text>
                <Text style={styles.dateValue}>
                  {new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                </Text>
                <Text style={styles.sigText}>Le Délégué du Gouvernement</Text>
              </View>
            </View>
          </View>
        </View>
        <Button title="Télécharger / Partager" onPress={generatePDF} style={styles.btn} />
      </ScrollView>
      <Footer />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 10, alignItems: 'center' },
  idCard: {
    width: '100%',
    aspectRatio: 1.58,
    backgroundColor: '#F0F7FF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#AAB',
    padding: 8,
    elevation: 5,
  },
  header: { alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#CE1021', marginBottom: 3 },
  countryName: { fontSize: 10, fontWeight: 'bold', color: '#003399' },
  cardType: { fontSize: 9, fontWeight: 'bold', color: '#CE1021' },
  ninBar: { alignItems: 'flex-start', paddingLeft: 5, marginBottom: 5 },
  ninText: { fontSize: 9, fontWeight: 'bold', color: '#CE1021' },
  mainBody: { flex: 1, flexDirection: 'row' },
  leftCol: { width: '25%', justifyContent: 'space-between' },
  photoBox: { width: 75, height: 90, backgroundColor: '#DDD', borderRadius: 4, justifyContent: 'center', alignItems: 'center', overflow: 'hidden' },
  photo: { width: '100%', height: '100%', resizeMode: 'cover' },
  photoIcon: { fontSize: 35 },
  parentsBox: { marginTop: 2 },
  parentLabel: { fontSize: 6, color: '#555' },
  parentValue: { fontSize: 7, fontWeight: 'bold', marginBottom: 1 },
  midCol: { flex: 1, paddingHorizontal: 5 },
  infoField: { marginBottom: 2 },
  label: { fontSize: 7, color: '#444' },
  value: { fontSize: 8, fontWeight: 'bold', color: '#000', textTransform: 'uppercase' },
  rightCol: { width: '25%', alignItems: 'center', justifyContent: 'space-between' },
  qrWrapper: { padding: 3, backgroundColor: '#FFF', borderRadius: 4, borderWidth: 1, borderColor: '#EEE' },
  qrImg: { width: 65, height: 65 },
  deliveryBox: { alignItems: 'center' },
  dateLabel: { fontSize: 6 },
  dateValue: { fontSize: 7, fontWeight: 'bold' },
  sigText: { fontSize: 5, fontStyle: 'italic', textAlign: 'center', marginTop: 5 },
  btn: { width: '100%', marginTop: 20 },
});