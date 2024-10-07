import requests
import pandas as pd
import numpy as np
import time
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Obtenir les clés API à partir des variables d'environnement
BABBAR_API_KEY = os.getenv("BABBAR_API_KEY")
VALUE_SERP_API_KEY = os.getenv("VALUE_SERP_API_KEY")

print("Loading CSV file...")
df = pd.read_csv('coucou.csv', skipinitialspace=True)
print(df.head())

# Imprimez les noms des colonnes pour vérifier
print("Les colonnes détectées dans le fichier CSV sont : ", df.columns.tolist())

# Ajouter une colonne pour les URLs en 404 si elle n'existe pas.
if 'Urls en 404' not in df.columns:
    df['Urls en 404'] = 0

# Ajouter les colonnes clients si elles n'existent pas.
client_columns = ['BAS client', 'Nombre de RD client', 'Link client', 'Backlinks Internes client']
for col in client_columns:
    if col not in df.columns:
        df[col] = np.nan

# Vérifier la présence des colonnes nécessaires
if 'KEYWORD' not in df.columns or 'URL' not in df.columns:
    raise ValueError("Required columns 'KEYWORD' or 'URL' are not present in the CSV file")

def send_to_babbar(url, api_key):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    json_payload = {"url": url}

    if not isinstance(url, str) or pd.isnull(url):
        print(f"URL invalide ou manquante: {url}")
        return None, False

    for attempt in range(3):
        response = requests.post("https://www.babbar.tech/api/url/overview/main", headers=headers, json=json_payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"Réponse de l'API sous forme de liste, probablement vide, pour l'URL: {url}")
                return None, False
            print(f"Réponse complète de l'API Babbar pour l'URL client {url}:")
            print(data)

            return data, False
        elif response.status_code == 429:
            print(f"Taux limite atteint, attente de 20 secondes avant de réessayer... (Tentative {attempt+1}/3)")
            time.sleep(30)
        elif response.status_code == 404:
            print(f"Page non trouvée (404) pour l'URL client: {url}. Passage à la suivante.")
            return None, True
        else:
            print(f"Erreur lors de l'envoi de l'URL à Babbar: {url}, Statut: {response.status_code}")

    print(f"Échec après 3 tentatives pour l'URL client: {url}")
    return None, False

def calculate_median_and_min(metrics):
    return {
        'median': np.median(metrics) if metrics else np.nan,
        'min': np.min(metrics) if metrics else np.nan
    }

print("Début de l'analyse des URLs SERP et des URLs clients...")

