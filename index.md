# Gestionnaire d'énergie multiboard

Le **Power Manager multiboard** de [Catroniq](https://catroniq.com/2022/11/01/gestionnaire-energetique-multi-circuits/) mesure la consommation de 2 à 42 circuits de votre panneau électrique avec des pinces ampèremétriques (CT). Les mesures arrivent directement dans [Home Assistant](https://www.home-assistant.io/) grâce à [ESPHome](https://esphome.io/).

**[Voir le kit et la documentation sur catroniq.com](https://catroniq.com/2022/11/01/gestionnaire-energetique-multi-circuits/)**

## Fonctions

- Carte principale ESP32 avec 2 entrées de pince, plus jusqu'à 5 cartes d'extension de 8 entrées : 2, 10, 18, 26, 34 ou 42 circuits
- Pinces CT de 5, 10, 15, 20, 25, 30, 50, 60 ou 100 A, à sortie 1 V, 0,5 V ou 0,333 V
- Courant (A), puissance (kW) et énergie du jour (kWh) pour chaque circuit, plus le total de la carte
- Circuits 120 V, 240 V (Amérique du Nord) ou 230 V (Europe)
- Réglage des pinces directement dans Home Assistant, sans modifier de code
- Un appareil Home Assistant par circuit
- Mises à jour proposées par Home Assistant
- Écran OLED qui affiche les mesures en boucle
- Page web intégrée, utilisable même sans Home Assistant

## Prérequis

- Home Assistant **2025.7** ou plus récent
- Pour les utilisateurs d'ESPHome : ESPHome **2025.7** ou plus récent

## Installation

1. Choisissez la langue des noms dans Home Assistant (français ou anglais), puis le nombre de circuits de votre montage : 2 pour la carte principale seule, puis 8 de plus par carte d'extension.
2. Branchez la carte principale à votre ordinateur avec un câble USB et cliquez sur le bouton. Le firmware s'installe depuis votre navigateur, puis la page vous demande votre réseau Wi-Fi.

<label for="lang"><strong>Langue dans Home Assistant :</strong></label>
<select id="lang">
  <option value="-fr" selected>Français</option>
  <option value="">English</option>
</select>

<label for="size"><strong>Nombre de circuits :</strong></label>
<select id="size">
  <option value="02">2 circuits (carte principale seule)</option>
  <option value="10" selected>10 circuits (1 carte d'extension)</option>
  <option value="18">18 circuits (2 cartes d'extension)</option>
  <option value="26">26 circuits (3 cartes d'extension)</option>
  <option value="34">34 circuits (4 cartes d'extension)</option>
  <option value="42">42 circuits (5 cartes d'extension)</option>
</select>

<script type="module" src="https://unpkg.com/esp-web-tools@10.4.0/dist/web/install-button.js?module"></script>
<p><esp-web-install-button id="install" manifest="./power-manager-multi-10-fr/manifest.json"></esp-web-install-button></p>
<script>
  function updateManifest() {
    var size = document.getElementById("size").value;
    var lang = document.getElementById("lang").value;
    document.getElementById("install").manifest = "./power-manager-multi-" + size + lang + "/manifest.json";
  }
  document.getElementById("size").addEventListener("change", updateManifest);
  document.getElementById("lang").addEventListener("change", updateManifest);
</script>

- Fonctionne avec **Chrome** ou **Edge** sur ordinateur (pas sur Firefox, Safari ni téléphone).
- Si la carte n'est pas détectée :
  1. Vérifiez votre câble USB. Plusieurs câbles (souvent ceux fournis avec des écouteurs ou des lampes) servent seulement à la recharge et ne transportent pas les données. Essayez un câble qui permet de transférer des fichiers vers un téléphone.
  2. Installez le [pilote USB CH340](https://www.wch-ic.com/downloads/CH341SER_EXE.html), puis débranchez et rebranchez la carte.

Une fois la carte connectée au Wi-Fi, Home Assistant la détecte automatiquement : ouvrez **Paramètres → Appareils et services** et cliquez sur **Configurer** sous ESPHome.

## Ajouter une carte d'extension

Vous passez de 10 à 18 circuits ? Branchez la nouvelle carte d'extension, revenez sur cette page, choisissez le nouveau nombre de circuits (**dans la même langue**) et réinstallez par USB.

**Vos réglages sont conservés** : les circuits déjà configurés gardent leur pince, leur tension, leur correction et leur historique dans Home Assistant. Seuls les nouveaux circuits apparaissent, désactivés (**Aucune**).

## Mises à jour

Quand une nouvelle version est publiée, Home Assistant affiche **Mise à jour disponible** dans **Paramètres → Mises à jour**. Cliquez sur **Installer** : la carte télécharge et installe le nouveau firmware par Wi-Fi, sans câble. La carte vérifie les mises à jour toutes les 6 heures.

Les mises à jour gardent la langue choisie à l'installation. Pour changer de langue, réinstallez par USB : les noms changent, donc Home Assistant crée de nouvelles entités et les réglages des circuits sont à refaire.

## Configuration des pinces

Dans Home Assistant, chaque circuit apparaît comme un appareil séparé (**PM A1**, **PM B0**…), relié à la carte. Il regroupe ses mesures (courant, puissance, énergie) et ses réglages. Les noms suivent ceux imprimés sur les cartes :

| Carte | Connecteurs |
|---|---|
| Carte principale | A1, A2 |
| 1re carte d'extension | B0 à B7 |
| 2e carte d'extension | C0 à C7 |
| 3e carte d'extension | D0 à D7 |
| 4e carte d'extension | E0 à E7 |
| 5e carte d'extension | F0 à F7 |

Par défaut, tous les circuits sont à **Aucune** (None, désactivés) pour éviter les valeurs au hasard sur les entrées sans pince. Pour chaque circuit utilisé, ouvrez son appareil dans Home Assistant, section **Configuration**, puis choisissez :

| Réglage | Valeurs | Description |
|---|---|---|
| Modèle de pince (CT Model) | Aucune, 5 A … 100 A | Calibre de la pince (inscrit sur la pince) |
| Sortie de pince (CT Output) | 1 V, 0.5 V, 0.333 V | Tension de sortie de la pince à pleine charge |
| Type de disjoncteur (Breaker Type) | Simple 120 V, Double 240 V, Simple 230 V | Disjoncteur simple ou double (voir ci-dessous) |
| Correction de pince (CT Correction) | 50 à 150 % | Ajustement fin, à comparer avec une pince ampèremétrique de référence |
| Numéro de disjoncteur (Breaker Number) | 0 à 80 | Numéro du disjoncteur dans le panneau (0 = non indiqué). Pour un double, entrez le premier : 29 donne « 29-31 » |
| Note | texte, 32 caractères | Ce que le circuit alimente, par exemple « Laveuse à linge » |

Les réglages sont conservés dans la carte, même après une panne de courant ou une mise à jour.

Sur l'appareil de la carte, réglez aussi **Taille du panneau** (Panel Size) : le nombre de positions de votre panneau (1 à 80). Un numéro de disjoncteur plus grand que le panneau est refusé et remis à 0.

Astuce : renommez l'appareil d'un circuit dans Home Assistant (par exemple « Sécheuse ») et toutes ses mesures suivent.

### Disjoncteur simple ou double ?

| Circuit | Pinces | Type de disjoncteur |
|---|---|---|
| Amérique du Nord, circuit 120 V (prises, éclairage) | 1 pince | Simple 120 V |
| Amérique du Nord, 240 V sans neutre (plinthes, chauffe-eau, thermopompe) | 1 pince sur **un seul** des deux fils | Double 240 V |
| Amérique du Nord, 240 V avec neutre (sécheuse, cuisinière) | 1 pince : approximation correcte · 2 pinces (une par fil) : mesure exacte | 1 pince : Double 240 V · 2 pinces : Simple 120 V chacune, puis additionner |
| Entrée principale du panneau | 2 pinces, une par phase | Simple 120 V chacune, puis additionner |
| Europe (monophasé) | 1 pince | Simple 230 V |

**Important :** ne refermez jamais une pince autour des deux fils d'un même circuit. Le courant circule en sens inverse dans chaque fil, les deux s'annulent et la pince lit 0.

## Utilisateurs d'ESPHome

Vous pouvez aussi adopter la carte dans le tableau de bord ESPHome, ou copier le fichier YAML de votre nombre de circuits (`power-manager-multi-10-fr.yaml` en français, `power-manager-multi-10.yaml` en anglais, etc.) depuis le [dépôt GitHub](https://github.com/djiesr/JLNTR2K4.MB-power-manager-multi).

---

[catroniq.com](https://catroniq.com/2022/11/01/gestionnaire-energetique-multi-circuits/)
