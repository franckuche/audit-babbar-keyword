import requests
import pandas as pd
import numpy as np
import time
from dotenv import load_dotenv
import os

print("Loading CSV file...")
df = pd.read_csv('coucou.csv')
print(df.head())

# Ajouter une colonne pour les URLs en 404 si elle n'existe pas
if 'Urls en 404' not in df.columns:
    df['Urls en 404'] = 0

# Vérifier la présence des colonnes nécessaires
if 'KEYWORD' not in df.columns or 'URL' not in df.columns:
    raise ValueError("Required columns 'KEYWORD' or 'URL' are not present in the CSV file")

# Configuration des clés API
BABBAR_API_KEY = "0qZjejHfO2gyKrG626SNah0h2Wl7wLRO5C61wCsBJ03C8t4xX2JznvJ4cb7S"
VALUE_SERP_API_KEY = "C25E576BDB1B461CA233A9905E909031"

def send_to_babbar(url, api_key):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    for attempt in range(3):
        response = requests.post("https://www.babbar.tech/api/url/overview/main", headers=headers, json={"url": url})
        if response.status_code == 200:
            data = response.json()

            babbar_score = data.get('babbarAuthorityScore', 'No data')
            host_count = data.get('backlinks', {}).get('hostCount', 'No data')  # Correct orthography for hostCount
            link_count = data.get('backlinks', {}).get('linkCount', 'No data')
            internal_backlink = data.get('backlinksInternal', 'No data')

            print(f"Successful API response from Babbar for {url}. Metrics:")
            print(f"- Babbar Authority Score: {babbar_score}")
            print(f"- Hosts Count: {host_count}")  # Now correctly displaying the data
            print(f"- Link Count: {link_count}")
            print(f"- Internal Backlinks: {internal_backlink}")

            return data
        elif response.status_code == 429:
            print(f"Rate limit reached, waiting 20 seconds before retrying... (Attempt {attempt+1}/3)")
            time.sleep(20)
        elif response.status_code == 404:
            print(f"Page not found (404) for URL: {url}. Moving to the next one.")
            return None
        else:
            print(f"Error sending URL to Babbar: {url}, Status: {response.status_code}")
    print(f"Failed after 3 attempts for URL: {url}")
    return None

for index, row in df.iterrows():
    keyword = row['KEYWORD']
    print(f"Processing keyword: {keyword}")
    params = {
        'api_key': VALUE_SERP_API_KEY,
        'q': keyword,
        'location': 'France',
        'google_domain': 'google.fr',
        'gl': 'fr',
        'hl': 'fr',
        'device': 'mobile'
    }

    api_result = requests.get('https://api.valueserp.com/search', params=params)
    if api_result.status_code == 200:
        api_response = api_result.json()

        babbar_scores = []
        hosts_counts = []  # Pour le calcul de la médiane
        link_counts = []
        internal_backlinks = []
        excluded_results = 0

        urls = [result['link'] for result in api_response.get('organic_results', [])]
        for url in urls:
            data = send_to_babbar(url, BABBAR_API_KEY)
            if data:
                babbar_scores.append(data.get('babbarAuthorityScore', np.nan))
                # Convertir 'No data' en np.nan et s'assurer que les valeurs sont numériques
                host_count = data.get('backlinks', {}).get('hostCount')
                hosts_counts.append(np.nan if host_count in [None, 'No data'] else float(host_count))
                link_counts.append(data.get('backlinks', {}).get('linkCount', np.nan))
                internal_backlinks.append(data.get('backlinksInternal', np.nan))
            else:
                excluded_results += 1

        median_babbar_score = np.nanmedian(babbar_scores) if babbar_scores else np.nan
        median_hosts_count = np.nanmedian(hosts_counts) if hosts_counts else np.nan  # Médiane correctement calculée
        median_link_count = np.nanmedian(link_counts) if link_counts else np.nan
        median_internal_backlinks = np.nanmedian(internal_backlinks) if internal_backlinks else np.nan

        # Mise à jour du DataFrame avec les médianes calculées
        df.at[index, 'Babbar Authority Score'] = median_babbar_score
        df.at[index, 'Hosts Count'] = median_hosts_count  # Correctement mis à jour
        df.at[index, 'Link Count'] = median_link_count
        df.at[index, 'Internal Backlinks'] = median_internal_backlinks
        df.at[index, 'Urls en 404'] = excluded_results

        print(f"Data for keyword '{keyword}':")
        print(f"- Babbar Authority Score: {median_babbar_score}")
        print(f"- Hosts Count: {median_hosts_count if not np.isnan(median_hosts_count) else 'No data available'}")
        print(f"- Link Count: {median_link_count if not np.isnan(median_link_count) else 'No data available'}")
        print(f"- Internal Backlinks: {median_internal_backlinks if not np.isnan(median_internal_backlinks) else 'No data available'}")
        print(f"Excluded {excluded_results} results from the calculation due to 404 errors.")

# Sauvegarde des résultats finaux dans un nouveau fichier CSV
df.to_csv('resultat-median-babbar.csv', index=False)
print("The medians of the encountered data for the positioned URLs have been saved in 'resultat-median-babbar.csv'.")