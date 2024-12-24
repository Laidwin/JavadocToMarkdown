from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional
from io import TextIOWrapper, _WrappedBuffer
from JavadocToMarkdown import JavadocToMarkdown

class JavaDocsProcessor:
    """
    Process Java files in a directory and generate Markdown documentation.
    
    The processor will generate Markdown documentation for each Java file in the source directory.
    The generated documentation will be saved in the output directory.
    The output directory will contain an index file with links to all generated documentation.
    
    The processor uses the JavadocToMarkdown converter to generate Markdown documentation.
    
    Attributes:
        source_dir: Path to the directory containing Java files
        output_dir: Path to the directory where documentation will be generated
        converter: JavadocToMarkdown instance used to generate Markdown documentation
        
    Methods:
        process_directory: Process all Java files in the source directory and its subdirectories
    """
    
    def __init__(self, source_dir: str, output_dir: Optional[str] = "docs"):
        """
        Initialize the processor with source and output directories.
        
        Args:
            source_dir: Path to the directory containing Java files
            output_dir: Path to the directory where documentation will be generated (default: 'docs')
        """
        self.source_dir: Path = Path(source_dir)
        self.output_dir: Path = Path(output_dir)
        self.converter: JavadocToMarkdown = JavadocToMarkdown()
        
    def process_directory(self) -> None:
        """
        Process all Java files in the source directory and its subdirectories.
        Generates Markdown documentation for each Java file.
        The generated documentation will be saved in the output directory.
        The output directory will contain an index file with links to all generated documentation.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        f: TextIOWrapper[_WrappedBuffer]
        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write('# Java Documentation Index\n\n')
            f.write('## Classes\n\n')
        
        java_file: Path
        for java_file in self.source_dir.rglob('*.java'):
            self._process_file(java_file)
            
        print(f"Documentation generated in: {self.output_dir}")
    
    def _process_file(self, file_path: Path) -> None:
        """
        Process a single Java file with improved error handling.
        
        Args:
            file_path: Path to the Java file to be processed
        """
        try:
            f: TextIOWrapper[_WrappedBuffer]
            with open(file_path, 'r', encoding='utf-8') as f:
                content: str = f.read()
            
            if not content.strip():
                print(f"Skipping empty file: {file_path}")
                return
                
            try:
                markdown: str = self.converter.from_javadoc(content, headings_level=1)
            except Exception as e:
                print(f"Error generating markdown for {file_path}: {str(e)}")
                return
            
            try:
                relative_path: Path = file_path.relative_to(self.source_dir)
            except ValueError:
                relative_path: Path = file_path.name
                
            markdown_path: Path = self.output_dir / relative_path.with_suffix('.md')
            
            markdown_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {relative_path}\n\n")
                    f.write(markdown)
                
                with open(self.output_dir / 'index.md', 'a', encoding='utf-8') as f:
                    f.write(f"- [{relative_path}](./{relative_path.with_suffix('.md')})\n")
                    
                print(f"Successfully processed: {relative_path}")
                
            except Exception as e:
                print(f"Error writing output for {file_path}: {str(e)}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
def main():
    """
    Command line interface for the Java docs processor.
    
    Usage:
        python JavaDocsProcessor.py <source_dir> [--output-dir <output_dir>]
    """
    
    parser: ArgumentParser = ArgumentParser(description="Generate Markdown documentation from Java files")
    parser.add_argument("source_dir", help="Directory containing Java files")
    parser.add_argument("--output-dir", "-o", help="Output directory for documentation (optional)")
    
    args: Namespace = parser.parse_args()
    
    processor: JavaDocsProcessor = JavaDocsProcessor(args.source_dir, args.output_dir)
    processor.process_directory()

if __name__ == "__main__":
    main()
