from recipe_scrapers import scrape_me
from recipe_scrapers._exceptions import SchemaOrgException
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

def save_recipe_to_markdown(recipe_url, yaml_settings):
    """
    Scrapes recipe URL and saves to markdown file.

    :param url: a url string from a recipe website

    :rtype: string
    :return: path to file
    """
    
    console.print(f"Beginning Recipe at url: {recipe_url}", style="bright_cyan bold")
    
    try:
        scraper = scrape_me(recipe_url, wild_mode=True)
    except Exception as e:
        console.print(f"    Could not scrape recipe, error: {str(e)}", style="bright_red")
        return None

    recipe_file = "out/" + scraper.title() + ".md"

    with open(recipe_file, "w+") as text_file:

        # Get variables for frontmatter

        output_url = ""
        try:
            scraper.canonical_url()
        except AttributeError:
            console.print("    No URL found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            output_url = scraper.canonical_url()

        output_keywords = ""
        try:
            scraper.keywords()
        except AttributeError:
            console.print("    No Keywords found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            output_keywords = scraper.keywords()

        output_total_time = ""
        try:
            scraper.total_time()
        except AttributeError:
            console.print("    No Total Time found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            output_total_time = scraper.total_time()

        output_servings = ""
        try:
            scraper.yields()
        except AttributeError:
            console.print("    No Yields found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            output_servings = scraper.yields()

        # Print yaml frontmatter
        print(f"---", file = text_file)
        print(f"type: recipe", file = text_file)
        print(f"url: {output_url}", file = text_file)
        print(f"tags: {output_keywords}", file = text_file)
        print(f"totalTime: {output_total_time}", file = text_file)
        print(f"activeTime: ", file = text_file)
        print(f"waitTime: ", file = text_file)
        print(f"servings: {output_servings}", file = text_file)
        print(f"spicy: ", file = text_file)
        print(f"status: tried", file = text_file)
        print(f"triedMultiples: ", file = text_file)
        print(f"danielleRating: ", file = text_file)
        print(f"johnRating: ", file = text_file)

        print(f"---", file = text_file)           

        # Print Equipment

        try:
            scraper.equipment()
        except NotImplementedError:
            console.print("    Equipment Attribute not implemented")
        except AttributeError:
            console.print("    No equipment found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            print(f"\n# Equipment", file = text_file)

            for equipment in scraper.equipment():
                print(f"- {equipment}", file = text_file)


        # Print Ingredients

        try:
            scraper.ingredient_groups()
        except AttributeError:
            console.print("    No Ingredients found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        except Exception as e:
            console.print(f"    Unknown Error in ingredient_groups: {e}")
        else:
            print(f"\n# Ingredients", file = text_file)
 
            for group in scraper.ingredient_groups():
                if len(scraper.ingredient_groups()) > 1:
                    print(f"\n## {group}", file = text_file)
                
                grouped_ingredients = []
                grouped_ingredients.extend(group.ingredients)
                for ingredient in grouped_ingredients:
                    print(f"- {ingredient}", file = text_file)

        # Print Instructions

        try:
            scraper.instructions_list()
        except AttributeError:
            console.print("    No Instructions found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            print(f"\n# Instructions", file = text_file)

            for [index, instruction] in enumerate(scraper.instructions_list()):
                print(f"{index+1}. {instruction}", file = text_file)

        # Print Nutritional Information

        try:
            scraper.nutrients()
        except AttributeError:
            console.print("    No Nutritional Information found")
        except SchemaOrgException:
            console.print("    Schema Exception")
        else:
            if len(scraper.nutrients()) > 0:
                print(f"\n# Nutritional Information", file = text_file)

                for key in scraper.nutrients():
                    print(f"**{key}**: {scraper.nutrients()[key]}", file = text_file)

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
    file_path = save_recipe_to_markdown(recipe_url, yaml_settings)
    f = open(file_path, "r")
    md = Markdown(f.read())
    f.close()
    print_markdown(md)

    return True


def save_list_of_recipes(url, settings):
    f = open(url, "r")
    for line in f:
        single_url = line.strip().rstrip("\n")
        save_recipe_to_markdown(single_url, settings)


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
