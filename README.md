# JSON to Markdown Converter

This tool converts Copilot JSON conversation files to well-formatted Markdown.

## Features

- Parses JSON files containing Copilot conversations
- Extracts and formats user requests and assistant responses
- Preserves code blocks and formatting
- Handles tool invocations and file edits

## Usage

```bash
python json_to_md.py <input_json_file> [output_md_file] [options]
```

### Arguments:

- `input_json_file`: Path to the JSON file to be converted (required)
- `output_md_file`: Path for the output Markdown file (optional, default: same name with .md extension)

### Options:

- `--details` or `-d`: Include detailed results in the output (like full tool responses and file edit details)
- `--compact` or `-c`: Generate a more compact Markdown output (omit request IDs and other verbose elements)

### Examples:

Basic conversion:
```bash
python json_to_md.py petsdb-fe.json conversation.md
```

Generate a detailed markdown with all available information:
```bash
python json_to_md.py petsdb-fe.json conversation.md --details
```

Generate a compact markdown for easier reading:
```bash
python json_to_md.py petsdb-fe.json --compact
```

If you don't specify an output file, it will create one with the same name as the input file but with a `.md` extension:
```bash
python json_to_md.py petsdb-fe.json
# Creates petsdb-fe.md
```

## Output Format

The generated Markdown file includes:
- Title with assistant's name
- Timestamp of generation
- Each request/response pair as a section
- Code blocks preserved with proper formatting
- Tool invocation summary information
- Indication of file edits

With the `--details` option, the output will also include:
- Detailed tool invocation results
- Raw JSON for file edits
- More information about other response items

## Requirements

- Python 3.6 or higher
- No additional packages needed (uses standard library only)
