import os
import argparse
import multiprocessing
from typing import List
from document_processor.processing_rules import ProcessingRule, read_config_file
import yaml
import chardet

class DocumentProcessor:
    def __init__(self, input_dir=None, output_dir=None, num_processes=1, config_path=None):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.num_processes = num_processes
        self.config_path = config_path
        self.processing_rules = []

    def parse_file(self, file_path: str) -> str:
        """Parses a file using the provided processing rules"""
        with open(file_path, "rb") as f:
            bytes = f.read()
            encoding = chardet.detect(bytes)["encoding"]
        with open(file_path, "r", encoding=encoding) as f:
            text = f.read()

        for rule in self.processing_rules:
            text = rule.process(text)

        return text

    def process_files(self, file_paths: List[str], output_dir: str) -> None:
        """Processes files using the provided processing rules and saves the results to the output directory"""
        for file_path in file_paths:
            output_file_path = os.path.join(output_dir, os.path.basename(file_path))

            parsed_text = self.parse_file(file_path)

            with open(output_file_path, "w") as f:
                f.write(parsed_text)

    def main(self) -> None:
        """Main function that processes files and writes the results to the output directory"""

        # Read config file
        if self.config_path:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                if 'input_dir' in config and not self.input_dir:
                    self.input_dir = config['input_dir']
                if 'output_dir' in config and not self.output_dir:
                    self.output_dir = config['output_dir']
                if 'num_processes' in config and not self.num_processes:
                    self.num_processes = config['num_processes']

            self.processing_rules = read_config_file(self.config_path)
        else:
            self.processing_rules = []

        # Walk the input_dir for all files in all subdirectories
        if self.input_dir:
            file_paths = []
            for root, _, files in os.walk(self.input_dir):
                for filename in files:
                    file_paths.append(os.path.join(root, filename))
        else:
            raise ValueError("No input directory specified")

        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            raise ValueError("No output directory specified")

        chunks = [[] for _ in range(self.num_processes)]

        for i, file_path in enumerate(file_paths):
            chunks[i % self.num_processes].append(file_path)

        processes = []

        for i in range(self.num_processes):
            p = multiprocessing.Process(
                target=self.process_files, args=(chunks[i], self.processing_rules, self.output_dir)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some HTML files.")
    parser.add_argument("-i", "--input_dir", help="the directory containing the HTML files to process")
    parser.add_argument("-o", "--output_dir", help="the directory to write the processed HTML files to")
    parser.add_argument("-n", "--num_processes", type=int, default=1, help="the number of processes to use for processing files")
    parser.add_argument("-c", "--config_path", help="the path to the config file to use for processing rules")
    args = parser.parse_args()

    DocumentProcessor(input_dir=args.input_dir, output_dir=args.output_dir, num_processes=args.num_processes, config_path=args.config_path).main()
