# LLM Wiki — Compétence de Graphe de Connaissances Multimodal

> *« Le LLM écrit et maintient le wiki ; les humains lisent et posent des questions. »*

![Architecture LLM Wiki](../skills/llm-wiki/assets/llm-wiki.svg)

**Autres langues :** [English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [Español](README.es.md)

---

## Qu'est-ce que c'est ?

`llm-wiki` est une Skill fonctionnant dans Claude Code qui ingère des documents bruts de tout format (PDF, DOCX, PPTX, XLSX, Markdown, images) dans un Wiki structuré et construit automatiquement un graphe de connaissances interactif (`graph.html`).

Il met en œuvre la philosophie de gestion des connaissances proposée par Karpathy : **la connaissance est synthétisée au moment de l'ingestion, pas au moment de la requête**. Chaque fois qu'un nouveau document est ajouté, le LLM extrait automatiquement les points clés, établit des références croisées, signale les contradictions et met à jour le résumé de synthèse — permettant à la base de connaissances de croître de façon exponentielle à chaque ingestion.

La différence fondamentale avec RAG : RAG jette les documents bruts dans un magasin vectoriel et assemble les réponses à la volée au moment de la requête ; llm-wiki compile la connaissance en pages wiki durables au moment de l'ingestion, de sorte que les requêtes lisent des conclusions déjà synthétisées.

---

## Structure des Répertoires

```
<wiki-root>/
  raw/                  # Documents bruts (jamais modifiés)
    <topic>/            # Organisé par thème, sous-répertoires à un niveau
  wiki/
    index.md            # Table des matières de toutes les pages (partitionnée par thème)
    overview.md         # Synthèse vivante de toutes les sources
    log.md              # Journal d'opérations en ajout uniquement
    sources/            # Page de résumé pour chaque document brut
    entities/           # Personnes / entreprises / projets / produits
    concepts/           # Concepts / cadres / méthodologies
    syntheses/          # Réponses aux requêtes archivées
    archive/            # Pages obsolètes archivées
  graph/
    graph.json          # Données de nœuds + arêtes
    graph.html          # Visualisation autonome basée sur vis.js
```

---

## Référence des Commandes

| Commande | Objectif |
|---|---|
| `wiki-config workspace <path>` | Définir le chemin de l'espace de travail wiki |
| `wiki-config show` | Afficher la configuration actuelle et l'état des répertoires |
| `wiki-input <path> [--topic <slug>]` | Ingérer n'importe quel chemin de fichier (archive automatique vers `raw/<topic>/`) |
| `wiki-ingest <file>` | Ingérer un fichier déjà dans `raw/` |
| `wiki-query: <question>` | Interroger la base de connaissances, synthétiser la réponse |
| `wiki-lint` | Vérifier les pages orphelines, les liens brisés, les contradictions |
| `wiki-graph` | Construire le graphe de connaissances interactif (`graph.html`) |

**Recommandé pour un usage quotidien : `wiki-input`** — accepte des chemins locaux ou distants, copie automatiquement vers `raw/<topic>/` avant l'ingestion. Aucune gestion manuelle du répertoire `raw/` nécessaire.

---

## Flux de Travail

### Ingestion

Lors de l'ingestion d'un document, le LLM exécute séquentiellement :

1. Extraction de contenu multimodal (PDF/DOCX/PPTX/XLSX/images → Markdown)
2. Écriture de `wiki/sources/<slug>.md` (résumé, points clés, citations importantes)
3. Mise à jour de `wiki/index.md` et `wiki/overview.md`
4. Création ou mise à jour des pages `wiki/entities/` et `wiki/concepts/`
5. Signalement des contradictions avec le contenu existant
6. Ajout du journal d'opérations à `wiki/log.md`

### Requête

Lit `wiki/index.md` pour identifier les pages pertinentes, synthétise une réponse avec des références en ligne au format `[[PageName]]`. Optionnellement, archive la réponse sous `wiki/syntheses/<slug>.md`.

### Graphe de Connaissances

Extrait les wikilinks explicites (`EXTRACTED`) et les associations sémantiques inférées par l'IA (`INFERRED`, confiance ≥ 0.5) entre les pages, générant un `graph.html` autonome sans dépendances avec colorisation par type de nœud et groupement par communauté.

---

## Formats Supportés

| Format | Méthode d'Extraction |
|---|---|
| `.md` `.txt` | Lecture directe |
| `.pdf` | pdfplumber (texte + tableaux) |
| `.docx` | python-docx (corps + titres + tableaux) |
| `.pptx` | python-pptx (titres + corps + notes) |
| `.xlsx` `.csv` | pandas (converti en tableaux Markdown) |
| `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` | Claude vision (multimodal) |

---

## Support Multimodal Détaillé

`llm-wiki` utilise la capacité multimodale native de Claude pour comprendre le contenu des images — pas seulement la reconnaissance de texte OCR, mais une compréhension sémantique complète des diagrammes, graphiques et captures d'écran.

### Ingestion Directe de Fichiers Image

Passez directement n'importe quel fichier image à `wiki-input` ou `wiki-ingest`. Claude lit l'image et la convertit en Markdown structuré avant d'exécuter le flux d'ingestion standard :

```bash
wiki-input ~/captures/diagramme-architecture.png --topic system-design
wiki-input ~/photos/session-tableau-blanc.jpg --topic meetings
```

**Ce que Claude extrait des images :**
- **Graphiques & courbes** — séries de données, étiquettes d'axe, tendances, valeurs numériques
- **Diagrammes & organigrammes** — nœuds, arêtes, relations, direction du flux
- **Captures d'écran** — structure UI, texte visible, contexte de mise en page
- **Notes manuscrites / tableaux blancs** — texte transcrit et structures dessinées
- **Tableaux dans les images** — reconstruits en tableaux Markdown
- **Contenu mixte** — documents photographiés ou numérisés avec texte et figures

### Images Intégrées dans les Documents

Lors de l'ingestion de fichiers PDF, DOCX ou PPTX contenant des images intégrées, l'outil d'extraction respectif capture tout le contenu textuel. Pour les figures et diagrammes essentiels à la compréhension que l'extraction de texte seule ne couvre pas suffisamment, réingérez-les en tant qu'images autonomes.

### Formats d'Image Supportés

| Format | Notes |
|---|---|
| `.png` | Sans perte ; idéal pour captures d'écran, diagrammes |
| `.jpg` / `.jpeg` | Photos, documents numérisés |
| `.webp` | Images optimisées pour le web |
| `.gif` | La première image est analysée (contenu statique) |
| `.bmp` | Bitmap non compressé |

### Pipeline d'Extraction Multimodale

Tout le contenu image suit le même pipeline d'ingestion que les documents texte — l'image est simplement convertie en Markdown au préalable :

```
Fichier Image
    │
    ▼
Claude Vision (outil Read)
    │  Extrait : texte, structure, données, relations
    ▼
Description Markdown
    │
    ▼
Flux d'Ingestion Standard (Étapes 2–10)
    │  sources/ entities/ concepts/ index/ overview/ log/
    ▼
Pages Wiki + Graphe de Connaissances
```

---

## Démarrage Rapide

```bash
# 1. Définir l'espace de travail wiki
wiki-config workspace ~/my-wiki

# 2. Ingérer le premier document
wiki-input ~/Downloads/paper.pdf --topic papers

# 3. Requête
wiki-query: Quelle est la contribution principale de cet article ?

# 4. Construire le graphe de connaissances
wiki-graph
```

---

## Références

- [Anthropic Skills — Dépôt officiel de compétences](https://github.com/anthropics/skills)
- [Andrej Karpathy — LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [SamurAIGPT — llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)
