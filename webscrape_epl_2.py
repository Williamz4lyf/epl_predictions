import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

#%%
# Download Pages
years = range(2021, 2024)
for year in years:
    url = f'https://fbref.com/en/comps/9/{year-1}-{year}/{year-1}-{year}-Premier-League-Stats'
    page = requests.get(url)

    with open(f'epl_seasons/{year}.html', 'w+') as file:
        file.write(page.text)

#%%
# Parse Data
epl_season = list()
teams = list()
years = range(2020, 2024)
for year in years:
    with open(f'epl_seasons/{year}.html') as file:
        page = file.read()
    soup = BeautifulSoup(page, 'html.parser')

    # Select first table
    standings_table = soup.select('table.stats_table')[0]
    # season_table = soup.find('table', id=f'switcher_results{year-1}-{year}91_overall')

    # Extract only the links from the table using the associated tag.
    links = standings_table.find_all('a')
    # Get only the href property from each link
    links = [l.get("href") for l in links]
    # Filter the links to get only those for the teams
    links = [l for l in links if '/squads/' in l]

    # Convert the filtered links into full urls, adding the domain part
    team_urls = [f"https://fbref.com{l}" for l in links]
    epl_season.append(team_urls)

epl_season

#%%
# Extract Match Stats

matches_df = list()
years = range(2020, 2024)
for year_links, year in zip(epl_season, years):
    for team_url in year_links:
        url = team_url
        # team_name = team_url[47:-6].replace('-', ' ')
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        page = requests.get(url)
        team_matches = pd.read_html(page.text, match="Scores & Fixtures")[0]
        page = requests.get(url)
        soup = BeautifulSoup(page.text)

        # Get links for Shooting Table
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")

        # Extract Shooting Table
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        try:
            team_data = team_matches.merge(shooting, 
                                           on=["Date", 'Time', 'Comp', 'Round',
                                               'Venue', 'Result', 'GF', 'GA',
                                               'Opponent', 'xG', 'Match Report'])
        except ValueError:
            continue

        # Extract EPL
        team_data = team_data[team_data["Comp"] == "Premier League"]

        team_data["Season"] = year
        team_data["Team"] = team_name
        matches_df.append(team_data)
        time.sleep(1)

match_df = pd.concat(matches_df)
match_df.to_csv('epl_20-23.csv', index=False)



#%%
match_df.head()



#%%
