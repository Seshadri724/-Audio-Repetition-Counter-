import unittest
from src.Audio_Counter import AudioCounter

class TestAudioCounter(unittest.TestCase):
    def setUp(self):
        self.counter = AudioCounter()

    def test_get_similarity(self):
        self.assertAlmostEqual(self.counter.get_similarity("hello", "hello"), 1.0)
        self.assertLess(self.counter.get_similarity("hello", "world"), 0.5)

if __name__ == '__main__':
    unittest.main()
