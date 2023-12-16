from recipe_scrapers import scrape_me
from rich.console import Console
import argparse
import yaml
import os
import platformdirs

console = Console()

try:
    with open("config.yaml", "r") as file:
        settings = yaml.safe_load(file)
except:
    print("A config.yaml file has been created in ~/.config/pure-recipe.")
    print("Please add a path to the config file to save your recipes.")
    print("No directory needed if viewing recipes in the terminal.")
    quit()


def format_file_name(recipe_title):
    """
    Converts the recipe title to a nice format.

    :param recipe_title: a string containing a recipe title.
    :return: formatted title
    :rtype: string
    """
    s = list(recipe_title.lower())

    for i, char in enumerate(s):
        if char.isspace():
            s[i] = "-"
    return "".join(s)


def save_to_markdown(recipe_url):
    """
    Scrapes recipe URL and saves to markdown file.

    :param url: a url string from a recipe website
    :return: True if successful, False otherwise.
    """
    load_config()

    scraper = scrape_me(recipe_url)
    directory = settings.get("directory")
    if not os.path.exists(directory):
        os.makedirs(directory, mode="0o777")
    title = scraper.title()
    recipe_file = directory + format_file_name(title) + ".md"

    with open(recipe_file, "w+") as text_file:
        print(f"# {title}", file=text_file)
        print(f"**Serves:** {scraper.yields()}", file=text_file)
        print(f"**Total Time:** {scraper.total_time()} mins", file=text_file)
        print(f"\n## Ingredients", file=text_file)
        for ingredient in scraper.ingredients():
            print(f"-", ingredient, file=text_file)
        print(f"\n## Instructions", file=text_file)
        for index, instruction in enumerate(scraper.instructions_list()):
            print(f"{index+1}.", instruction, file=text_file)

    return True


def view_in_terminal(recipe_url):
    """
    Scrapes recipe url and returns plain-text recipe to terminal output.

    :param url: a url string from a recipe website
    :return: True if successful, False otherwise.
    """
    scraper = scrape_me(recipe_url)

    console.print("\n\n", scraper.title(), style="bold white", justify="center")

    console.print("\nINGREDIENTS", style="bold white")
    for index, ingredient in enumerate(scraper.ingredients()):
        console.print("-", ingredient, style="gold3")

    console.print("\nINSTRUCTIONS", style="bold white")
    for index, instruction in enumerate(scraper.instructions_list()):
        console.print(index + 1, ") ", style="white", sep="", end="", highlight=False)
        console.print(instruction, style="gold3")

    return True


def load_config():
    """
    Loads the config settings for saving recipe files.
    """
    config_path = platformdirs.user_config_path(appname="pure-recipe")

    try:
        os.chdir(config_path)
    except:
        os.mkdir(config_path)
        os.chdir(config_path)

    directory = settings.get("directory")

    if directory == "":
        print("Please add a path to the config file to save your recipes.")
        print("Then, try again.")
        quit()


def main():
    parser = argparse.ArgumentParser(
        prog="Pure Recipe", description="Make recipes pretty again."
    )

    parser.add_argument("operations", choices=["view", "save"])
    parser.add_argument("url")

    args = parser.parse_args()
    url = args.url

    if args.operations == "view":
        view_in_terminal(url)

    if args.operations == "save":
        save_to_markdown(url)


main()