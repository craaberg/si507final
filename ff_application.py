from flask import Flask, render_template, request
from ff_datamgmt import player_data_blend as get_data, TEAM_NAMES
import ff_objects as obj

app = Flask(__name__)

headings = ("Name", "Position", "Team", "Last Year's Points", "Projected Points",
            "Projected Points Deviation", "Games Played Last Year", "Player Contract",
            "Percent Guaranteed")


def fill_tree(tree, json):
    """
    Takes a BST data structure and json payload and iterates through the json data,
    converting it into PlayerNode objects and thenpopulates the BST in with the json data.
    Parameters
    ----------
    tree: BST
        empty binary tree data structure
    json: json
        json payload containing nfl fantasy football data
    Returns
    -------
    tree: BST
        binary tree data structure that is fill with PlayerNode objects based on their player_uuid
    """
    for player in json:
        cur_elem = obj.PlayerNode(player_uuid=player, json=json[player])
        tree.insert(cur_elem)
    return tree


def list_players(json):
    """
    takes in json data and converts it into a list of PlayerNode objects
    Parameters
    ----------
    json: json
        json data of nfl player information containing fantasy football data

    Returns
    -------
    player_list: list
        list of PlayerNode objects
    """
    player_list = []
    for player in json:
        player_list.append(obj.PlayerNode(player_uuid=player, json=json[player]))
    return player_list


def get_risky_players(player_list):
    """
    takes in a lit of PlayerNode objects and filters out PlayerNode objects where players
     played more than 12 games or their projected standard deviation is less than 40
    Parameters
    ----------
    player_list: list
        a list of PlayerNode objects

    Returns
    -------
    player_list: list
        list of PlayerNode objects
    """
    risky_list = []
    for player in player_list:
        if player.games_played < 12 or player.st_dev_proj > 40:
            risky_list.append(player)
    risky_list.sort(key=lambda x: x.proj_ffp, reverse=True)
    return risky_list


@app.route('/')
def homepage():
    return render_template("ff_home.html", headings=headings, data=list_of_players)

@app.route('/risky')
def risky():
    return render_template("ff_risky_players.html", headings=headings, data=risky_players)

@app.route('/salary')
def salary():
    return render_template("ff_salary.html", headings=headings, data=player_data_sorted_salary)

@app.route('/search')
def search():
    return render_template("ff_search.html", headings=headings, team_names=TEAM_NAMES)

@app.route('/handle_search', methods=['POST'])
def handle_search():
    player_last_name = str(request.form['name']).casefold()
    player_pos = str(request.form['pos']).casefold()
    player_team = str(request.form['team']).casefold()
    player_id = player_last_name + player_pos + player_team
    print(player_id)
    search_results = player_tree.search(player_id)
    if search_results is False:
        return "Player not found, please check spelling or search for a different player <a href='/search'>here</a>"
    return render_template("ff_search_results.html", headings=headings, player_info=search_results)


if __name__ == "__main__":
    player_tree = obj.BinarySearchTree()
    player_data = get_data()
    player_tree = fill_tree(player_tree, player_data)
    list_of_players = list_players(player_data)
    player_data_sorted_salary = sorted(list_of_players, key=lambda x: x.contract_value, reverse=True)
    risky_players = get_risky_players(list_of_players)
    app.run(debug=True)