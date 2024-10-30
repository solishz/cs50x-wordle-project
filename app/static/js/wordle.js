// Logic of the wordle game

// global vaiables
let currentRow = 1;
const maxRows = 6;
const maxCols = 5;


// Add an event listener to all the keyboard keys
document.querySelectorAll(".keyboard-key").forEach(key => {
    key.addEventListener("click", key_press);
});

// Handle key press
function key_press(e){
    // Get the key that is pressed
    const key = e.target.innerHTML;
    const row = document.querySelectorAll(`.row${currentRow}`);
    if (key == "Enter") {
        // Check if the row is fully filled before submitting
        if (isRowComplete(row)) {
            const word = getWordFromRow(row);
            // Submit the word
            submitWord(word);

            // Proceed to the next row if current row < maxRows
            if (currentRow <= maxRows) {
                currentRow++;
            }
        } else {
            alert("Please fill in all tiles before submitting.");
        }
    }
    else if (key == "⌫") {
        // Remove the last inserted key in current row
        const filledTiles = document.querySelectorAll(`.row${currentRow}:not(:empty)`);
        const lastFilledTile = filledTiles[filledTiles.length - 1];
        if (lastFilledTile) {
            lastFilledTile.innerHTML = "";
        }
    }
    else {
        updateGrid(key, row);
    }
}

// Update the next empty spot in the current row
function updateGrid(key, row) {
    for (let tile of row) {
        if (tile.innerHTML === "") {
            tile.innerHTML = key;
            break;
        }
    }
}

// Check if the row is completely filled
function isRowComplete(row) {
    for (let tile of row) {
        if (tile.innerHTML === "") {
            // There's an empty tile
            return false; 
        }
    }
    // All tiles are filled
    return true; 
}

// Gather the word from the row
function getWordFromRow(row) {
    let word = "";
    for (let tile of row) {
        word += tile.innerHTML;
    }
    return word;
}

// Submit the word (handle this function according to your needs)
function submitWord(word) {
    console.log("Submitting word:", word);
    // Use Fetch API to submit the word
    fetch('/submit-word', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ word: word , score: currentRow})
    })
    // Parse JSON response
    .then(response => response.json()) 
    .then(data => {
        console.log("Server response:", data);
        // Handle the server response (e.g., show success or failure)
        if (data.feedback) {
            showFeedback(data.feedback);
        }
        else 
        {
            currentRow--;
            setTimeout(() => {
                alert(`${word} is not a word`);
            }, 100);
        }   
        
        if (data.result === "correct") {
            setTimeout(() => {
                if (confirm(`Congratulations!\nYou got ${data.score} Scores\nPress Ok to restart:`) == true) {
                    // Reload the page
                    location.reload();
                    // # TODO: Show a modal with the aquired score
                }
                else {
                    // Reload the page
                    location.reload();
                }
            }, 100);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}


function showFeedback(list) {
    const row = document.querySelectorAll(`.row${currentRow - 1}`);
    for (let i = 0; i < 6; i++) {
        // Check if row[i] exists
        if (row[i]) {  
            if (list[i] === "+") {
                // Correct letter
                row[i].classList.add("correct"); 
            } else if (list[i] === "-") {
                // Close letter
                row[i].classList.add("close");    
            } else {
                // Incorrect letter
                row[i].classList.add("incorrect");
                // Disable the incorrect keyboard key
                letter = row[i].innerHTML;
                keys = document.querySelectorAll(".keyboard-key");
                for (key of keys) {
                    if (key.innerHTML == letter) {
                        key.disabled = true;
                        key.classList.add("disabled");
                    }
                }
            }
        }
    }
}


