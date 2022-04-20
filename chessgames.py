import os
import re

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def check_file(folder_name, filename):
    # Entramos a la carpeta de la coleccion
    os.chdir(folder_name)

    # Comprobamos si existe el fichero
    if os.path.isfile(filename):
        # borramos el fichero
        os.remove(filename)

    # Volvemos a la carpeta de la aplicacion
    os.chdir("..")


def download_games_chessgames(page_title, game_id_list):
    folder_name = "ChessGames Collections"
    check_folder(folder_name)

    filename = folder_name + "/" + page_title.replace(" ", "_") + ".pgn"

    print("\nDownloading games from {}".format(page_title))

    # Comprobamos si existe el fichero
    check_file(folder_name, filename)

    # Abrimos el fichero
    with open(filename, "w", encoding="utf-8") as f:
        current_percentage = 0
        position = 0

        for game_id in game_id_list:
            url_game = "https://www.chessgames.com/perl/nph-chesspgn?text=1&gid=" + str(
                game_id
            )
            response = requests.get(url_game, headers=headers)
            pgn = response.text.replace('\\"', "").replace("\r", " ")

            f.write(pgn)
            f.write("\n\n\n\n")

            position += 1
            new_percentage = int(position * 100 / len(game_id_list))

            if new_percentage > current_percentage:
                print("{}%".format(new_percentage))
                current_percentage = new_percentage

    print("\nGames downloaded successfully")


def download_games_chesscom(page_title, game_id_list):
    folder_name = "ChessCom Games"
    check_folder(folder_name)

    filename = folder_name + "/" + page_title.replace(" ", "_") + ".pgn"

    print("\nDownloading games from {}".format(page_title))

    # Comprobamos si existe el fichero
    check_file(folder_name, filename)

    # Dividimos la lista de Ids en grupos de 25
    game_id_list_divided = [
        game_id_list[i : i + 25] for i in range(0, len(game_id_list), 25)
    ]

    # Abrimos el fichero
    with open(filename, "w", encoding="utf-8") as f:
        current_percentage = 0
        position = 0

        for game_id_group in game_id_list_divided:
            url_download = (
                "https://www.chess.com/games/downloadPgn?game_ids="
                + ",".join(str(game_id) for game_id in game_id_group)
            )

            response = requests.get(url_download, headers=headers)
            # pgn = response.text.replace('\\"', "").replace("\r", " ")
            pgn = response.text.replace('\\"', "").replace("\r", "")

            pgn_list = pgn.split("\n\n\n")
            pgn_list = [pgn_unit.rstrip() for pgn_unit in pgn_list]

            pgn = "\n\n\n\n".join(pgn_list)

            f.write(pgn)
            f.write("\n\n\n\n")

            position += 1
            new_percentage = int(position * 100 / len(game_id_list_divided))

            if new_percentage > current_percentage:
                print("{}%".format(new_percentage))
                current_percentage = new_percentage

    print("\nGames downloaded successfully")


def option1_menu():
    url = input("\nEnter the URL of the chess games collection: ")

    # Validate user input
    while not url.startswith("https://www.chessgames.com"):
        url = input("Invalid URL. Enter the URL of the chess games collection: ")

    # Get the HTML of the chess games collection
    response = requests.get(url, headers=headers)
    print(response.status_code)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # search all "a" that contain href with text "/perl/chessgame?gid="
    # and extract the gid
    a_tags = soup.select('a[href^="/perl/chessgame?gid="]')

    game_ids = [a_tag.attrs["href"].split("=")[-1] for a_tag in a_tags]

    page_title = soup.title.text

    download_games_chessgames(page_title, game_ids)

    # Return to main menu
    main_menu()


