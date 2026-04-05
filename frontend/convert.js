const fs = require('fs');

const content = fs.readFileSync('./assets/data/divisions.txt', 'utf-8');

const arbre = {};
let provinceActuelle = null;
let territoireActuel = null;

const lignes = content.split('\n');

lignes.forEach((ligne) => {
  const propre = ligne.trim();

  if (!propre || propre.includes('Nbre') || propre.startsWith("Niv.")) return;

  // Province
  const matchProvince = propre.match(/^\d+\s+([A-Za-z\- ]+)$/);
  if (matchProvince) {
    provinceActuelle = matchProvince[1].trim();
    arbre[provinceActuelle] = {};
    territoireActuel = null;
    return;
  }

  // Territoire
  const matchTerritoire = propre.match(/Territoire\s+(de|d')\s+(.+)/);
  if (matchTerritoire && provinceActuelle) {
    territoireActuel = matchTerritoire[2].trim();
    arbre[provinceActuelle][territoireActuel] = [];
    return;
  }

  // Secteur / Chefferie
  const matchSecteur = propre.match(/(Secteur|Chefferie)\s+(de|d')?\s*(.+)/);
  if (matchSecteur && territoireActuel && provinceActuelle) {
    const nom = matchSecteur[3]
      .replace(/\s+\d+$/, '')
      .trim();

    arbre[provinceActuelle][territoireActuel].push(nom);
  }
});

// 💾 Sauvegarde JSON
fs.writeFileSync(
  './assets/data/divisions.json',
  JSON.stringify(arbre, null, 2),
  'utf-8'
);

console.log("✅ JSON généré !");