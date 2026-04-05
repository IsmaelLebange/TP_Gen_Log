// Importation directe du fichier JSON comme un module
import divisionsData from '../../assets/data/divisions.json';

export const loadDivisions = async () => {
  try {
    console.log("⏳ Chargement des divisions...");
    
    // Pas besoin de parser, le JSON est déjà un objet JS structuré
    const arbre = divisionsData;

    console.log("✅ Données chargées. Provinces :", Object.keys(arbre));
    return arbre;
  } catch (error) {
    console.error("❌ Erreur lors du chargement des divisions :", error);
    return {};
  }
};