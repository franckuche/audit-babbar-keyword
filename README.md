## Sommaire
- [Description](#description)
- [Prérequis](#prérequis)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Fonctionnement du script](#fonctionnement-du-script)
- [Sortie](#sortie)
- [Fonctions](#fonctions)

## Description
Ce script Python automatise l'audit de mots-clés en utilisant les API de Babbar et ValueSERP pour extraire et analyser les métriques SEO pertinentes. Il effectue les tâches suivantes :

1. Charge un fichier CSV contenant des mots-clés et des URLs pour analyse.
2. Pour chaque mot-clé, extrait les résultats organiques de Google via l'API ValueSERP.
3. Envoie chaque URL à l'API Babbar pour obtenir des métriques comme le score d'autorité Babbar, le nombre d'hôtes, le nombre de liens et le nombre de backlinks internes.
4. Calcule les médianes de ces métriques pour chaque mot-clé.
5. Met à jour le DataFrame avec les médianes calculées.
6. Sauvegarde les résultats finaux dans un nouveau fichier CSV.

## Prérequis
- Python 3.x
- Bibliothèques Python : `requests`, `pandas`, `numpy`, `time`, `dotenv`

## Configuration
1. Créez un fichier `.env` à la racine du projet pour stocker les clés API de manière sécurisée :
```plaintext
BABBAR_API_KEY=votre_clé_api_babbar
VALUE_SERP_API_KEY=votre_clé_api_valueserp
```
2. Assurez-vous que le fichier CSV nommé coucou.csv, situé dans le même répertoire que le script, contient les colonnes nécessaires KEYWORD et URL. Le script soulèvera une erreur si ces colonnes ne sont pas présentes.

## Utilisation
Placez le fichier CSV coucou.csv dans le même répertoire que le script.
Exécutez le script en utilisant la commande suivante :

```bash
python3 script.py
```

## Fonctionnement du script

Le script commence par charger les données du fichier CSV coucou.csv. Il vérifie ensuite l'existence des colonnes KEYWORD et URL. Chaque mot-clé est traité individuellement pour récupérer les résultats de recherche via ValueSERP. Les URLs obtenues sont envoyées à l'API Babbar pour extraction des métriques SEO.

Pour chaque URL, le script effectue jusqu'à trois tentatives d'appel à l'API Babbar, gérant les problèmes comme les erreurs 404 ou les limites de taux d'appel. Les métriques recueillies sont utilisées pour calculer les médianes qui sont ensuite sauvegardées dans un DataFrame mis à jour.

Le traitement finalise avec la création d'un fichier CSV contenant toutes les médianes et le compte des URLs qui ont renvoyé une erreur 404, offrant ainsi une vue consolidée des métriques pour chaque mot-clé.

## Sortie

Le fichier resultat-median-babbar.csv contiendra les médianes des métriques Babbar pour chaque mot-clé ainsi que le nombre d'URLs en 404.
Les médianes sont privilégiées pour résumer les données, adaptées à des distributions avec des valeurs extrêmes ou non uniformes.

## Fonctions
send_to_babbar(url, api_key): Envoie une URL à l'API Babbar et retourne les métriques SEO.
Des logs sont générés tout au long du processus pour un suivi en temps réel de l'avancement et du traitement des données.

Le script inclut une gestion des erreurs pour les requêtes API, avec des tentatives répétées en cas d'erreurs courantes comme les dépassements de quota.
