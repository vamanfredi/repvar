import os
import re
import json
import typer
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

app = typer.Typer()

# ANSI color codes for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

summary = {"found": 0, "changed": 0, "unchanged": 0}

def load_variables(json_path: Path) -> dict:
    """Load variables from a JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}✗ ERROR: Failed to load variables from {json_path}: {e}{RESET}")
        raise typer.Exit(f"Error loading variables file: {e}")

def replace_variable(match: re.Match, variables: dict) -> str:
    """Replace a variable with its value, applying transformations."""
    raw_var = match.group(1)  # Extract the variable name with transformation
    if "-" in raw_var:
        var_name, transformation = raw_var.split("-", 1)
    else:
        var_name, transformation = raw_var, None

    value = variables.get(var_name, match.group(0))  # Default to the original if not found

    if transformation:
        if transformation == "lowercase":
            value = value.lower()
        elif transformation == "uppercase":
            value = value.upper()
        elif transformation == "nocase":
            value = value.replace("_", "").lower()
        elif transformation == "remove_":
            value = value.replace("_", "")

    return value

def process_file(input_file: Path, output_file: Path, variables: dict) -> bool:
    """Replace variables in a single file and save the result to the output path."""
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    updated_content = re.sub(r"\$\{(.*?)}", lambda m: replace_variable(m, variables), content)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Return whether the content was modified
    return content != updated_content


def process_folder(input_folder: Path, output_folder: Path, variables: dict) -> None:
    """Process all files in the input folder and save results in the output folder."""
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            # Skip the variables.json file
            if file_name == "variables.json":
                continue

            summary["found"] += 1
            input_file = Path(root) / file_name

            updated_file_name = re.sub(r"\$\{(.*?)}", lambda m: replace_variable(m, variables), file_name)
            relative_path = Path(root).relative_to(input_folder)
            output_file = output_folder / relative_path / updated_file_name

            if process_file(input_file, output_file, variables):
                summary["changed"] += 1
            else:
                summary["unchanged"] += 1


@app.command()
def replace(
    input_folder: Path = typer.Argument(..., help="Path to the input folder."),
    output_folder: Path = typer.Argument(..., help="Path to the output folder."),
    variables_json: Annotated[Optional[Path], typer.Argument(..., help="Path to the JSON file with variables. Defaults to variables.json in the input folder.")] = None
):
    """
    Replace variables in all files and filenames in the input folder.

    The replacements are saved in the specified output folder.

    If no variables JSON file is provided, the script looks for variables.json in the input folder.
    """
    if variables_json is None:
        variables_json = input_folder / "variables.json"

    if not variables_json.exists():
        print(f"{RED}✗ ERROR: Variables JSON file not found: {variables_json}{RESET}")
        raise typer.Exit("Variables JSON file not found.")

    variables = load_variables(variables_json)
    print(f"{MAGENTA}Input Folder: {input_folder}{RESET}")
    print(f"{MAGENTA}Output Folder: {output_folder}{RESET}")
    print(f"{MAGENTA}Variables Loaded: {list(variables.keys())}{RESET}")

    process_folder(input_folder, output_folder, variables)

    # Print summary with colors
    print(f"{BLUE}Files Found: {summary['found']}{RESET}")
    print(f"{GREEN}✓ Files Changed: {summary['changed']}{RESET}")
    print(f"{YELLOW}~ Files Unchanged: {summary['unchanged']}{RESET}")

def main():
    app()

