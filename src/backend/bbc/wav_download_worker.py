import sys
import argparse
import zipfile
import requests
from pathlib import Path
from src.backend.common.logger import Logger


class WavDownloadWorker:
    def __init__(self, logger: Logger, url: str, dest_dir: Path, sound_id: str, filename: str):
        self.url = url
        self.logger = logger
        self.dest_dir = dest_dir
        self.sound_id = sound_id
        self.filename = filename

    def download_and_extract(self):
        self.dest_dir.mkdir(parents=True, exist_ok=True)

        zip_path = self.dest_dir / f"{self.sound_id}.wav.zip"
        temp_path = Path(f"{zip_path}.tmp")
        wav_path = self.dest_dir / f"{self.filename}.wav"

        if wav_path.exists():
            self.logger.info(f"WAV already exists, skipping: {wav_path}")
            return

        self.logger.info(f"Downloading WAV zip from {self.url}")

        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()

            with temp_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            temp_path.rename(zip_path)

        except Exception as e:
            self.logger.error(f"Failed to download WAV zip: {e}")
            temp_path.unlink(missing_ok=True)
            return

        self.logger.info(f"Extracting {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    if member.endswith(".wav"):
                        data = zf.read(member)
                        wav_path.write_bytes(data)
                        break

        except Exception as e:
            self.logger.error(f"Failed to extract WAV zip: {e}")
        finally:
            zip_path.unlink(missing_ok=True)

        if wav_path.exists():
            self.logger.info(f"WAV saved to {wav_path}")
        else:
            self.logger.error(f"WAV extraction produced no file at {wav_path}")


def main():
    logger = Logger()

    parser = argparse.ArgumentParser(description="WAV Download Worker")
    parser.add_argument("url")
    parser.add_argument("dest_dir")
    parser.add_argument("sound_id")
    parser.add_argument("filename")
    args = parser.parse_args()

    worker = WavDownloadWorker(logger, args.url, Path(args.dest_dir), args.sound_id, args.filename)
    worker.download_and_extract()


if __name__ == "__main__":
    main()
