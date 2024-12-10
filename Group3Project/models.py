import mariadb
from geopy import distance
from random import choice

connection = mariadb.connect(
        user="eyobtalew",
        password="",
        host="127.0.0.1",
        port=3306,
        database="project",
        autocommit=True
    )
cursor = connection.cursor()

class Player:
    """An object to store the information of the player"""
    def __init__(self, player_id):
        self.id = player_id

        name = query_player_data(self.id, "player_name")
        current_funds = query_player_data(self.id, "current_funds")
        current_airport = query_player_data(self.id, "current_airport")
        coordinates = query_airport_coordinates(current_airport)
        time_left = query_player_data(self.id, "time_left")

        self.info = {
            "id": self.id,
            "name": name,
            "current_funds": current_funds,
            "current_airport": current_airport,
            "coordinates": coordinates,
            "time_left": time_left,
        }


def query_player_id(username, password):
    """Query the play's ID by username and password provided by the player after successfully login"""
    sql = f"""
        SELECT player_id
        FROM game
        WHERE game.player_name="{username}" AND game.player_password="{password}";
    """
    cursor.execute(sql)
    response = cursor.fetchone()
    if response:
        player_id = response[0]
    else:
        player_id = response
    return player_id

def query_player_data(player_id, column_name):
    """Query the specific data of a player according to the player's id and specific column name"""
    sql = f"""
        SELECT {column_name} 
        FROM game
        WHERE game.player_id="{player_id}";
    """
    cursor.execute(sql)
    response = cursor.fetchone()
    data = response[0]
    return data

def is_username_registered(username):
    """Check if a username is registered in the database"""
    sql = f"""
        SELECT player_id
        FROM game
        WHERE player_name="{username}";
    """
    cursor.execute(sql)
    response = cursor.fetchone()
    if response:
        return True
    else:
        return False 
    
def register_player(username, password):
    """Insert the new player's data into the game table"""
    initial_airport = generate_random_airport()
    sql = f"""
        INSERT INTO game
        VALUES (DEFAULT, "{username}", "{password}", DEFAULT, "{initial_airport}", DEFAULT);
    """
    cursor.execute(sql)

def generate_random_airport():
    """Generate a random airpot as the initially spawned place for a new player"""
    airport_idents = query_all_airport_idents()
    airport = choice(airport_idents)
    return airport

def query_airport_coordinates(ident):
    """Query the airport table about the coordiantes of an airport by its ident"""
    sql = f"""
        SELECT latitude_deg, longitude_deg
        FROM airport
        WHERE ident="{ident}";
    """
    cursor.execute(sql)
    coordinates = cursor.fetchone()
    return coordinates

def query_airport_name(ident):
    """Query the airport table about the name of an airport by its ident"""
    sql = f"""
        SELECT name
        FROM airport
        WHERE ident="{ident}";
    """
    cursor.execute(sql)
    name = cursor.fetchone()[0]
    return name

def query_all_airport_idents():
    """Query all airports ident from table airport"""
    sql = f"""
        SELECT ident 
        FROM airport;
    """
    cursor.execute(sql)
    response = cursor.fetchall()
    airpot_idents = []
    for item in response:
        airpot_idents.append(item[0])
    return airpot_idents

def get_all_airports_info(current_airport_ident):
    airports = []
    current_airport_coordinates = query_airport_coordinates(current_airport_ident)
    airports_idents = query_all_airport_idents()
    for ident in airports_idents:
        airport_info = {}
        airport_info["ident"] = ident
        airport_info["name"] = query_airport_name(ident)
        airport_info["coordinates"] = query_airport_coordinates(ident)
        airport_info["travel_time"] = get_travel_time(current_airport_ident, ident)
        airports.append(airport_info)
    return airports

def get_distance(ident1, ident2):
    """Return the distance between two airports by idents"""
    coordinates1 = query_airport_coordinates(ident1)
    coordinates2 = query_airport_coordinates(ident2)
    return distance.distance(coordinates1, coordinates2).km

def get_travel_time(ident1, ident2):
    """Return the travel time of two airports by idents"""
    distance = get_distance(ident1, ident2)
    travel_time = distance / 500

    return float(f"{travel_time:.1f}")
    
def update_player_time_left(player_id, time_left):
    """Update the player's time left"""
    sql = f"""
        UPDATE game
        SET time_left={time_left}
        WHERE player_id={player_id};
    """
    cursor.execute(sql)

def update_player_current_airport(player_id, current_airport):
    """Update the player's current airport"""
    sql = f"""
        UPDATE game
        SET current_airport="{current_airport}"
        WHERE player_id={player_id};
    """
    cursor.execute(sql)

def query_goods_info(ident):
    """Query all goods info of a store by its ident"""
    goods = []

    sql = f"""
        SELECT gida.goods_id, g.name, gida.buy_price, gida.sell_price, gida.stock
        FROM goods_in_different_airport as gida, goods as g
        WHERE gida.airport_ident="{ident}" 
        AND gida.goods_id=g.id;
    """
    cursor.execute(sql)
    result = cursor.fetchall()

    for good in result:
        goods_info = {}
        goods_info["goods_id"] = good[0]
        goods_info["name"] = good[1]
        goods_info["buy_price"] = good[2]
        goods_info["sell_price"] = good[3]
        goods_info["stock"] = good[4]
        goods.append(goods_info)

    return goods

def query_player_inventory(player_id, current_airport_ident):
    """Query the player's inventory"""
    inventory = []

    sql = f"""
        SELECT pi.goods_id, pi.quantity, gida.sell_price   
        FROM player_inventory as pi, goods_in_different_airport as gida
        WHERE pi.player_id={player_id}
        AND gida.airport_ident="{current_airport_ident}"
        AND pi.goods_id=gida.goods_id;
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    
    for good in result:
        goods_info = {}
        goods_info["goods_id"] = good[0]
        goods_info["quantity"] = good[1]
        goods_info["sell_price"] = good[2]
        inventory.append(goods_info)

    return inventory

if __name__ == "__main__":
    print(query_goods_info("KMIA"))