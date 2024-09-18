from unittest import TestCase
from app import app
from flask import session
from boggle import Boggle

class FlaskTests(TestCase):

    def setUp(self):
        """Set up test client and configurations."""
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_new_game(self):
        """Test if the new game route generates a new board and renders correctly."""
        with self.client:
            res = self.client.get("/new-game")
            self.assertEqual(res.status_code, 200)
            self.assertIn('board', session)  # Test if board is saved in the session
            self.assertIn(b'<div id="boggle-board">', res.data)

    def test_check_word_valid(self):
        """Test if the check-word route properly validates a word."""
        with self.client as client:
            client.get("/new-game")  # First create a new game to have a board in the session
            with client.session_transaction() as sess:
                sess['board'] = [["C", "A", "T", "S", "P"],
                                 ["A", "N", "I", "M", "L"],
                                 ["B", "O", "G", "T", "H"],
                                 ["E", "R", "D", "O", "G"],
                                 ["M", "P", "U", "S", "E"]]
            res = client.post("/check-word", json={'word': 'CAT'})
            self.assertEqual(res.json['result'], 'ok')

    def test_check_word_not_on_board(self):
        """Test if check-word returns 'not-on-board' for words not on the board."""
        with self.client as client:
            client.get("/new-game")
            with client.session_transaction() as sess:
                sess['board'] = [["C", "A", "T", "S", "P"],
                                 ["A", "N", "I", "M", "L"],
                                 ["B", "O", "G", "T", "H"],
                                 ["E", "R", "D", "O", "G"],
                                 ["M", "P", "U", "S", "E"]]
            res = client.post("/check-word", json={'word': 'DOGS'})
            self.assertEqual(res.json['result'], 'not-on-board')

    def test_check_word_not_in_dictionary(self):
        """Test if check-word returns 'not-word' for words that are not valid in the dictionary."""
        with self.client as client:
            client.get("/new-game")
            with client.session_transaction() as sess:
                sess['board'] = [["C", "A", "T", "S", "P"],
                                 ["A", "N", "I", "M", "L"],
                                 ["B", "O", "G", "T", "H"],
                                 ["E", "R", "D", "O", "G"],
                                 ["M", "P", "U", "S", "E"]]
            res = client.post("/check-word", json={'word': 'XYZ'})
            self.assertEqual(res.json['result'], 'not-word')

    def test_score_calculation(self):
        """Test if the score route calculates score based on the word length."""
        with self.client:
            res = self.client.post("/score", json={"words": ["CAT", "DOGS"]})
            self.assertEqual(res.json['score'], 7)  # 3 letters for "CAT" + 4 letters for "DOGS"

    def test_post_score(self):
        """Test if the post-score route updates games played and high score."""
        with self.client as client:
            # Initialize the session
            client.get("/new-game")

            # Post a score and check the response
            res = client.post("/post-score", json={"score": 10})
            data = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["games_played"], 1)
            self.assertEqual(data["high_score"], 10)

            # Post another score and check if high score updates
            res = client.post("/post-score", json={"score": 15})
            data = res.get_json()

            self.assertEqual(data["games_played"], 2)
            self.assertEqual(data["high_score"], 15)

            # Post a lower score and ensure high score remains the same
            res = client.post("/post-score", json={"score": 5})
            data = res.get_json()

            self.assertEqual(data["games_played"], 3)
            self.assertEqual(data["high_score"], 15)  # High score should still be 15



