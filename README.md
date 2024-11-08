Boutique Break - Fashion Puzzle and Quiz Game

Boutique Break is a fashion-themed puzzle and quiz game built with FastAPI. Players solve a color matching puzzle and answer fashion questions to earn points, with progress tracked and a final score displayed upon completion.

Features:

- Color Matching Puzzle: Match clothing items with their correct color.
- Fashion Quiz: Answer fashion-related questions to earn points.
- Game Progress: Tracks the player's score and shows the completion status.
- Final Score: Displays the final score after completing both puzzles and quizzes.

Technologies:

- Backend: FastAPI
- Frontend: Jinja2 Templates
- Database: In-memory storage for game states

Setup & Installation:

- Clone the repository: 
git clone https://github.com/codefromlani/Boutique_break.git
cd Boutique_break

- Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

- Install the dependencies:
pip install -r requirements.txt

- Run the application:
uvicorn main:app --reload
Open the app in your browser at http://127.0.0.1:8000.

How to Play:

- Start a new game by clicking "Start Your Fashion Adventure!" on the home page.
- Solve the color matching puzzle and then answer the fashion quiz questions.
- Your score will be displayed at the end of the game.

Contributing:

Feel free to fork this project, submit issues, or create pull requests if you have improvements or suggestions!

License:
This project is licensed under the MIT License - see the LICENSE file for details.