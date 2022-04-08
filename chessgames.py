
import os
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def check_directory():
    if not os.path.exists("ChessGames Collections"):
        os.mkdir("ChessGames Collections")

def check_file(filename):
    # Entramos a la carpeta de la coleccion
    os.chdir("ChessGames Collections")

    # Comprobamos si existe el fichero
    if os.path.isfile(filename):
        # borramos el fichero
        os.remove(filename)
    
    # Volvemos a la carpeta de la aplicacion
    os.chdir("..")

def download_games(page_title, game_id_list):
    check_directory()

    filename = "ChessGames Collections/" + page_title.replace(" ", "_") + ".pgn"

    print("\nDownloading games from {}".format(page_title))

    # Comprobamos si existe el fichero
    check_file(filename)

    # Abrimos el fichero
    with open(filename, "w") as f:
        current_percentage = 0
        position = 0

        for game_id in game_id_list:
            url_game = "https://www.chessgames.com/perl/nph-chesspgn?text=1&gid=" + str(game_id)
            response = requests.get(url_game, headers=headers)
            pgn = response.text.replace('\\"', '').replace('\r', ' ')

            f.write(pgn)
            f.write("\n\n\n\n")

            position += 1
            new_percentage = int(position * 100 / len(game_id_list))

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

    game_ids = [a_tag.attrs['href'].split("=")[-1] for a_tag in a_tags]

    page_title = soup.title.text

    download_games(page_title, game_ids)

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
        url_page = f"https://www.chessgames.com/perl/chess.pl?page={page}&pid={player_id}"
        response = requests.get(url_page, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        a_tags = soup.select('a[href^="/perl/chessgame?gid="]')

        game_ids += [a_tag.attrs['href'].split("=")[-1] for a_tag in a_tags]

    download_games(page_title, game_ids)




def main_menu():
    print("""
    --------------------------------------
    1. Download Collection of Chess Games
    2. Download Games from Player
    3. Exit
    --------------------------------------
    """)

    # Wait for user input
    choice = input("Enter your choice: ")

    # Validate user input
    while choice not in ["1", "2", "3"]:
        choice = input("Invalid choice. Enter your choice: ")

    if choice == "1":
        option1_menu()
    elif choice == "2":
        option2_menu()
    elif choice == "3":
        exit()


if __name__ == "__main__":
    main_menu()
