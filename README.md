# JavaDoc to Markdown Converter

A Python tool that converts Javadoc comments into Markdown documentation.

## Features

- Converts Javadoc comments to Markdown
- Processes single files or entire directories
- Maintains original code structure in documentation
- Generates documentation index
- Supports common doc tags (@param, @return, @throws, etc.)
- Handles multiple documentation styles

## Installation

1. Clone the repository
2. Ensure Python 3.9+ is installed
3. No additional dependencies required

## Usage

### Command Line

```bash
python process_java_docs.py /path/to/your/java/files
# Optional: specify output directory
python process_java_docs.py /path/to/your/java/files -o /path/to/output
```

### Python Code

```python
from java_docs_processor import JavaDocsProcessor

# Initialize processor
processor = JavaDocsProcessor("/path/to/your/java/files")

# Generate documentation
processor.process_directory()
```

## Output

- Creates a `docs` directory containing:
  - Markdown files for each processed Java file
  - `index.md` linking to all documentation
  - Maintains source directory structure

## Supported Tags

- `@param` - Method parameters
- `@return` - Return values
- `@throws` - Exceptions
- `@author` - Authors
- `@version` - Version information
- `@see` - References
- And more...

## License

MIT License