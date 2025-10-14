import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO, format='%(message)s')

WATCH_DIRS = ["src"]
EXTENSIONS = (".toml", ".py")

class RebuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(EXTENSIONS):
            subprocess.run(["python", "build.py"], check=False)

if __name__ == "__main__":
    observer = Observer()
    handler = RebuildHandler()

    for path in WATCH_DIRS:
        observer.schedule(handler, Path(path), recursive=True)

    logging.info("👀 Watching for changes... Press Ctrl+C to stop.")
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()