# JSON Variable Replacer CLI (repvar)

This project is a Command Line Interface (CLI) application built using Python and the `typer` library. It allows you to replace variables in files and filenames within an input folder and save the processed files to an output folder.

## Features

- **Variable Replacement**: Replace variables in the format `${variable}` found in file contents and filenames.
- **Transformations**: Supports variable transformations such as:
  - `lowercase`: Convert variable value to lowercase.
  - `uppercase`: Convert variable value to uppercase.
  - `nocase`: Remove underscores (`_`) and apply lowercase.
  - `remove_`: Remove underscores (`_`).
- **Automatic Variable Detection**: If no variables JSON file is specified, the application looks for a `variables.json` file in the input folder.
- **Logging Summary**: Displays a concise summary with color-coded output, including:
  - Number of files found.
  - Number of files changed.
  - Number of files unchanged.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vamanfredi/repvar.git
   cd repvar
   ```
2. Install dependencies:
   ```bash
   pip install typer typing-extensions
   ```
### Method 2: Use uv
 1. Install uv:
    ```bash
    pip install uv
    ```
 2. Run uv tool install:
    ```bash
     uv tool install --from git+https://github.com/vamanfredi/repvar repvar
     ```

## Usage

Run the CLI application with the following command:
```bash
python main.py replace <input_folder> <output_folder> [variables_json]
```

### Arguments
- `<input_folder>`: Path to the folder containing the files to process.
- `<output_folder>`: Path to the folder where processed files will be saved.
- `[variables_json]`: Optional. Path to the JSON file with variables. Defaults to `variables.json` in the input folder.

### Example
```bash
python main.py replace ./input ./output ./variables.json
```

## Example `variables.json`

```json
{
  "username": "JohnDoe",
  "project": "MyProject",
  "greeting": "Hello"
}
```

### Result
- Before replacement:
  - Filename: `welcome_${username}.txt`
  - Content: `Welcome to ${project}, ${greeting}!`
- After replacement:
  - Filename: `welcome_JohnDoe.txt`
  - Content: `Welcome to MyProject, Hello!`

## Output Example

Upon execution, the CLI will display a summary:
```plaintext
Input Folder: ./input
Output Folder: ./output
Variables Loaded: ['username', 'project', 'greeting']
Files Found: 10
✓ Files Changed: 8
~ Files Unchanged: 2
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

