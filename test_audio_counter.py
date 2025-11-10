import unittest
from unittest.mock import Mock
from src.Audio_Counter import AudioCounter

class TestAudioCounter(unittest.TestCase):
    def setUp(self):
        self.mock_socketio = Mock()
        self.counter = AudioCounter(self.mock_socketio)

    def test_get_similarity(self):
        self.assertAlmostEqual(self.counter.get_similarity("hello", "hello"), 1.0)
        self.assertLess(self.counter.get_similarity("hello", "world"), 0.5)

if __name__ == '__main__':
    unittest.main()
