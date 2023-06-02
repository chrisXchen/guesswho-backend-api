import random
import openai
import json
from typing import List

from fastapi import FastAPI, Request, HTTPException, Response
from pydantic import BaseModel, BaseSettings

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


class Settings(BaseSettings):
    app_name: str = "Guesswho API"
    OPENAI_API_KEY: str
    SESSION_SECRET: str


settings = Settings()

app = FastAPI()


# Use the OpenAI API to send prompts to a GPT-3 model
# and receive responses
openai.api_key = settings.OPENAI_API_KEY


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware,
                   secret_key=settings.SESSION_SECRET)


# A class that defines the data model for a chat message
class ChatMessage(BaseModel):
    text: str

# A class that defines the data model for the user's guess of who they are talking to


class CharacterGuess(BaseModel):
    character: str


# Maximum allowed messages
max_messages = 5

# List of 11 possible Harry Potter characters
characters = ["Sansa Stark", "Brienne of Tarth", "Cersei Lannister",
              "Arya Stark", "Olenna Tyrell", "Daenerys Targaryen",
              "Theon Greyjoy", "Littlefinger", "Tyrion Lannister",
              "Jon Snow", "Jamie Lannister", "Robb Stark", "Ned Stark",
              "The Hound", "Catelyn Stark", "Ramsey Bolton", "Samwell Tarly",
              "Bran Stark"]

# this endpoint picks a random character thats not the one already in the game cookie
# AND this endpoint is hit when trying to restart
@app.post("/change_character")
async def change_character(request: Request):
    # Get the current character from the request
    current_character = (await request.json())["gameCookie"]["selectedCharacter"]

    # Make a copy of the characters list and remove the current character from it
    new_character_choices = [
        character for character in characters if character != current_character]

    # Select a new character
    new_character = random.choice(new_character_choices)

    return {"character": new_character}

# new guess endpoint
@app.post("/guess")
async def guess(request: Request):

    # Extract the guess and game cookie from the request JSON
    data = await request.json()
    guess = data["guess"]
    game_cookie = data["gameCookie"]

    if "selectedCharacter" not in game_cookie:
        return {"error": "No character selected in game"}

    if guess == game_cookie["selectedCharacter"]:
        # Use the OpenAI API to generate a cheeky but honest response
        # if the user's guess is correct
        response_text = f"Yes, great job! I am {guess}. You win!"
        return {"correct": True, "response": response_text}
    else:
        # Use the OpenAI API to generate a cheeky but honest response
        # if the user's guess is incorrect
        response_text = f"No! I'm not {guess}."
        return {"correct": False, "response": response_text}


#       LISTEN ======= FROM THIS CODE AND BELOW, IT'S THE BUGGY BULLSHIT FROM BEFORE

"""
an endpoint that returns either an existing cookie or creates and sets one
"""


@app.get("/start_game")
def start_game(request: Request, response: Response):
    # Check if the cookie exists
    if "game_cookie" in request.cookies:
        game_cookie_value = json.loads(request.cookies["game_cookie"])
        # Return the game parameters if the cookie exists
        return {"game_parameters": game_cookie_value}
    else:
        game_cookie_value = {
            "num_messages": 0,
            "selected_character": random.choice(characters)
        }
        response.set_cookie(key="game_cookie",
                            value=json.dumps(game_cookie_value))
        # Return the new game parameters
        return {"game_parameters": game_cookie_value}


@app.get("/selected_character")
def get_selected_character(request: Request):
    session = request.session
    if "selected_character" not in session:
        session["selected_character"] = random.choice(characters)
    return {"selected_character": session["selected_character"]}


# An endpoint that returns the list of all characters
@app.get("/characters")
def get_characters():
    return {"characters": characters}


# An endpoint that returns the max number of messages:
@app.get("/message_nums")
def get_message_nums(request: Request):
    session = request.session
    if "num_messages" not in session:
        session["num_messages"] = 0
    return {
        "max_messages": max_messages,
        "current_messages": session["num_messages"]
    }


"""
an endpoint to handle chat messages and updating the game cookies accordingly
"""


@app.post("/chat")
async def chat(request: Request, response: Response):
    if "game_cookie" in request.cookies:
        game_cookie_value = json.loads(request.cookies["game_cookie"])
    else:
        game_cookie_value = {
            "num_messages": 0,
            "selected_character": random.choice(characters)
        }

    message = ChatMessage(**await request.json())
    game_cookie_value["num_messages"] += 1

    if game_cookie_value["num_messages"] > max_messages:
        return {"error": "You have reached the maximum number of messages. Please guess who you are talking to."}

    input_text = f"You are {game_cookie_value['selected_character']} from the television series \"Game of Thrones\" on HBO. From now on, act as though you are {game_cookie_value['selected_character']}, your answers should match what they would say. Stay short and concise. Conversation:\n\nuser: {message.text}."

    response_text = openai.Completion.create(
        model="text-davinci-003",
        prompt=input_text,
        temperature=0.5,
        max_tokens=50
    )

    response_text = response_text["choices"][0]["text"]
    response_text = response_text[response_text.find(":") + 2:]
    if response_text.find(game_cookie_value["selected_character"]) != -1:
        response_text = response_text[:response_text.find("\n")]

    response.set_cookie(key="game_cookie", value=json.dumps(game_cookie_value))

    # Return the message and the model's response to the user
    return {"message": message, "response": response_text}

'''
# An endpoint that accepts the user's guess of who they are talking to
@app.post("/guess")
def guess(request: Request, guess: CharacterGuess):
    session = request.session
    if "selected_character" not in session:
        session["selected_character"] = random.choice(characters)

    # Check if the user's guess is correct
    if guess.character == session["selected_character"]:
        # Use the OpenAI API to generate a cheeky but honest response
        # if the user's guess is correct
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"user:##break. Are you impersonating {guess.character}?",
            temperature=0.5,
            max_tokens=100,
        )
        tmp = session["selected_character"]
        response_text = f"Yes, great job! I am {tmp}."
        return {"correct": True, "response": response_text}
    else:
        # Use the OpenAI API to generate a cheeky but honest response
        # if the user's guess is incorrect
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"user: Are you {guess.character}?",
            temperature=0.5,
            max_tokens=100,
        )
        response_text = response["choices"][0]["text"]
        return {"correct": False, "response": response_text}
'''

# An endpoint that resets the number of messages sent back to 0 and selects another random character


@app.post("/reset")
def reset(request: Request):
    session = request.session
    session["num_messages"] = 0
    session["selected_character"] = random.choice(characters)
    return {"message": "Number of messages and selected character have been reset."}
