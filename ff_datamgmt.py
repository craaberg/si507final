# This module is used to pull in the data and store it in python objects to be used
# for processing. This file is responsible for webscaping, making API calls, reading
# in files.
from typing import Dict, Union, Any

import requests
import csv
import json
import ff_keys as keys
from bs4 import BeautifulSoup
from itertools import zip_longest


TEAM_NAMES = {
    'Cardinals': 'Ari',
    'Falcons': 'Atl',
    'Ravens': 'Bal',
    'Bills': 'Buf',
    'Panthers': 'Car',
    'Bears': 'Chi',
    'Bengals': 'Cin',
    'Browns': 'Cle',
    'Cowboys': 'Dal',
    'Broncos': 'Den',
    'Lions': 'Det',
    'Packers': 'GB',
    'Texans': 'Hou',
    'Colts': 'Ind',
    'Jaguars': 'Jax',
    'Chiefs': 'KC',
    'Chargers': 'LAC',
    'Rams': 'LAR',
    'Raiders': 'LV',
    'Dolphins': 'Mia',
    'Vikings': 'Min',
    'Patriots': 'NE',
    'Saints': 'NO',
    'Giants': 'NYG',
    'Jets': 'NYJ',
    'Eagles': 'Phi',
    'Steelers': 'Pit',
    'Seahawks': 'Sea',
    '49ers': 'SF',
    'Buccaneers': 'TB',
    'Titans': 'Ten',
    'Commanders': 'Wsh'
}


