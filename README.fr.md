# Dr. DevLove
### *ou : Comment j'ai appris à arrêter la paralysie de l'analyse et à aimer écrire des quantités massives de code*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)

> "Messieurs, vous ne pouvez pas vous battre ici ! C'est la salle de guerre !" — *Dr. Strangelove*
>
> "Développeurs, vous ne pouvez pas trop réfléchir ici ! C'est l'IDE !" — *Dr. DevLove*

Vous en avez assez de fixer un curseur clignotant ? Vous souffrez de *paralysie de l'analyse* chronique ? Vous passez plus de temps à planifier votre code qu'à l'écrire ?

**Dr. DevLove** (alias `gh-stats`) est votre prescription. C'est un outil CLI qui prouve que vous *travaillez*. Il valide votre existence en suivant vos contributions quotidiennes sur GitHub, sans avoir besoin de clones locaux.

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 La Prescription (Caractéristiques)

*   **Diagnostic à distance**: Scanne votre activité GitHub directement via l'API. Pas de dépôts locaux requis.
*   **Signes vitaux**: Sortie terminal colorée avec barres de progression.
*   **Traitement évolutif**: Projets personnels et organisations.
*   **Voyage dans le temps**: `today` (aujourd'hui), `yesterday` (hier), `thisweek` (cette semaine), `lastweek` (la semaine dernière), etc.
*   **Collecte de preuves**: Exportez tous les messages de commit dans un fichier Markdown. Parfait pour l'analyse IA ou les rapports de performance.
*   **Mode Triage**: Trie automatiquement les dépôts par date de push.

## 📥 Ingestion (Installation)

```bash
brew install gh
gh auth login
gh auth refresh -s read:org  # Requis pour les organisations
```

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 Dosage (Utilisation)

```bash
# Vérifiez que vous avez fait quelque chose aujourd'hui
poetry run gh-stats --range today

# Exportez les commits de la semaine dernière pour un résumé IA
poetry run gh-stats --range lastweek --export-commits
```

### Paramètres

| Flag | Effet | Défaut |
| :--- | :--- | :--- |
| `--range` | Raccourci de date (`today`, `yesterday`, `lastweek`, `3days`) | Aucun |
| `--no-personal` | Exclure les dépôts personnels | - |
| `--export-commits` | Exporte les messages en Markdown | False |
| `--all-branches` | Scanne toutes les branches actives | False |

## 📄 Licence

MIT. Faites ce que vous voulez, écrivez juste du code.
