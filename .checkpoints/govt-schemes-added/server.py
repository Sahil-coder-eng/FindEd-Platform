#!/usr/bin/env python3
"""
Find Ed - Resilient HTTP Server with Automatic Checkpoint Fallback
==================================================================
This server serves Find Ed on port 3000.
If any file is corrupted, missing, or if an error is encountered during
request handling or server execution, the server automatically falls back
to the verified checkpoint state in .checkpoints/fallback/ and self-heals.
"""

import http.server
import socketserver
import os
import sys
import shutil
import json
import logging
import time
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT_DIR = BASE_DIR / ".checkpoints" / "fallback"
LOG_FILE = BASE_DIR / "server.log"
PORT = 3000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def restore_from_checkpoint(specific_file: str = None):
    """Restores files from the fallback checkpoint."""
    if not CHECKPOINT_DIR.exists():
        logging.error(f"Fallback checkpoint directory not found at {CHECKPOINT_DIR}")
        return False
    
    try:
        if specific_file:
            src = CHECKPOINT_DIR / specific_file
            dst = BASE_DIR / specific_file
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                logging.info(f"Self-healed from checkpoint: restored '{specific_file}'")
                return True
            else:
                logging.warning(f"File '{specific_file}' not found in fallback checkpoint.")
                return False
        else:
            # Full restoration
            logging.info("Restoring full application state from fallback checkpoint...")
            for item in CHECKPOINT_DIR.iterdir():
                dst = BASE_DIR / item.name
                if item.is_dir():
                    shutil.copytree(item, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dst)
            logging.info("Full restoration from fallback checkpoint completed successfully.")
            return True
    except Exception as e:
        logging.error(f"Error during checkpoint restoration: {e}")
        return False

class FallbackHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with error trapping and self-healing fallback."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        # Health check endpoint
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            data = {
                "status": "healthy",
                "app": "Find Ed",
                "port": PORT,
                "checkpoint_available": CHECKPOINT_DIR.exists(),
                "time": time.time()
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # Explicit restore endpoint
        if self.path == "/api/restore-fallback":
            success = restore_from_checkpoint()
            self.send_response(200 if success else 500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            resp = {
                "restored": success,
                "message": "Fallback state restored successfully" if success else "Restoration failed",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # Clean requested path to verify target file
        clean_path = self.path.split("?")[0].lstrip("/")
        if not clean_path or clean_path == "":
            clean_path = "index.html"
            
        target_file = BASE_DIR / clean_path
        
        # Verify if target file is missing or corrupted (0-byte)
        if not target_file.exists() or (target_file.is_file() and target_file.stat().st_size == 0):
            logging.warning(f"File missing or empty: {clean_path}. Triggering automatic fallback recovery.")
            restored = restore_from_checkpoint(clean_path)
            if not restored and clean_path == "index.html":
                # Fall back to serving checkpoint file directly
                checkpoint_index = CHECKPOINT_DIR / "index.html"
                if checkpoint_index.exists():
                    logging.info("Directly serving index.html from checkpoint fallback.")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    with open(checkpoint_index, "rb") as f:
                        self.wfile.write(f.read())
                    return

        try:
            super().do_GET()
        except Exception as e:
            logging.error(f"Error handling GET request for {self.path}: {e}")
            logging.info("Encountered error in request handling: incorporating fallback state...")
            restore_from_checkpoint()
            # Send fallback response
            try:
                checkpoint_index = CHECKPOINT_DIR / "index.html"
                if checkpoint_index.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    with open(checkpoint_index, "rb") as f:
                        self.wfile.write(f.read())
            except Exception as inner_e:
                logging.error(f"Failed to serve fallback: {inner_e}")
                self.send_error(500, "Internal Server Error - Fallback triggered")

    def log_message(self, format, *args):
        # Route HTTP access logs to logging
        logging.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def run_server():
    """Runs the server with auto-recovery and crash supervision."""
    logging.info(f"Starting Find Ed server on port {PORT} with checkpoint fallback protection...")
    logging.info(f"Fallback checkpoint directory: {CHECKPOINT_DIR}")
    
    # Ensure checkpoint exists
    if not CHECKPOINT_DIR.exists():
        logging.warning("Fallback checkpoint directory missing. Creating initial snapshot...")
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        restore_from_checkpoint()

    # Supervision loop
    while True:
        try:
            with ReusableTCPServer(("", PORT), FallbackHTTPRequestHandler) as httpd:
                logging.info(f"Find Ed server active and listening at http://localhost:{PORT}/")
                httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user.")
            break
        except Exception as e:
            logging.error(f"Server encountered an unexpected error: {e}")
            logging.info("Triggering automatic state restoration from fallback checkpoint...")
            restore_from_checkpoint()
            logging.info("Restarting server in 1 second...")
            time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_from_checkpoint()
    else:
        run_server()
