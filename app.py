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

# An endpoint that returns the list of all characters


@app.get("/characters")
def get_characters():
    return {"characters": characters}


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

# new chat endpoint
# working beautifully


@app.post("/chat")
async def chat(request: Request):

    # Extract the message input and game cookie from the request JSON
    data = await request.json()
    message = data["text"]
    game_cookie = data["gameCookie"]

    # Handling the 6th or more chat attempt
    if game_cookie["numMessages"] >= max_messages:
        return {
            "message": message,
            "response": "You have reached the maximum number of messages. Please guess who you are talking to.",
            "game_cookie": {
                "num_messages": game_cookie["numMessages"],
                "selected_character": game_cookie["selectedCharacter"]
            },
            "error": "User has sent more than the max number of messages allowed. This won't change until the user resets the game."
        }

    game_cookie["numMessages"] += 1

    prompt_text = f"You are {game_cookie['selectedCharacter']} from the television series \"Game of Thrones\" on HBO. From now on, act as though you are {game_cookie['selectedCharacter']}, and your responses should be as similar to what the real {game_cookie['selectedCharacter']} would say as possible. Stay short and concise. Conversation:\n\nuser: {message}."

    response_text = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_text,
        temperature=0.5,
        max_tokens=70
    )
    response_text = response_text["choices"][0]["text"]
    response_text = response_text[response_text.find(":") + 2:]
    if response_text.find(game_cookie["selectedCharacter"]) != -1:
        response_text = response_text[:response_text.find("\n")]

    return {
        "message": message,
        "response": response_text,
        "game_cookie": {
            "num_messages": game_cookie["numMessages"],
            "selected_character": game_cookie["selectedCharacter"]
        }
    }

#       LISTEN ======= FROM THIS CODE AND BELOW, IT'S THE BUGGY BULLSHIT FROM BEFORE
