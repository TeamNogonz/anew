import os
import sys
from pathlib import Path

os.environ["ENVIRONMENT"] = "development"
os.environ["FIXTURE_MODE"] = "true"
os.environ["SCHEDULE_ENABLED"] = "false"
os.environ["NUDGER_SERVICE_TOKEN"] = "s" * 32
os.environ["GOOGLE_API_KEY"] = "test-only"
os.environ["LOG_DIR"] = "/tmp/anew-test-logs"
os.environ["LOG_FORMAT"] = "%(asctime)s %(levelname)s %(message)s"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
