# -*- coding: utf-8 -*-
from pathlib import Path
import unittest


COMPOSE = (Path(__file__).resolve().parents[1] / "docker-compose.yml").read_text(encoding="utf-8-sig")


class TestDockerContracts(unittest.TestCase):
    def test_ollama_service_does_not_receive_application_credentials(self):
        ollama = COMPOSE.split("  ollama:\n", 1)[1].split("\n  new-api:\n", 1)[0]
        self.assertIn('test: ["CMD", "ollama", "list"]', ollama)
        self.assertNotIn("environment:", ollama)
        for secret_name in (
            "API_TOKEN",
            "OPENPROJECT_API_TOKEN",
            "GLPI_APP_TOKEN",
            "GLPI_USER_TOKEN",
            "NEW_API_KEY",
        ):
            with self.subTest(secret_name=secret_name):
                self.assertNotIn(secret_name, ollama)

    def test_backend_waits_for_ollama_and_receives_ai_endpoint_settings(self):
        backend = COMPOSE.split("  cockpit-backend:\n", 1)[1].split("\nvolumes:\n", 1)[0]
        self.assertIn("condition: service_healthy", backend)
        self.assertIn("IA_DEFAULT_ENDPOINT", backend)
        self.assertIn("IA_ALLOWED_ENDPOINTS", backend)
        self.assertIn("COCKPIT_API_TOKEN", backend)

    def test_backend_mounts_process_data_file(self):
        backend = COMPOSE.split("  cockpit-backend:\n", 1)[1].split("\nvolumes:\n", 1)[0]
        self.assertIn("- ./data:/app/data", backend)
        self.assertIn("COCKPIT_PROCESSOS_FILE=/app/data/processos.json", backend)

    def test_backend_healthcheck_probes_http_liveness(self):
        backend = COMPOSE.split("  cockpit-backend:\n", 1)[1].split("\nvolumes:\n", 1)[0]
        self.assertIn("healthcheck:", backend)
        self.assertIn('http://127.0.0.1:5000/', backend)
        self.assertIn("interval: 30s", backend)
        self.assertIn("start_period: 20s", backend)


if __name__ == "__main__":
    unittest.main()
