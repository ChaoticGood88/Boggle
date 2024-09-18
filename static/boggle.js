class BoggleGame {
    constructor() {
        this.score = 0;
        this.timeLeft = 60;
        this.words = new Set();  // Store valid words to avoid duplicates
        this.timerId = null;
        
        // Initialize the game
        this.startTimer();
        this.handleFormSubmission();
    }

    // Start the countdown timer
    startTimer() {
        this.timerId = setInterval(() => {
            this.timeLeft--;
            $("#timer").text(`Time Left: ${this.timeLeft}s`);

            if (this.timeLeft <= 0) {
                clearInterval(this.timerId);
                this.endGame();
            }
        }, 1000);
    }

    // Handle form submission for word guessing
    handleFormSubmission() {
        $("#guess-form").on("submit", async (evt) => {
            evt.preventDefault();

            if (this.timeLeft <= 0) return;  // Don't allow guesses after time is up

            const guess = $("#guess").val().toLowerCase();  // Normalize word to lowercase

            // Check for duplicate words
            if (this.words.has(guess)) {
                $("#result").text("You already guessed that word!");
                return;
            }

            try {
                const res = await axios.post("/check-word", { word: guess });
                
                if (res.data.result === "ok") {
                    $("#result").text("Word is valid!");
                    this.words.add(guess);  // Add word to the set to prevent duplicates
                    this.updateScore(guess);
                } else if (res.data.result === "not-on-board") {
                    $("#result").text("Word is not on the board!");
                } else {
                    $("#result").text("Not a valid word!");
                }
            } catch (err) {
                console.error("Error checking word", err);
            }

            $("#guess").val("");  // Clear the input field
        });
    }

    // Update the score
    updateScore(word) {
        this.score += word.length;
        $("#score").text(this.score);
    }

    // End the game when time runs out
    async endGame() {
        $("#result").text("Time's up! No more guesses allowed.");
        $("#guess-form :input").prop("disabled", true);  // Disable the form

        try {
            const res = await axios.post("/post-score", { score: this.score });
            $("#stats").html(`Games Played: ${res.data.games_played} | Highest Score: ${res.data.high_score}`);
        } catch (err) {
            console.error("Error posting score", err);
        }
    }
}

// Initialize the Boggle game when the page loads
$(document).ready(function() {
    new BoggleGame();
});
