import json

# Odczyt danych gracza z pliku
with open("C:/Users/matqk/Documents/testy do vps/game_data.json", "r") as file:
    game_data = json.load(file)

print(game_data)

characters = game_data["characters"]
items = game_data["items"]
skills = game_data["skills"]

def display_character(character_name):
    if character_name in characters:
        char = characters[character_name]
        print(f"Postać: {char['name']}")
        print(f"Poziom: {char['level']}")
        print(f"Zdrowie: {char['health']}")
        print("Statystyki:")
        for stat, value in char["stats"].items():
            print(f"  {stat}: {value}")
        print("Ekwipunek:")
        for item in char["inventory"]:
            print(f"  - {item}")
        print("Umiejętności:")
        for skill in char["skills"]:
            print(f"  - {skill}")
    else:
        print("Nie znaleziono takiej postaci.")

# Przykład wyświetlenia
display_character("hero")


with open("game_data.json", "w") as file:
    json.dump(game_data, file, indent=4, ensure_ascii=False)