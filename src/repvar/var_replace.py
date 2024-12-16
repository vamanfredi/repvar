import os
import re
import shutil
import json
import typer
import logging
from pathlib import Path
from typing import Optional

app = typer.Typer()

# Configure logging
logging.basicConfig(
    filename="variable_replacement.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def load_variables(json_path: Path) -> dict:
    """Load variables from a JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load variables from {json_path}: {e}")
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
        else:
            logging.warning(f"Unknown transformation: {transformation}")

    return value

def process_file(input_file: Path, output_file: Path, variables: dict) -> None:
    """Replace variables in a single file and save the result to the output path."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace variables in file content
        updated_content = re.sub(r"\$\{(.*?)}", lambda m: replace_variable(m, variables), content)

        # Write updated content to the output file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

        logging.info(f"Processed file: {input_file} -> {output_file}")
    except Exception as e:
        logging.error(f"Failed to process file {input_file}: {e}")
        raise typer.Exit(f"Error processing file {input_file}: {e}")

def process_folder(input_folder: Path, output_folder: Path, variables: dict) -> None:
    """Process all files in the input folder and save results in the output folder."""
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            input_file = Path(root) / file_name

            # Replace variables in filenames
            updated_file_name = re.sub(r"\$\{(.*?)}", lambda m: replace_variable(m, variables), file_name)
            relative_path = Path(root).relative_to(input_folder)
            output_file = output_folder / relative_path / updated_file_name

            # Process file content
            process_file(input_file, output_file, variables)

@app.command()
def replace(
    input_folder: Path = typer.Argument(..., help="Path to the input folder."),
    output_folder: Path = typer.Argument(..., help="Path to the output folder."),
    variables_json: Optional[Path] = typer.Option(
        None, help="Path to the JSON file with variables. Defaults to variables.json in the input folder."
    ),
):
    """
    Replace variables in all files and filenames in the input folder.

    The replacements are saved in the specified output folder.

    If no variables JSON file is provided, the script looks for variables.json in the input folder.
    """
    # Determine variables JSON file path
    if variables_json is None:
        variables_json = input_folder / "variables.json"

    if not variables_json.exists():
        logging.error(f"Variables JSON file not found: {variables_json}")
        raise typer.Exit("Variables JSON file not found.")

    # Load variables
    variables = load_variables(variables_json)

    # Process folder
    process_folder(input_folder, output_folder, variables)

def main():
    app()