def option2_menu():
    url = input("\nEnter the Url of the player: ")

    # Validate user input
    while not url.startswith("https://www.chessgames.com"):
        url = input("Invalid URL. Enter the Url of the player: ")

    player_id = url.split("=")[-1]

    # Get the HTML of the player
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    page_title = soup.title.text

    target_tag = soup.select('td[background="/chessimages/table_stripes.gif"]')
    pages_string = target_tag[0].text.strip()
    total_games = int(pages_string.split(" ")[-1].replace(",", ""))
    total_pages = int(pages_string.split(";")[0].split(" ")[-1])

    print("\nTotal games: {}".format(total_games))
    print("Total pages: {}".format(total_pages))

    game_ids = []

    for page in range(1, total_pages + 1):
        url_page = (
            f"https://www.chessgames.com/perl/chess.pl?page={page}&pid={player_id}"
        )
        response = requests.get(url_page, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        a_tags = soup.select('a[href^="/perl/chessgame?gid="]')

        game_ids += [a_tag.attrs["href"].split("=")[-1] for a_tag in a_tags]

    download_games_chessgames(page_title, game_ids)

    # Return to main menu
    main_menu()


def option3_menu():
    url = input("\nEnter the Url of the player: ")

    # Validate user input
    while not url.startswith("https://www.chess.com/players/"):
        url = input(
            "Invalid URL. Example: https://www.chess.com/players/mikhail-tal\nEnter the Url of the player: "
        )

    # Get the HTML of the player
    response = requests.get(url, headers=headers)

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # El botón que nos dirigirá a la página de las partidas del jugador
    tag_games = soup.find("a", string=re.compile("Show All Games"))

    # Nos redirigimos a la nueva página
    url_games = tag_games.attrs["href"]
    response = requests.get(url_games, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Título de la página
    page_title = soup.title.text

    # Buscamos el nav con la clase "ui_pagination-navigation"
    nav_tag = soup.find("nav", class_="ui_pagination-navigation")

    # Obtenemos la página 2
    tag_page2 = nav_tag.select_one('a[href$="&page=2"]')

    url_page2 = tag_page2.attrs["href"]

    page_base = url_page2[:-1]

    print("\nEtapa 1: Almacenar las IDs de todas las partidas\n")

    game_id_list = []
    index = 1

    while True:
        url_page = page_base + str(index)
        response = requests.get(url_page, headers=headers)

        if (
            "Your search did not match any games. Please try a new search."
            in response.text
        ):
            print("\nSe almacenaron todas las IDs de las partidas")
            break

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Buscamos el div con id "master-games-container"
        div_tag = soup.find("div", id="master-games-container")

        # Buscamos los "a" que contengan href con texto "https://www.chess.com/games/view/"
        a_tags = div_tag.find_all(
            "a", href=re.compile("https://www.chess.com/games/view/")
        )

        # Almacenamos las IDs de las partidas
        local_id_list = [a_tag.attrs["href"].split("/")[-1] for a_tag in a_tags]
        local_id_list = list(set(local_id_list))

        game_id_list += local_id_list

        print("Se obtuvieron {} IDs de partidas".format(len(game_id_list)))

        index += 1

    if len(game_id_list) == 0:
        print("\nNo se encontraron partidas")
    else:
        print("\nEtapa 2: Descargar las partidas\n")

        download_games_chesscom(page_title, game_id_list)

    # Return to main menu
    main_menu()


def main_menu():
    print(
        """
    --------------------------------------
    1. Download Collection of Chess Games (chessgames.com)
    2. Download Games from Player (chessgames.com)
    3. Download Games from Player (chess.com)
    4. Exit
    --------------------------------------
    """
    )

    # Wait for user input
    choice = input("Enter your choice: ")

    # Validate user input
    while choice not in ["1", "2", "3", "4"]:
        choice = input("Invalid choice. Enter your choice: ")

    if choice == "1":
        option1_menu()
    elif choice == "2":
        option2_menu()
    elif choice == "3":
        option3_menu()
    elif choice == "4":
        exit()


if __name__ == "__main__":
    main_menu()