# Boucle sur les lignes du DataFrame pour traiter les données SERP et client
for index, row in df.iterrows():
    keyword = row["KEYWORD"]
    print(f"Traitement du mot-clé: {keyword}")
    params = {
        'api_key': VALUE_SERP_API_KEY,
        'q': keyword,
        'location': 'France',
        'google_domain': 'google.fr',
        'gl': 'fr',
        'hl': 'fr',
        'device': 'mobile',
        'num': '10'
    }

    api_result = requests.get('https://api.valueserp.com/search', params=params)
    urls_in_404 = 0
    if api_result.status_code == 200:
        api_response = api_result.json()

        babbar_scores = []
        domain_counts = []
        link_counts = []
        internal_backlinks = []

        urls = [result['link'] for result in api_response.get('organic_results', [])]
        for url in urls:
            data, is_404 = send_to_babbar(url, BABBAR_API_KEY)
            if is_404:
                urls_in_404 += 1
            if data:
                babbar_scores.append(data.get('babbarAuthorityScore', 0))
                domain_counts.append(data.get('backlinks', {}).get('domainCount', 0))
                link_counts.append(data.get('backlinks', {}).get('linkCount', 0))
                internal_backlinks.append(data.get('backlinksInternal', 0))

        top3_metrics = {
            'babbar_scores': calculate_median_and_min(babbar_scores[:3]),
            'domain_counts': calculate_median_and_min(domain_counts[:3]),
            'link_counts': calculate_median_and_min(link_counts[:3]),
            'internal_backlinks': calculate_median_and_min(internal_backlinks[:3])
        }
        top5_metrics = {
            'babbar_scores': calculate_median_and_min(babbar_scores[:5]),
            'domain_counts': calculate_median_and_min(domain_counts[:5]),
            'link_counts': calculate_median_and_min(link_counts[:5]),
            'internal_backlinks': calculate_median_and_min(internal_backlinks[:5])
        }
        top10_metrics = {
            'babbar_scores': calculate_median_and_min(babbar_scores),
            'domain_counts': calculate_median_and_min(domain_counts),
            'link_counts': calculate_median_and_min(link_counts),
            'internal_backlinks': calculate_median_and_min(internal_backlinks)
        }

        df.at[index, 'Median BAS Top 3'] = top3_metrics['babbar_scores']['median']
        df.at[index, 'Min BAS Top 3'] = top3_metrics['babbar_scores']['min']
        df.at[index, 'Median Domain Count Top 3'] = top3_metrics['domain_counts']['median']
        df.at[index, 'Min Domain Count Top 3'] = top3_metrics['domain_counts']['min']
        df.at[index, 'Median Link Count Top 3'] = top3_metrics['link_counts']['median']
        df.at[index, 'Min Link Count Top 3'] = top3_metrics['link_counts']['min']
        df.at[index, 'Median Backlinks Internes Top 3'] = top3_metrics['internal_backlinks']['median']
        df.at[index, 'Min Backlinks Internes Top 3'] = top3_metrics['internal_backlinks']['min']

        df.at[index, 'Median BAS Top 5'] = top5_metrics['babbar_scores']['median']
        df.at[index, 'Min BAS Top 5'] = top5_metrics['babbar_scores']['min']
        df.at[index, 'Median Domain Count Top 5'] = top5_metrics['domain_counts']['median']
        df.at[index, 'Min Domain Count Top 5'] = top5_metrics['domain_counts']['min']
        df.at[index, 'Median Link Count Top 5'] = top5_metrics['link_counts']['median']
        df.at[index, 'Min Link Count Top 5'] = top5_metrics['link_counts']['min']
        df.at[index, 'Median Backlinks Internes Top 5'] = top5_metrics['internal_backlinks']['median']
        df.at[index, 'Min Backlinks Internes Top 5'] = top5_metrics['internal_backlinks']['min']

        df.at[index, 'Median BAS Top 10'] = top10_metrics['babbar_scores']['median']
        df.at[index, 'Min BAS Top 10'] = top10_metrics['babbar_scores']['min']
        df.at[index, 'Median Domain Count Top 10'] = top10_metrics['domain_counts']['median']
        df.at[index, 'Min Domain Count Top 10'] = top10_metrics['domain_counts']['min']
        df.at[index, 'Median Link Count Top 10'] = top10_metrics['link_counts']['median']
        df.at[index, 'Min Link Count Top 10'] = top10_metrics['link_counts']['min']
        df.at[index, 'Median Backlinks Internes Top 10'] = top10_metrics['internal_backlinks']['median']
        df.at[index, 'Min Backlinks Internes Top 10'] = top10_metrics['internal_backlinks']['min']

        df.at[index, 'Urls en 404'] = urls_in_404

    client_url = row['URL']
    client_data, is_404 = send_to_babbar(client_url, BABBAR_API_KEY)

    if client_data and isinstance(client_data, dict):
        babbar_authority_score = client_data.get('babbarAuthorityScore', np.nan)
        backlinks_data = client_data.get('backlinks', {})
        domain_count = backlinks_data.get('domainCount', np.nan)
        link_count = backlinks_data.get('linkCount', np.nan)
        backlinks_internal = client_data.get('backlinksInternal', np.nan)

        print(f"Enregistrement dans le fichier CSV :")
        print(f"- BAS client : {babbar_authority_score}")
        print(f"- Nombre de RD client : {domain_count}")
        print(f"- Link client : {link_count}")
        print(f"- Backlinks Internes client : {backlinks_internal}")

        df.at[index, 'BAS client'] = babbar_authority_score
        df.at[index, 'Nombre de RD client'] = domain_count
        df.at[index, 'Link client'] = link_count
        df.at[index, 'Backlinks Internes client'] = backlinks_internal
    else:
        print(f"Données non disponibles pour l'URL client: {client_url}")

df.to_csv('resultat-final.csv', index=False)
print("Les données des URLs SERP et des URLs clients ont été traitées et fusionnées dans 'resultat-final.csv'.")
