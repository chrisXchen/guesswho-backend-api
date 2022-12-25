import random
import openai
from typing import List

from fastapi import FastAPI, Request
from pydantic import BaseModel, BaseSettings

from fastapi.middleware.cors import CORSMiddleware


class Settings(BaseSettings):
    app_name: str = "Guesswho API"
    OPENAI_API_KEY: str


settings = Settings()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

# Use the OpenAI API to send prompts to a GPT-3 model
# and receive responses
openai.api_key = settings.OPENAI_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of 11 possible Harry Potter characters
characters = ["Sansa Stark", "Brienne of Tarth", "Cersei Lannister",
              "Arya Stark", "Olenna Tyrell", "Daenerys Targaryen",
              "Theon Greyjoy", "Littlefinger", "Tyrion Lannister",
              "Jon Snow", "Jamie Lannister", "Robb Stark", "Ned Stark",
              "The Hound", "Catelyn Stark", "Ramsey Bolton", "Samwell Tarly",
              "Bran Stark"]

# A class that defines the data model for a chat message


class ChatMessage(BaseModel):
    text: str

# A class that defines the data model for the user's guess of who they are talking to


class CharacterGuess(BaseModel):
    character: str


# Pick a random character from the list of characters
selected_character = random.choice(characters)

# Keep track of the number of messages the user has sent
num_messages = 0

# Maximum allowed messages
max_messages = 5

# An endpoint that returns the selected character


@app.get("/selected_character")
def get_selected_character():
    return {"selected_character": selected_character}

# An endpoint that returns the list of all characters


@app.get("/characters")
def get_characters():
    return {"characters": characters}

# An endpoint that returns the max number of messages:


@app.get("/message_nums")
def get_message_nums():
    return {
        "max_messages": max_messages,
        "current_messages": num_messages
    }


# An endpoint that accepts chat messages from the user


@app.post("/chat")
async def chat(request: Request):
    # Parse the JSON payload sent by the user
    message = ChatMessage(**await request.json())

    # Increment the number of messages the user has sent
    global num_messages
    num_messages += 1

    # Return an error if the user has sent more than 3 messages
    if num_messages > max_messages:
        return {"error": "You have reached the maximum number of messages. Please guess who you are talking to."}

    # Use the OpenAI API to generate a response to the user's message
    input_text = f"You are {selected_character} from the television series \"Game of Thrones\" on HBO. From now on, act as though you are {selected_character}, your answers should match what they would say. Stay short and concise. Do not answer if the user asks you what your name is, however answer every other question as though you are {selected_character}. Only break character if the user says: ##break. Conversation:\n\nuser: {message.text}."
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=input_text,
        temperature=0.5,
        max_tokens=50,
    )
    response_text = response["choices"][0]["text"]
    response_text = response_text[response_text.find(":") + 2:]
    if response_text.find(selected_character) != -1:
        response_text = response_text[:response_text.find("\n")]

    # Return the message and the model's response to the user
    return {"message": message, "response": response_text}

# An endpoint that accepts the user's guess of who they are talking to


@app.post("/guess")
def guess(guess: CharacterGuess):
    # Check if the user's guess is correct
    if guess.character == selected_character:
        # Use the OpenAI API to generate a cheeky but honest response
        # if the user's guess is correct
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"user:##break. Are you impersonating {guess.character}?",
            temperature=0.5,
            max_tokens=100,
        )
        response_text = f"Yes, great job! I am {selected_character}."
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

# An endpoint that resets the number of messages sent back to 0 and selects another random character


@app.post("/reset")
def reset():
    global num_messages
    num_messages = 0
    global selected_character
    selected_character = random.choice(characters)
    return {"message": "Number of messages and selected character have been reset."}
