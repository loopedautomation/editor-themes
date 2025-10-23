import subprocess
import logging
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO, format="%(message)s")

WATCH_DIRS = ["src"]
EXTENSIONS = (".toml", ".py")
# Enable test running with --test flag
RUN_TESTS = "--test" in sys.argv


class RebuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(EXTENSIONS):
            return

        changed_path = Path(event.src_path)
        logging.info(f"🔄 File changed: {event.src_path}")

        # Determine which build scripts to run based on file location
        build_vscode = False
        build_zed = False

        # Check if the change is in a template directory
        if "templates/code" in event.src_path or "templates\\code" in event.src_path:
            logging.info("📝 VS Code template changed")
            build_vscode = True
        elif "templates/zed" in event.src_path or "templates\\zed" in event.src_path:
            logging.info("📝 Zed template changed")
            build_zed = True
        else:
            # For other changes (theme files, build scripts, etc), rebuild both
            logging.info("📝 Generic source changed, rebuilding both")
            build_vscode = True
            build_zed = True

        # Run VS Code build if needed
        if build_vscode:
            logging.info("🏗️  Building VS Code themes...")
            result = subprocess.run(
                ["python", "build.py"], capture_output=True, text=True
            )
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode != 0:
                logging.error(f"❌ build.py failed with code {result.returncode}")
            else:
                logging.info("✅ VS Code build complete")

        # Run Zed build if needed
        if build_zed:
            logging.info("🏗️  Building Zed themes...")
            result = subprocess.run(
                ["python", "build_zed.py"], capture_output=True, text=True
            )
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode != 0:
                logging.error(f"❌ build_zed.py failed with code {result.returncode}")
            else:
                logging.info("✅ Zed build complete")

        # Run tests if enabled
        if RUN_TESTS and (build_vscode or build_zed):
            logging.info("🧪 Running tests...")
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode != 0:
                logging.error("❌ Tests failed")
            else:
                logging.info("✅ All tests passed")

        logging.info("")  # Empty line for readability


if __name__ == "__main__":
    observer = Observer()
    handler = RebuildHandler()

    for path in WATCH_DIRS:
        observer.schedule(handler, Path(path), recursive=True)

    logging.info("👀 Watching for changes... Press Ctrl+C to stop.")
    logging.info("   - Changes to src/templates/code/ → build VS Code themes only")
    logging.info("   - Changes to src/templates/zed/ → build Zed themes only")
    logging.info("   - Changes to other files → build both")
    if RUN_TESTS:
        logging.info("   - Tests will run after each build (--test flag enabled)")
    else:
        logging.info("   - Tip: Add --test flag to run tests after each build")
    logging.info("")
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
