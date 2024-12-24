#
# This script is a Python implementation of a Javadoc to Markdown converter.
# The JavadocToMarkdown class provides a method from_javadoc that generates Markdown documentation from Javadoc comments.
# 
# Author: William
# Date: 2024-12-24
# License: MIT  

import re
from typing import Any, Callable, Optional, Iterator, Match, Literal

class JavadocToMarkdown:
    """
    Generate Markdown from your Javadoc comments

    Usage: Create a new instance of JavadocToMarkdown and call the from_javadoc method with your Javadoc comments.
    
    Attributes:
        _self: The instance of JavadocToMarkdown
    
    Methods:
        from_javadoc: Generate Markdown from Javadoc comments
        process_tags: Process tags for static types documentation
    """

    def __init__(self):
        """Initialize the JavadocToMarkdown converter."""
        self._self = self

    def _from_doc(self, code: str, headings_level: int, fn_add_tags_markdown: Callable) -> str:
        """
        Generates Markdown documentation from code on a more abstract level.

        Args:
            code (str): The code that contains doc comments
            headings_level (int): The headings level to use as the base (1-6)
            fn_add_tags_markdown (Callabre): Function that processes doc tags and generates Markdown
        
        Returns:
            str: The Markdown documentation
        """
        sections: list[dict[str, str]] = self._get_sections(code)
        
        out: list[str] = []
        out.append("#" * headings_level + " Documentation")

        section: dict[str, str]
        for section in sections:
            out.append(self._from_section(section, headings_level, fn_add_tags_markdown))

        return "".join(out) + "\n"

    def process_tags(self, tag: dict[str, str], assoc_buffer: dict[str, list[str]]) -> None:
        """ 
        Process tags for static types documentation.

        Args:
            tag (dict[str, str]): The tag to process
            assoc_buffer (dict[str, list[str]]): The buffer to store the tags
        """
        
        def add_to_buffer(key: str, value: Optional[str]) -> None:
            """ Add a tag to the buffer.
            
            Args:
                key (str): The key of the tag
                value (Optional[str]): The value of the tag
            """
            if key not in assoc_buffer:
                assoc_buffer[key] = []
            assoc_buffer[key].append(value)

        key: str = tag['key']
        value: str = tag['value']

        if key in ['abstract', 'access', 'author', 'copyright', 'exports', 'license', 'link', 'package', 'since', 'static', 'subpackage']:
            add_to_buffer(key.title(), value)
        elif key in ['constructor', 'deprecated', 'private']:
            add_to_buffer(key.title(), None)
        elif key in ['exception', 'throws']:
            tokens = self._tokenize(value, r'\s+', 2)
            add_to_buffer('Exceptions', f'`{tokens[0]}` — {tokens[1]}')
        elif key == 'param':
            tokens = self._tokenize(value, r'\s+', 2)
            add_to_buffer('Parameters', f'`{tokens[0]}` — {tokens[1]}')
        elif key in ['return', 'returns']:
            add_to_buffer('Returns', value)
        elif key == 'see':
            add_to_buffer('See also', value)
        elif key == 'this':
            add_to_buffer('This', f'`{value}`')
        elif key == 'todo':
            add_to_buffer('To-do', value)
        elif key == 'version':
            add_to_buffer('Version', value)
    
    def from_javadoc(self, code: str, headings_level: int) -> str:
        """
        Generates Markdown documentation from Javadoc comments.

        Args:
            code (str): The code that contains doc comments
            headings_level (int): The headings level to use as the base (1-6)
        
        Returns:
            str: The Markdown documentation
        """
        return self._from_doc(code, headings_level, self.process_tags)

    def _from_section(self, section: dict[str, str], headings_level: int, fn_add_tags_markdown: Callable) -> str:
        """
        Process a single documentation section.
        
        Args:
            section (dict[str, str]): The section containing the code and doc comment
            headings_level (int): The level of headings to use
            fn_add_tags_markdown (Callable): Function that processes doc tags and generates Markdown
        
        Returns:
            str: The Markdown documentation for the section
        """
        field: str = self._get_field_declaration(section['line'])
        if not field:
            return ""

        out: list[str] = []
        out.append("\n\n")
        out.append("#" * (headings_level + 1) + f" `{field}`")

        doc_comment_parts: list[str | Any] = re.split(r'^(?:\t| )*?\*(?:\t| )*?(?=@)', section['doc'], flags=re.M)
        raw_main_description: str | Any = doc_comment_parts[0]
        raw_tags: list[str | Any] = doc_comment_parts[1:] if len(doc_comment_parts) > 1 else []

        description: str = self._get_doc_description(raw_main_description)
        if description:
            out.append("\n\n")
            out.append(description)

        tags: list[dict[str, str]] = self._get_doc_tags(raw_tags)
        if tags:
            out.append("\n")
            assoc_buffer: dict[str, list[str]] = {}
            
            tag: dict[str, str]
            for tag in tags:
                fn_add_tags_markdown(tag, assoc_buffer)

            name: str
            entries: list[str]
            for name, entries in assoc_buffer.items():
                out.append(self._from_tag_group(name, entries))

        return "".join(out)

    def _get_doc_description(self, doc_lines: str) -> str:
        """
        Extract and format the main description from doc lines with improved handling.
        
        Args:
            doc_lines (str): The lines of the doc comment
        
        Returns:
            str: The formatted description
        """
        try:
            clean_lines: list[str] = []
            line: str
            for line in doc_lines.split('\n'):
                line = re.sub(r'^\s*\*\s*', '', line)
                line = re.sub(r'^\s*/\*+\s*', '', line)
                line = re.sub(r'\s*\*+/\s*$', '', line)
                
                if line.strip():
                    clean_lines.append(line.strip())
            
            description: str = ' '.join(clean_lines)
            description = self._clean_line(description)
            description = self._replace_html_with_markdown(description)
            return description.replace('<p>', '\n\n').replace('</p>', '\n\n')
            
        except Exception as e:
            print(f"Warning: Error processing description: {str(e)}")
            return ""
    
    def _from_tag_group(self, name: str, entries: list[Optional[str]]) -> str:
        """
        Format a group of tags into Markdown.
        
        Args:
            name (str): The name of the tag group
            entries (list[Optional[str]]): The entries for the tag group
            
        Returns:
            str: The formatted tag group
        """
        out: list[str] = ["\n"]
        
        if len(entries) == 1 and entries[0] is None:
            out.append(f" * **{name}**")
        else:
            out.append(f" * **{name}:**")
            if len(entries) > 1:
                for entry in entries:
                    out.append("\n")
                    out.append(f"   * {entry}")
            elif len(entries) == 1:
                out.append(f" {entries[0]}")

        return "".join(out)

    def _get_sections(self, code: str) -> list[dict[str, str]]:
        """
        Extract documentation sections from code with improved pattern matching.
        
        Args:
            code (str): The code to extract sections from
            
        Returns:
            list[dict[str, str]]: The extracted sections
        """
        sections: list[dict[str, str]] = []
        
        pattern: Literal[''] = r'/\*\*(.*?)\*/\s*([^{;]*(?:[{;]|$))'
        try:
            matches: Iterator[Match[str]] = re.finditer(pattern, code, re.DOTALL)
            
            match: Match[str]
            for match in matches:
                try:
                    doc_comment: str | Any = match.group(1) if match.group(1) else ""
                    code_section: str | Any = match.group(2) if match.group(2) else ""
                    
                    if not doc_comment or not code_section:
                        continue
                        
                    code_section: str | Any = code_section.strip()
                    
                    if code_section.startswith('import'):
                        continue
                    
                    if not doc_comment.strip().startswith('*'):
                        doc_comment = f"* {doc_comment.strip()}"
                    
                    sections.append({
                        'line': code_section,
                        'doc': doc_comment
                    })
                    
                except Exception as e:
                    print(f"Warning: Error processing individual section: {str(e)}")
                    print(f"Problem section text: {match.group(0)[:100]}...")
                    continue
                    
        except Exception as e:
            print(f"Warning: Error in pattern matching: {str(e)}")
            
        if not sections:
            try:
                fallback_pattern: Literal[''] = r'/\*\*(.*?)\*/'
                matches: Iterator[Match[str]] = re.finditer(fallback_pattern, code, re.DOTALL)
                
                match: Match[str]
                for match in matches:
                    doc_comment: str | Any = match.group(1)
                    if doc_comment:
                        end_pos: int = match.end()
                        next_lines: list[str] = code[end_pos:].split('\n')
                        line: str
                        for line in next_lines:
                            if line.strip():
                                sections.append({
                                    'line': line.strip(),
                                    'doc': doc_comment
                                })
                                break
            except Exception as e:
                print(f"Warning: Error in fallback pattern matching: {str(e)}")
        
        return sections
    
    def _get_field_declaration(self, line: str) -> str:
        """
        Extract field declaration with improved handling.
        
        Args:
            line (str): The line to extract the field declaration from
        
        Returns:
            str: The extracted field declaration
        """
        try:
            line = re.sub(r'[{;]\s*$', '', line)
            return self._clean_single_line(line)
        except Exception as e:
            print(f"Warning: Error processing field declaration: {str(e)}")
            return line.strip()


    def _replace_html_with_markdown(self, html: str) -> str:
        """
        Convert HTML tags to Markdown format.
        
        Args:
            html (str): The HTML text to convert
        
        Returns:
            str: The Markdown text
        """
        return re.sub(r'<\s*?code\s*?>(.*?)<\s*?/\s*?code\s*?>', r'`\1`', html)

    def _get_doc_tags(self, doc_lines: list[str]) -> list[dict[str, str]]:
        """
        Extract and format documentation tags with improved error handling.
        
        Args:
            doc_lines (list[str]): The lines of the doc comment
            
        Returns:
            list[dict[str, str]]: The formatted tags
        """
        tags: list[dict[str, str]] = []
        pattern: Literal[''] = r'^(?:\t| )*?@([a-zA-Z]+)([\s\S]*)'
        
        line: str
        for line in doc_lines:
            try:
                match: Match[str] | None = re.match(pattern, line)
                if match:
                    key: str | Any
                    value: str | Any
                    key, value = match.groups()
                    value = value.strip() if value else ""
                    value = re.sub(r'[\r\n]{1,2}(?:\t| )*?\*(?:\t| )*', '\n\n     ', value)
                    tags.append({
                        'key': self._clean_single_line(key),
                        'value': value
                    })
            except Exception as e:
                print(f"Warning: Error processing doc tag: {str(e)}")
                continue
                
        return tags

    def _clean_line(self, line: str) -> str:
        """
        Clean up a line of text safely.
        
        Args:
            line (str): The line to clean
            
        Returns:
            str: The cleaned line
        """
        try:
            line = line.strip()
            line = re.sub(r'\s+', ' ', line)
            return line
        except Exception as e:
            print(f"Warning: Error cleaning line: {str(e)}")
            return line

    def _clean_single_line(self, line: str) -> str:
        """
        Clean up a single line of text.
        
        Args:
            line (str): The line to clean
        
        Returns:
            str: The cleaned line
        """
        line = self._clean_line(line)
        line = re.sub(r'[\n\r\t]', ' ', line)
        return line

    def _tokenize(self, text: str, split_by_regex: str, limit: int) -> list[str]:
        """
        Split text into tokens with improved error handling.
        
        Args:
            text (str): The text to tokenize
            split_by_regex (str): The regex pattern to split by
            limit (int): The maximum number of tokens to return
        
        Returns:
            list[str]: The tokens
        """
        try:
            if not text:
                return [''] * limit
                
            tokens: list[str | Any] = re.split(split_by_regex, text.strip(), maxsplit=limit-1)
            return (tokens + [''] * limit)[:limit]
            
        except Exception as e:
            print(f"Warning: Error tokenizing text: {str(e)}")
            return [''] * limit
