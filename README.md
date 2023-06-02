# guesswho-backend-api

###### an api that handles the routing and communication between the guesswho-frontend-app and a generative LLM

### Short term goals (FROM A BIRDS EYE)

- [x] get chat feature working in the same way, however chat messages are only stored on the brwoser in the react states (if they reload the page then they lose their previous messages)
- [ ] refactor backend (easy)
- [ ] add tests for backend routes (medium)
- [ ] refactor frontend, this means finally making components and pages (hard)

### Medium term goals (features I want to get out soon)
- [ ] encrypt mystery character name in the cookie, and decrypt key is only available server side
- [ ] add more characters and bundle them (this will require a relational db)
    - Storing their:
        + character name
        + character genre
        + character media (literature, television, movie, etc.)
        + character book name (tv series, or movie name)
        + basic character facts (race, height, weight, sex, occupation, age, hometown, birth date, birth time, current location, parents:{}, etc.)
        + some random quotes that capture how they sound and what tone they use
        + a picture or gif link
    - Use case:
        1. a mystery character exists; I know who it is but the user does not
        2. the user sends a chat message to find out some info about them
        3. I run a sql query to get the mystery character's entire row and data
        4. I format and stuff the information from that sql query into a prompt
        5. I send the prompt to OpenAI and get back the response
    - Note:
        + This will obviously be more expensive simply because I'm stuffing so much more info in each prompt, but it should be manageable
        + This is the easiest solution; I can probably implement a starter version of this in less than a day
        + The hardest part of this is gathering the character information and sorting it then upserting it
            * Should this be done on bulk? Should I be doing it manually? How many characters am I actually expecting this game to have?

### Long term goals
- [ ] store characters and their biographies, histories, and maybe stories, into vector databases (hard)
- [ ] store conversations in cookies (medium)
- [ ] add rate limiting (hard)
- [ ] integrate langchain (maybe - easy)
