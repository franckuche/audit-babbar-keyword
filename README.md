## Sommaire
- [Description](#description)
- [Prérequis](#prérequis)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Fonctionnement du script](#fonctionnement-du-script)
- Déroulement et gestion des erreurs (#deroulement-et-gestion-des-erreurs)
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
- **Python 3.x** : Assurez-vous que Python 3 est installé sur votre système. Vous pouvez le télécharger et l'installer depuis [python.org](https://www.python.org/downloads/).

- **Bibliothèques Python** : Ce script nécessite les bibliothèques `requests`, `pandas`, `numpy`, `time`, et `dotenv`. Ces dépendances peuvent être installées en utilisant le fichier `requirements.txt` présent dans votre répertoire de projet. Exécutez la commande suivante dans votre terminal pour installer ces bibliothèques :
  ```bash
  pip install -r requirements.txt

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
python3 main.py
```

## Fonctionnement du script

Le script commence par charger les données du fichier CSV coucou.csv. Il vérifie ensuite l'existence des colonnes KEYWORD et URL. Chaque mot-clé est traité individuellement pour récupérer les résultats de recherche via ValueSERP. Les URLs obtenues sont envoyées à l'API Babbar pour extraction des métriques SEO.

Pour chaque URL, le script effectue jusqu'à trois tentatives d'appel à l'API Babbar, gérant les problèmes comme les erreurs 404 ou les limites de taux d'appel. Les métriques recueillies sont utilisées pour calculer les médianes qui sont ensuite sauvegardées dans un DataFrame mis à jour.

Le traitement finalise avec la création d'un fichier CSV contenant toutes les médianes et le compte des URLs qui ont renvoyé une erreur 404, offrant ainsi une vue consolidée des métriques pour chaque mot-clé.

## Déroulement et gestion des erreurs

Lors de l'exécution du script, divers messages sont affichés dans le terminal pour indiquer l'état d'avancement et pour faciliter le débogage en cas d'erreurs. Voici un résumé du flux de messages et des vérifications d'erreurs intégrées au script :

### Messages du terminal

1. **Chargement du fichier CSV** : Le script commence par charger le fichier CSV avec les données initiales et affiche les premières lignes pour confirmation.

```bash
Loading CSV file...
```

2. **Vérification des colonnes** : Les noms des colonnes du fichier CSV sont imprimés pour s'assurer que les colonnes nécessaires (`KEYWORD` et `URL`) sont présentes.

```bash
Les colonnes détectées dans le fichier CSV sont : ['KEYWORD', 'URL', ...]
```

3. **Traitement par mot-clé** : Pour chaque mot-clé, le script affiche le traitement en cours, ce qui aide à suivre le processus pour chaque entrée.

```bash
Processing keyword: mot-clé spécifique
```


4. **Réponses et erreurs API** : Chaque appel à l'API affiche le résultat ou l'erreur correspondante, permettant une réaction immédiate en cas de problème.
- Succès :

  ```
  Successful API response from Babbar for [URL]. Metrics:
  - Babbar Authority Score: [score]
  - Hosts Count: [count]
  - Link Count: [count]
  - Internal Backlinks: [count]
  ```

- Limitation de débit :

  ```
  Rate limit reached, waiting 20 seconds before retrying... (Attempt X/3)
  ```

- Erreur 404 :

  ```
  Page not found (404) for URL: [URL]. Moving to the next one.
  ```

- Autres erreurs :
  ```
  Error sending URL to Babbar: [URL], Status: [status code]
  ```

5. **Échecs après tentatives multiples** :

```
Failed after 3 attempts for URL: [URL]
```

6. **Fin du traitement et sauvegarde** : À la fin du processus, un message confirme la sauvegarde des résultats dans le fichier CSV final.

```
The medians of the encountered data for the positioned URLs have been saved in 'resultat-median-babbar.csv'.
```


### Gestion des erreurs

Le script inclut une gestion proactive des erreurs :
- **Vérification des colonnes nécessaires** : Si les colonnes `KEYWORD` ou `URL` ne sont pas présentes, le script interrompt l'exécution et lève une exception.

```python
raise ValueError("Required columns 'KEYWORD' or 'URL' are not present in the CSV file")
```

- Gestion des réponses d'API : En cas d'erreurs courantes telles que les erreurs 404 ou les limites de taux d'appel, le script effectue des tentatives répétées et gère l'attente nécessaire entre les tentatives.
- Logs détaillés : Les messages imprimés dans le terminal offrent une vue claire de l'état d'avancement et des problèmes rencontrés, permettant un débogage rapide et efficace.


## Sortie

Le fichier resultat-median-babbar.csv contiendra les médianes des métriques Babbar pour chaque mot-clé ainsi que le nombre d'URLs en 404.
Les médianes sont privilégiées pour résumer les données, adaptées à des distributions avec des valeurs extrêmes ou non uniformes.

## Fonctions
send_to_babbar(url, api_key): Envoie une URL à l'API Babbar et retourne les métriques SEO.
Des logs sont générés tout au long du processus pour un suivi en temps réel de l'avancement et du traitement des données.

Le script inclut une gestion des erreurs pour les requêtes API, avec des tentatives répétées en cas d'erreurs courantes comme les dépassements de quota.
