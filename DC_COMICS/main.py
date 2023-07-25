import json

import requests
from bs4 import BeautifulSoup

character_names = []
dc_comics_characters = []
picture_urls = {}
unique_character_names = []
dummy_character_info_dict = {}
character_info_dict = {}
dc_file_path = "dc_comics.json"
text_file = 'dc.txt'
count = 0

# URL FOR FIRST LINK
base_url = 'https://www.dc.com/characters?page={}'

for page_number in range(1, 14):
    url1 = base_url.format(page_number)
    response = requests.get(url1)

    if response.status_code == 200:
        html1_text = requests.get(url1).content
        soup1 = BeautifulSoup(html1_text, 'lxml')

        # Find all elements with the class "card-container"
        characters = soup1.find_all(class_="card-container")

        # Iterate over the elements
        for character in characters:
            character_name = character.find(class_='card-title').text.strip()

            if character_name.endswith('.'):
                character_name = character_name[:-1]
            if "." or ":" or "'" in character_name:
                character_name = character_name.replace('.', '-')
                character_name = character_name.replace(':', '')
                character_name = character_name.replace('\'', '')
            character_name = character_name.lower().replace(' ', '-')  # changing names to lower and hyphenating them

            if character_name not in character_names:
                character_names.append(character_name)
                if character_name == 'earth-6':
                    character_names.remove(character_name)
                picture_urls.update({character_name: character.find('img')['src']})
    # character_names = character_names[9:]  # REMOVING CHARACTERS NOT IN THE BOTTOM GRID
    # print(character_names)
    # GETTING UNIQUE CHARACTER NAMES IN THE LIST
    # for unique_name in character_names:
    #     if unique_name not in unique_character_names:
    #         unique_character_names.append(unique_name)

    char_string = '\n'.join(character_names)
    with open(text_file, 'w') as file:
        file.write(char_string)

    # GETTING CHARACTER STORY
    for unique_name in character_names:
        url2 = f'https://www.dc.com/characters/{unique_name}'
        html2_text = requests.get(url2).content
        soup2 = BeautifulSoup(html2_text, 'lxml')

        # GETTING THE DIV WITH CLASS= "sc-g8nqnn-0 hTEdPw" THE P TAGS
        h1_tag = soup2.find('h1', class_='text-left')

        about_character = []
        #
        if h1_tag:
            for tag in h1_tag.find_all_next():
                if tag.name == 'h2' and tag.get_text().strip().lower() == 'character facts':
                    break
                about_character.append(tag)

        # DELETING UNWANTED TAGS FROM CHARACTER'S ABOUT
        del about_character[0]
        # count += 1
        # print(f'0 of {count} deleted')

#         # GETTING FACTS ABOUT CHARACTER
#         # DELETING MULTIPLE 'CHARACTER FACTS'
        indices_to_delete = [i for i, elem in enumerate(about_character) if
                             elem.find("h2", class_="text-left") and elem.find("h2",
                                                                               class_="text-left").text == "Character Facts"]
        indices_to_delete.sort(reverse=True)
        for index in indices_to_delete:
            del about_character[index]

        # GETTING STRINGS OF TEXT FROM THE ARRAY
        story = ''
        for tag in about_character:
            story += tag.get_text().strip()

        # ADDING NAME,PHOTO AND STORY AS A KEYS TO THE LIST OF DC CHARACTERS
        dummy_character_info_dict.update({'name': unique_name, 'story': story, 'photo': picture_urls[unique_name]})

        # GETTING CHARACTER FACTS
        fact_values_dict = {}
        labels = soup2.find_all(class_="sc-b3fnpg-2 bAcwzp")
        for label in labels:
            fact = label.p.get_text().strip()
            values = list(
                map(str.strip, label.p.find_next('p').get_text(strip=True).split(',')))  # changing string to list
            # and removing whitespaces
            fact_values_dict[fact] = values

        dummy_character_info_dict.update({'facts': fact_values_dict})
        character_info_dict = dummy_character_info_dict.copy()

        dc_comics_characters.append(character_info_dict)


# SAVING DATA INTO A FILE
def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_data(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


existing_data = load_data(dc_file_path)

for character in dc_comics_characters:
    if character not in existing_data:
        existing_data.append(character)

save_data(existing_data, dc_file_path)

print("Data updated and saved to", dc_file_path)
