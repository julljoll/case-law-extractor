"""
Unit tests for TSJScheduler auto-updater module in Case Law Extractor powered by sha256.us.
"""

import unittest
from src.scheduler import TSJScheduler


class TestTSJScheduler(unittest.TestCase):
    """Test suite for TSJScheduler background auto-updater."""

    def setUp(self):
        self.scheduler = TSJScheduler(interval_seconds=3600)

    def tearDown(self):
        if self.scheduler.is_running():
            self.scheduler.stop()

    def test_scheduler_initial_state(self):
        """Tests that scheduler starts in inactive state."""
        self.assertFalse(self.scheduler.is_running())
        info = self.scheduler.get_info()
        self.assertFalse(info["activo"])
        self.assertEqual(info["intervalo_horas"], 1.0)

    def test_scheduler_start_stop(self):
        """Tests starting and stopping background scheduler thread."""
        self.scheduler.start()
        self.assertTrue(self.scheduler.is_running())
        info = self.scheduler.get_info()
        self.assertTrue(info["activo"])
        
        self.scheduler.stop()
        self.assertFalse(self.scheduler.is_running())

    def test_force_update_mock(self):
        """Tests force_update returns metadata dictionary."""
        info = self.scheduler.get_info()
        self.assertIn("estado", info)
        self.assertIn("ultima_ejecucion", info)


if __name__ == "__main__":
    unittest.main()
