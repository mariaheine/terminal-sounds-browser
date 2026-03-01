import sys
import argparse
import requests
from pathlib import Path
from src.logger import Logger

class DownloadWorker:
    def __init__(self, logger: Logger, url: str, file_path: Path):
        self.url = url
        self.logger = logger
        self.download_path = file_path

    def download_file(self):
        self.logger.info(f"Starting download at {self.url}")

        temp_file = Path(f"{self.download_path}.tmp")

        response = requests.get(self.url, stream=True)
        response.raise_for_status() # TODO

        try:
            if response.status_code == 200:
                with temp_file.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.logger.warning(f"done {self.download_path}")
                temp_file.rename(self.download_path)
            else:
                self.logger.error(f"Download bbc preview sound failed, status code: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error while downloading from url: {self.url}, status code: {response.status_code}, error: {e}")

def main():

    logger = Logger()
    logger.info("ARE WE EVEN HERE")

    parser = argparse.ArgumentParser(description="Download Worker")
    parser.add_argument("url")
    parser.add_argument("download_path")
    args = parser.parse_args()
    
    worker = DownloadWorker(logger, args.url, Path(args.download_path))
    worker.download_file()

if __name__ == "__main__":
    main()