def grouper(iterable, n, fillvalue=None):
    """
    This is pulled from the recipes of the itertools page
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    "Collect data into non-overlapping fixed-length chunks or blocks"
    Parameters
    ----------
    iterable: list
        any iterable that you want to group
    n: int
        the number you want the elements grouped by
    fillvalue: str
        The value you would like to fill in if therea re any empties

    Returns
    -------
    list that is grouped

    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def get_player_season_stats():
    """
    pulls the season stats of an individual player from the sportsdataio database and formats
    the data into a dictionary with the unique player key of last name, position, team abbreviation

    Returns
    -------
    dictionary containing the player's season stats
    """
    player_season_stats_dict = {}
    response_sportsdataio_player_season_stats = requests.get(f'https://api.sportsdata.io/v3/nfl/stats/json/'
                                                             f'PlayerSeasonStats/2021REG?'
                                                             f'key={keys.SPORTDATAIO_FANTASY_DATA_KEY}')
    player_season_stats_results = response_sportsdataio_player_season_stats.json()
    for player in player_season_stats_results:
        player_season_stats_dict[player['Name'].split(".")[1].casefold() + player['Position'].casefold() + player['Team'].casefold()] = player
    return player_season_stats_dict


def get_sportio_player_proj():
    """
    pulls the sportsio projections for the players for the upcoming and formats
    the data into a dictionary with the unique player key of last name, position, team abbreviation
    Returns
    -------
    dictionary containing the player's projection stats for the year
    """
    player_proj_stats_dict = {}
    response_sportsdataio_player_proj_stats = requests.get(f'https://api.sportsdata.io/v3/nfl/projections/json/'
                                                           f'PlayerSeasonProjectionStats/2022?'
                                                           f'key={keys.SPORTDATAIO_FANTASY_DATA_KEY}')
    player_proj_stats_results = response_sportsdataio_player_proj_stats.json()
    for player in player_proj_stats_results:
        player_proj_stats_dict[player['Name'].split(" ")[1].casefold() + player['Position'].casefold() + player['Team'].casefold()] = player
    return player_proj_stats_dict


# TODO weekly player stats, will build this out if I have time
# NBR_SEASON_GAMES = 17
# player_weekly_stats_results = []
# for week in range(NBR_SEASON_GAMES):
#     response_sportsdataio_player_weekly_stats = requests.get(f'https://api.sportsdata.io/v3/nfl/stats/json/'
#                                                          f'PlayerGameStatsByWeek/2021REG/{week+1}?'
#                                                          f'key={keys.SPORTDATAIO_FANTASY_DATA_KEY}')
#     player_weekly_stats_results.append(response_sportsdataio_player_weekly_stats.json())


def get_espn_player_projections():
    """
    pulls the csv data containing top 300 players and the espn projection for their stats
    Returns
    -------
    a dictionary of dictionary items representing espn player values with the key being
    last name, position, team abbreviation
    """
    espn_proj_2022 = []
    espn_proj_2022_dict = {}
    with open('Fantasy Football 2022.csv', 'r', encoding='utf-8-sig', newline='') as espn_proj_2022_file:
        reader = csv.DictReader(espn_proj_2022_file)
        for row in reader:
            espn_proj_2022.append(row)
    for player in espn_proj_2022:
        espn_proj_2022_dict[player['PLAYER'].split(" ")[1].casefold()
                            + player['Position'].casefold()
                            + player['Team'].casefold()] = player
    for player in espn_proj_2022_dict:
        type_convert = espn_proj_2022_dict[player]['FFP_TOTAL']
        type_convert = float(type_convert)
        espn_proj_2022_dict[player]['FFP_TOTAL'] = type_convert
    return espn_proj_2022_dict


def get_nfl_player_contracts():
    """
    Web-scrapes nfl player contract data from overthecap.com and returns a dictionary with
    the key of a unique id based on player's last name, position, and team
    Returns
    -------
    player_salary_information_dict: dict
        dictionary of player salary information
    """
    player_salary_information = []
    player_salary_information_dict = {}
    nfl_contract_url = 'https://overthecap.com/contracts'
    response = requests.get(nfl_contract_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    player_contracts = soup.find('table', class_="sortable controls-table")
    for x in player_contracts.find_all('td'):
        player_salary_information.append(x.string)
    player_salary_list = grouper(player_salary_information, 8, None)
    for player in player_salary_list:
        player_salary_information_dict[player[0].split(" ")[1].casefold()
                                       + player[1].casefold()
                                       + TEAM_NAMES[player[2]].casefold()] = {
            'Name': player[0],
            'Position': player[1],
            'Team': TEAM_NAMES[player[2]],
            'Total Value': player[3],
            'APY': player[4],
            'Total Guaranteed': player[5],
            'AVG Annual Guarantee': player[6],
            'Percent Guaranteed': player[7]
        }
    return player_salary_information_dict


def open_cache():
    """
    the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary

    Returns
    -------
    The opened cache
    """
    try:
        cache_file = open('Player_Cached_Data.json', 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    """ saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    """
    dumped_json_cache = json.dumps(cache_dict)
    fw = open('Player_Cached_Data.json', "w")
    fw.write(dumped_json_cache)
    fw.close()


def player_data_blend():
    """
    This function calls all the data request functions and creates a dictionary of espn projection
    records with augmented data from the other data sources to be used to create the player objects

    Returns
    -------
    dictionary of top 300 players with augmented data from all data sources
    """
    espn_proj_data = open_cache()
    if espn_proj_data == {}:
        espn_proj_data = get_espn_player_projections()
        player_salary_data = get_nfl_player_contracts()
        player_season_data = get_player_season_stats()
        sportio_proj_data = get_sportio_player_proj()

        for player in espn_proj_data:
            if player in player_salary_data:
                espn_proj_data[player]['Total_Salary'] = player_salary_data[player]['Total Value']
                espn_proj_data[player]['Annual_Salary'] = player_salary_data[player]['APY']
                espn_proj_data[player]['Percent_Guaranteed'] = player_salary_data[player]['Percent Guaranteed']
            else:
                espn_proj_data[player]['Total_Salary'] = '0'
                espn_proj_data[player]['Annual_Salary'] = '0'
                espn_proj_data[player]['Percent_Guaranteed'] = '0'
            if player in player_season_data:
                espn_proj_data[player]['Games Played'] = player_season_data[player]['Played']
                espn_proj_data[player]['Historic Fantasy Points'] = [player_season_data[player]['FantasyPointsFanDuel'],
                                                                     player_season_data[player]['FantasyPointsDraftKings'],
                                                                     player_season_data[player]['FantasyPointsYahoo'],
                                                                     player_season_data[player]['FantasyPointsFantasyDraft'],
                                                                     player_season_data[player]['FantasyPointsPPR']]
            else:
                espn_proj_data[player]['Games Played'] = 0
                espn_proj_data[player]['Historic Fantasy Points'] = 0
            if player in sportio_proj_data:
                espn_proj_data[player]['Fantasy Projections'] = [espn_proj_data[player]['FFP_TOTAL'],
                                                                 sportio_proj_data[player]['FantasyPointsFanDuel'],
                                                                 sportio_proj_data[player]['FantasyPointsDraftKings'],
                                                                 sportio_proj_data[player]['FantasyPointsYahoo'],
                                                                 sportio_proj_data[player]['FantasyPointsFantasyDraft'],
                                                                 sportio_proj_data[player]['FantasyPointsPPR']]

        save_cache(espn_proj_data)
        return espn_proj_data
    else:
        return espn_proj_data







