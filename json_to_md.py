#!/usr/bin/env python3
"""
JSON to Markdown Converter

This script parses a JSON file containing conversation data (like GitHub Copilot conversations)
and converts it into a well-formatted Markdown document.
"""

import json
import sys
import os
import re
from datetime import datetime

def clean_json_file(file_path):
    """Remove comments and fix potential JSON issues in the input file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
    
    # Try to parse and return the content
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Attempting to clean the JSON file...")
        
        # More aggressive cleaning if needed
        # This is a simplified approach - for complex JSON issues you might need more robust handling
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            if not line.strip().startswith('//'):
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e2:
            print(f"Could not parse JSON even after cleaning: {e2}")
            sys.exit(1)

def extract_code_blocks(text):
    """Extract code blocks from text using regex patterns."""
    if not text:
        return text
    
    # Look for markdown code blocks with language specification
    pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f"\n```{lang}\n{code}\n```\n"
    
    # First, handle code blocks
    processed = re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
    
    # Then handle potential inline code using backticks
    inline_pattern = r'`([^`]+)`'
    processed = re.sub(inline_pattern, r'`\1`', processed)
    
    return processed

def convert_tool_invocation(invocation, include_details=False):
    """Convert a tool invocation to markdown format."""
    md_content = []
    
    if 'invocationMessage' in invocation and 'value' in invocation['invocationMessage']:
        message = invocation['invocationMessage']['value']
        md_content.append(f"> **Tool Invocation:** {message}")
    
    if 'pastTenseMessage' in invocation and 'value' in invocation['pastTenseMessage']:
        result = invocation['pastTenseMessage']['value']
        md_content.append(f"> **Result:** {result}")
    
    if include_details and 'resultDetails' in invocation:
        md_content.append("\n<details><summary>Result Details</summary>\n")
        md_content.append("```json")
        md_content.append(json.dumps(invocation['resultDetails'], indent=2))
        md_content.append("```")
        md_content.append("</details>\n")
    
    return "\n".join(md_content)

def generate_markdown(data, output_file, include_details=False, compact_mode=False):
    """Generate markdown content from the parsed JSON data.
    
    Args:
        data: The parsed JSON data
        output_file: Path where the markdown file will be written
        include_details: Whether to include detailed tool results
        compact_mode: Whether to generate a more compact output
    """
    md_content = []
    
    # Add title and metadata
    md_content.append(f"# Conversation with {data.get('responderUsername', 'Assistant')}")
    md_content.append(f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")
    
    # Process each request and response
    for request in data.get('requests', []):
        # Process user request
        user_message = request.get('message', {}).get('text', '')
        request_id = request.get('requestId', '')
        
        if compact_mode:
            md_content.append(f"## User")
        else:
            md_content.append(f"## User: {request_id}")
            
        md_content.append(user_message)
        md_content.append("")
        
        # Process response
        md_content.append(f"## {data.get('responderUsername', 'Assistant')}:")
        
        for response_item in request.get('response', []):
            # Handle text responses
            if 'value' in response_item and response_item['value']:
                content = extract_code_blocks(response_item['value'])
                md_content.append(content)
            
            # Handle tool invocations
            elif 'kind' in response_item and response_item['kind'] == 'toolInvocationSerialized':
                md_content.append(convert_tool_invocation(response_item, include_details))
            
            # Handle text edits
            elif 'kind' in response_item and response_item['kind'] == 'textEditGroup':
                if 'uri' in response_item:
                    file_path = response_item['uri'].get('path', '').split('/')[-1]
                    md_content.append(f"\n> **Edited file:** `{file_path}`\n")
                    
                    # Include the edits if details are requested
                    if include_details and 'edits' in response_item:
                        md_content.append("<details><summary>File Edits</summary>\n")
                        md_content.append("```json")
                        md_content.append(json.dumps(response_item['edits'], indent=2))
                        md_content.append("```")
                        md_content.append("</details>\n")
            
            # Handle other kinds of response items if details are requested
            elif include_details and 'kind' in response_item:
                kind = response_item['kind']
                md_content.append(f"\n> **{kind}**\n")
        
        md_content.append("\n---\n")
    
    # Write the markdown content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert JSON conversation files to Markdown')
    parser.add_argument('input_file', help='Path to the JSON file to be converted')
    parser.add_argument('output_file', nargs='?', help='Path for the output Markdown file (optional)')
    parser.add_argument('--details', '-d', action='store_true', help='Include detailed results in the output')
    parser.add_argument('--compact', '-c', action='store_true', help='Generate a more compact Markdown output')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    
    # Default output filename if not provided
    if args.output_file:
        output_file = args.output_file
    else:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.md"
    
    # Parse the JSON file
    try:
        data = clean_json_file(input_file)
        generate_markdown(data, output_file, include_details=args.details, compact_mode=args.compact)
        print(f"Markdown file generated: {output_file}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
