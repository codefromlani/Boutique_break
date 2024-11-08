from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, List, Optional
import json

app = FastAPI(
    title="Boutique Break",
    description="A fashionable escape room adventure",
    version="1.0.0"
)

#Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Game state storage
class GameState:
    def __init__(self):
        self.score: int = 0
        self.completed_puzzles: List[str] = []
        self.current_puzzle: str = "color"
        self.quiz_progress: int = 0

# Simple in-memory storage for game states
game_states: Dict[str, GameState] = {}

# Basic game configuration
COLOR_PUZZLES = {
    "color_matching": {
        "choices": [
            {"id": 1, "color": "pink", "name": "Pink Dress"},
            {"id": 2, "color": "blue", "name": "Blue Skirt"},
            {"id": 3, "color": "purple", "name": "Purple Blouse"}
        ],
        "correct_answer": "pink",
        "points": 25
    }
}

QUIZ_QUESTIONS = [
    {
        "question": "Which season is typically associated with pastel colors?",
        "options": ["Spring", "Summer", "Fall", "Winter"],
        "correct": "Spring",
        "points": 25
    },
    {
        "question": "What is the classic 'little black dress' often abbreviated as?",
        "options": ["LBD", "CBD", "BBD", "DBD"],
        "correct": "LBD",
        "points": 25
    },
    {
        "question": "Which fabric is known for its luxurious smoothness and shine?",
        "options": ["Cotton", "Silk", "Polyester", "Wool"],
        "correct": "Silk",
        "points": 25
    }
]

# Request models
class ColorAnswer(BaseModel):
    chosen_color: str

class QuizAnswer(BaseModel):
    answer: str

class GameCompletion(BaseModel):
    final_score: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Display the welcome page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/game/start")
async def start_game():
    """Initialize a new game"""
    game_id = len(game_states) + 1
    game_states[game_id] = GameState()
    return {"game_id": game_id, "message": "Game started!"}

@app.get("/puzzle/color/{game_id}", response_class=HTMLResponse)
async def show_color_puzzle(request: Request, game_id: int):
    """Show the color matching puzzle"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return templates.TemplateResponse(
        "color_puzzle.html",
        {
            "request": request,
            "puzzle": COLOR_PUZZLES["color_matching"],
            "game_id": game_id,
            "current_score": game_states[game_id].score
        }
    )

@app.post("/puzzle/color/{game_id}/check")
async def check_color_answer(game_id: int, answer: ColorAnswer):
    """Check if the chosen color is correct"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_states[game_id]
    is_correct = answer.chosen_color == COLOR_PUZZLES["color_matching"]["correct_answer"]
    
    if is_correct and "color" not in game.completed_puzzles:
        game.score += COLOR_PUZZLES["color_matching"]["points"]
        game.completed_puzzles.append("color")
        game.current_puzzle = "quiz"
    
    return {
        "correct": is_correct,
        "message": "Perfect match!" if is_correct else "Not quite right. Try again!",
        "score": game.score
    }

@app.get("/quiz/{game_id}", response_class=HTMLResponse)
async def fashion_quiz(request: Request, game_id: int):
    """Display the fashion quiz"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_states[game_id]
    if "color" not in game.completed_puzzles:
        return RedirectResponse(url=f"/puzzle/color/{game_id}")
    
    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "game_id": game_id,
            "current_score": game.score,
            "questions": QUIZ_QUESTIONS  # Make sure this is passed to the template
        }
    )

@app.post("/quiz/{game_id}/answer")
async def check_quiz_answer(game_id: int, answer: QuizAnswer):
    """Check quiz answer and update score"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_states[game_id]

    # Check if quiz_progress is valid (within bounds of QUIZ_QUESTIONS)
    if game.quiz_progress >= len(QUIZ_QUESTIONS):
        raise HTTPException(status_code=400, detail="Quiz is already complete or progress is out of range")
    
    current_question = QUIZ_QUESTIONS[game.quiz_progress]
    is_correct = answer.answer == current_question["correct"]
    
    if is_correct:
        game.score += current_question["points"]
    
    game.quiz_progress += 1
    is_complete = game.quiz_progress >= len(QUIZ_QUESTIONS)
    
    if is_complete:
        game.completed_puzzles.append("quiz")
    
    return JSONResponse(content={
        "correct": is_correct,
        "score": game.score,
        "is_complete": is_complete,
        "message": "Correct!" if is_correct else f"Incorrect. The right answer was: {current_question['correct']}"
    })

@app.get("/complete/{game_id}", response_class=HTMLResponse)
async def show_completion(request: Request, game_id: int):
    """Show the completion screen"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_states[game_id]
    return templates.TemplateResponse(
        "complete.html",
        {
            "request": request,
            "final_score": game.score,
            "max_score": COLOR_PUZZLES["color_matching"]["points"] + sum(q["points"] for q in QUIZ_QUESTIONS)
        }
    )

@app.post("/game/{game_id}/complete")
async def complete_game(game_id: int, completion: GameCompletion):
    """Handle game completion"""
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_states[game_id]
    if len(game.completed_puzzles) < 2:
        raise HTTPException(status_code=400, detail="All puzzles must be completed")
    
    return {
        "message": "Game completed successfully!",
        "final_score": game.score
    }