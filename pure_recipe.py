from recipe_scrapers import scrape_me
from rich.console import Console
from rich.markdown import Markdown
import argparse
import yaml
import os
import platformdirs

console = Console()


def main():
    settings = {
        "yield": True,
        "time": True
    }

    args = parse_arguments()
    url = args.url

    try: 
        if args.operations == "view":
            view_recipe(args.url, settings)
        elif args.operations == "save":
            save_recipe_to_markdown(args.url, settings)
        elif args.operations == "list":
            save_list_of_recipes(args.url, settings)
        elif args.operations == "browse":
            browse_recipes()
        else: 
            console.print("Invlaid operation. See documentation.", style="bright_red")
    except Exception as e:
        console.print(f"\nAn error occured: {str(e)}", style="bright_red bold")


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


def save_recipe_to_markdown(recipe_url, yaml_settings):
    """
    Scrapes recipe URL and saves to markdown file.

    :param url: a url string from a recipe website

    :rtype: string
    :return: path to file
    """
    try:
        scraper = scrape_me(recipe_url, wild_mode=True)
    except Exception as e:
        console.print(f"\nCould not scrape recipe, error: {str(e)}", style="bright_cyan bold")

    title = scraper.title().replace(" ", "-")
    recipe_file = "out/" + format_file_name(title) + ".md"

    console.print(scraper)

    with open(recipe_file, "w+") as text_file:
        print(f"# {title}", file=text_file)

        print(f"**Serves:** {scraper.yields()}\n", file=text_file)
        print(f"**Total Time:** {scraper.total_time()} mins\n", file=text_file)
        print(f"**Source URL:** {recipe_url}\n", file=text_file)

        print("\n\n----\n\n", file=text_file)

        try:
            print(f"**host:** {scraper.host()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing host to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**title:** {scraper.title()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing title to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**total_time:** {scraper.total_time()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing total_time to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**yields:** {scraper.yields()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing yields to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**nutrients:** {scraper.nutrients()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing nutrients to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**canonical_url:** {scraper.canonical_url()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing canonical_url to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**equipment:** {scraper.equipment()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing equipment to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**cooking_method:** {scraper.cooking_method()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing cooking_method to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**keywords:** {scraper.keywords()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing keywords to file: {str(e)}", style="bright_green bold")

        try:
            print(f"**dietary_restrictions:** {scraper.dietary_restrictions()}\n", file=text_file)
        except Exception as e:
            console.print(f"    Error writing dietary_restrictions to file: {str(e)}", style="bright_green bold")


        print("\n\n----\n\n", file=text_file)
        
        print(f"\n## Ingredients", file=text_file)

        for ingredient in scraper.ingredients():
            print(f"-", ingredient, file=text_file)

        print(f"\n## Instructions", file=text_file)

        for index, instruction in enumerate(scraper.instructions_list()):
            print(f"{index+1}.", instruction, file=text_file)

    return recipe_file


def print_markdown(md):
    console.print("\n")
    console.print(md)
    console.print("\n")
    return True


def view_recipe(recipe_url, yaml_settings):
    """
    Scrapes recipe url and returns markdown-formatted recipe to terminal output.


    :param url: a url string from a recipe website
    :rtype: bool
    :return: True if successful, False otherwise.
    """
    # try:
    file_path = save_recipe_to_markdown(recipe_url, yaml_settings)
    f = open(file_path, "r")
    md = Markdown(f.read())
    f.close()
    print_markdown(md)
    # except:
        # console.print("\nError in view_recipe function.\n", style="bright_red")
        # return False

    return True


def save_list_of_recipes(url, settings):
    # os.chdir(settings["directory"])
    f = open(url, "r")
    for line in f:
        try:
            single_url = line.strip().rstrip("\n")
            save_recipe_to_markdown(single_url, settings)
        except:
            console.print(
                "\nFile error. Try again using proper file format. See documentation.\n",
                style="bright_red",
            )


def browse_recipes():
    """
    Allow user to browse previously-saved recipes.
    User can choose 1 to view in terminal.
    """
    with open("config.yaml", "r") as file:
        settings = yaml.safe_load(file)

    directory = settings.get("directory")

    print(directory)

    files_to_paths = {}

    def print_titles(recipe_path):
        with open(recipe_path, "r") as f:
            title = f.readline().lstrip("#")
            console.print((index + 1), title, style="green")

    # Add files to file_to_paths dictionary
    # And print each filename for selection
    for index, file in enumerate(os.listdir(directory)):
        filename = os.fsdecode(file)
        file_path = directory + '/' + filename
        if filename.endswith(".md"):
            files_to_paths.update({filename: file_path})
            print_titles(file_path)

    def choose_recipe():
        file_path = ""

        inp = input("Enter a number to choose a recipe. Or, enter 'q' to quit.\n")

        if inp == "q":
            exit()

        try:
            choice = int(inp) - 1
            file_path = list(files_to_paths.values())[choice]
        except:
            console.print("\nInput error. Try again.\n", style="bright_red")
            choose_recipe()

        if file:
            f = open(file_path, "r")
            md = Markdown(f.read())
            print_markdown(md)

    choose_recipe()


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="Pure Recipe", description="Make recipes pretty again."
    )

    parser.add_argument("operations", choices=["view", "save", "list", "browse"])
    parser.add_argument("url", default="foo", nargs="?")

    return parser.parse_args()


if __name__ == "__main__":
    main()
