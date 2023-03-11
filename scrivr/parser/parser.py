import os
import argparse
import multiprocessing
from typing import List
from .processing_rules import read_config_file
import yaml
import chardet
import warnings

class ScrivrParser:
    def __init__(self, input_dir=None, output_dir=None, num_processes=1, config_path=None, output_filetype=''):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.num_processes = num_processes
        self.config_path = config_path
        self.processing_rules = []
        self.output_filetype = output_filetype

        if config_path:
            self.load_config()

    def load_config(self):
        """Reads the config file and returns a list of processing rules"""
        if self.config_path:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                if 'input_dir' in config and not self.input_dir:
                    self.input_dir = config['input_dir']
                if 'output_dir' in config and not self.output_dir:
                    self.output_dir = config['output_dir']
                if 'num_processes' in config:
                    self.num_processes = config['num_processes']
                if 'output_filetype' in config:
                    self.output_filetype = config['output_filetype']

            self.processing_rules = read_config_file(self.config_path)

    def process_files(self) -> None:
        """Processes files in the input directory using the given processing rules and writes the results to the output directory"""

        if not self.input_dir:
            raise ValueError("No input directory specified.")
        if not self.output_dir:
            raise ValueError("No output directory specified.")

        # Walk the input_dir for all files in all subdirectories
        file_paths = []
        for root, _, files in os.walk(self.input_dir):
            if not files:
                warnings.warn(f"No files found in input directory {self.input_dir}")
            for filename in files:
                file_paths.append(os.path.join(root, filename))

        os.makedirs(self.output_dir, exist_ok=True)

        chunks = [[] for _ in range(self.num_processes)]

        for i, file_path in enumerate(file_paths):
            chunks[i % self.num_processes].append(file_path)

        processes = []

        for i in range(self.num_processes):
            p = multiprocessing.Process(
                target=self.process_files_chunk, args=(chunks[i],)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    def process_files_chunk(self, file_paths: List[str]) -> None:
        """Processes files using the provided processing rules and saves the results to the output directory"""
        for file_path in file_paths:
            base_name, ext = os.path.splitext(os.path.basename(file_path))

            output_file_path = os.path.join(self.output_dir, "{}{}".format(base_name, ext))

            # Modify output_file_path extension if output_filetype is not empty
            if self.output_filetype:
                output_file_root = os.path.join(self.output_dir, base_name)

                # Avoid creating `file..txt` if output_filetype starts with '.'
                ext = self.output_filetype[1:] if self.output_filetype.startswith(".") else self.output_filetype
                output_file_path = output_file_root + '.' + ext

            parsed_text = self.parse_file(file_path)

            with open(output_file_path, "w") as f:
                f.write(parsed_text)


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("-i", "--input_dir", help="the directory containing the files to process")
    parser.add_argument("-o", "--output_dir", help="the directory to write the processed files to")
    parser.add_argument("-f", "--output_filetype", help="The extension type of outputted files")
    parser.add_argument("-n", "--num_processes", type=int, default=1, help="the number of processes to use for processing files")
    parser.add_argument("-c", "--config_path", help="the path to the config file to use for processing rules")
    args = parser.parse_args()

    ScrivrParser(input_dir=args.input_dir, output_dir=args.output_dir, num_processes=args.num_processes, config_path=args.config_path, output_filetype=args.output_filetype).process_files()
