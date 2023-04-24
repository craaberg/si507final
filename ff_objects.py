import numpy as np
import re
trim = re.compile(r'[^0-9.]')


class PlayerNode:
    """
    class PlayerNode represents an nfl football player and contains all relevant fantasy football data about that
    player's performance and projected performance for the upcoming football season. Also contains the player's contract
    information.

    Parameters
    ----------
    player_uuid: str
        unique id that is a combination of lastname, player's position, and player's team
    name: str
        player's first and last name
    pos: str
        abbreviation of the player's position. It is either QB, WR, RB, TE, K, or D/ST
    team: str
        abbreviation of the name the player plays on
    ly_ffp: float
        the total fantasy football points the player acquired last year
    proj_ffp: float
        the total fantasy football points the player is projected to get this year
    games_played: int
        number of games the player played last year
    contract_value: float
        the total value of the player's contract
    contract_value_str: str
        A formatted string of the total value of the player's contract used for presentation
    percent_guaranteed: float
        The percent of the total contract that is guaranteed money for the player
    percent_guaranteed_str: str
        A formatted string of the percent guaranteed of the player's contract used for presentation
    st_dev_proj: float
        The standard deviation of the projected fantasy football points the player will get this football season
    Methods
    -------
    get_player_data()
        Returns a list of selected values from the player object that is used for populating the data tables
    """
    def __init__(self, player_uuid='', name='name missing', pos='position missing', team='team missing', ly_ffp=0,
                 proj_ffp=0, games_played=0, contract_value=0, contract_value_str='', percent_guaranteed=0,
                 percent_guaranteed_str='', st_dev_proj=0, json=None):
        self.left_child = None
        self.right_child = None
        if json is None:
            print('No json')
            self.player_uuid = player_uuid
            self.name = name
            self.pos = pos
            self.team = team
            self.ly_ffp = ly_ffp
            self.proj_ffp = proj_ffp
            self.games_played = games_played
            self.contract_value = contract_value
            self.contract_value_str = contract_value_str
            self.percent_guaranteed = percent_guaranteed
            self.percent_guaranteed_str = percent_guaranteed_str
            self.st_dev_proj = st_dev_proj
        else:
            self.player_uuid = player_uuid
            self.name = json['PLAYER']
            self.pos = json['Position']
            self.team = json['Team']
            if 'Historic Fantasy Points' not in json:
                self.ly_ffp = ly_ffp
            else:
                self.ly_ffp = round(np.mean(json['Historic Fantasy Points']), 2)
            if 'Games Played' not in json:
                self.games_played = games_played
            else:
                self.games_played = json['Games Played']
            if 'Fantasy Projections' not in json:
                self.proj_ffp = float(json['FFP_TOTAL'])
                self.st_dev_proj = st_dev_proj
            else:
                self.proj_ffp = round(np.mean(json['Fantasy Projections']), 2)
                self.st_dev_proj = round(np.std(json['Fantasy Projections']), 2)
            if 'Total_Salary' not in json:
                self.contract_value = contract_value
                self.contract_value_str = contract_value_str
                self.percent_guaranteed = percent_guaranteed
                self.percent_guaranteed_str = percent_guaranteed_str
            else:
                self.contract_value = float(trim.sub('', json['Total_Salary']))
                self.contract_value_str = json['Total_Salary']
                self.percent_guaranteed = float(trim.sub('', json['Percent_Guaranteed']))
                self.percent_guaranteed_str = json['Percent_Guaranteed']


    def get_player_data(self):
        return [self.player_uuid, self.name, self.pos, self.team, self.ly_ffp, self.proj_ffp, self.st_dev_proj,
                self.games_played, self.contract_value_str, self.percent_guaranteed_str]


class BinarySearchTree:
    """
    class BinarySearchTree is a BST data structure that is built out based on the player_uuid to enable the search
    functionality of the application
    Parameters
    ----------
    root: obj
        this represents the root node of the BST data structure
    Methods
    -------
    insert(value)
        accessible method used to insert PlayerNode objects into the BST.
         Takes a PlayerNode object from the BST in as an input
    _insert(value, cur_node)
        hidden method used to insert PlayerNode objects into the BST.
         Takes two PlayerNode objects from the BST in as input
    print_tree()
        accessible method that prints out all the nodes in the tree
    _print_tree(cur_node)
        accessible method that prints out all the nodes in the tree.
         Takes a PlayerNode object from the BST in as input
    height()
        accessible method that returns how many levels there are in the BST data structure
    _height(cur_node, cur_height)
        inaccessible method that returns how many levels there are in the BST data structure.
         Takes two PlayerNode objects from the BST in as input
    search(value)
        accessible method used to take user input and returns the player data in the BST that the user inputted
    _search(value)
        inaccessible method used to take user input and returns the player data in the BST that the user inputted
        Takes two PlayerNode objects from the BST in as input
    """
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = value
        else:
            self._insert(value, self.root)

    def _insert(self, value, cur_node):
        if value.player_uuid < cur_node.player_uuid:
            if cur_node.left_child is None:
                cur_node.left_child = value
            else:
                self._insert(value, cur_node.left_child)
        elif value.player_uuid > cur_node.player_uuid:
            if cur_node.right_child is None:
                cur_node.right_child = value
            else:
                self._insert(value, cur_node.right_child)
        else:
            print("Value already in tree!")

    def print_tree(self):
        if self.root is not None:
            self._print_tree(self.root)

    def _print_tree(self, cur_node):
        if cur_node is not None:
            self._print_tree(cur_node.left_child)
            print(str(cur_node.player_uuid))
            self._print_tree(cur_node.right_child)

    def height(self):
        if self.root is not None:
            return self._height(self.root, 0)
        else:
            return 0

    def _height(self, cur_node, cur_height):
        if cur_node is None:
            return cur_height
        left_height = self._height(cur_node.left_child, cur_height + 1)
        right_height = self._height(cur_node.right_child, cur_height + 1)
        return max(left_height, right_height)

    def search(self, value):
        if self.root is not None:
            return self._search(value, self.root)
        else:
            return self.value

    def _search(self, value, cur_node):
        if value == cur_node.player_uuid:
            return cur_node.get_player_data()
        elif value < cur_node.player_uuid and cur_node.left_child is not None:
            return self._search(value, cur_node.left_child)
        elif value > cur_node.player_uuid and cur_node.right_child is not None:
            return self._search(value, cur_node.right_child)
        return False


