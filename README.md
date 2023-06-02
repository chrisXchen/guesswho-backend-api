FOR THE NEW VERSION

AS OF 6/1/23 I GOT THE:
cookie storing and sending working for the selected character and num of messages values.
- this means that I only have the
FRONTEND
- handleRestart
- handleGuessSubmit
- updateGameCookie
- useEffect
functions working. Additionally, they're not particularly nice nor robust nor encompassing many different features. Future features to add/update would be adding a guess counter and adding more information to the cookie such as conversation history
BACKEND
- /change_character POST (json payload of gameCookie) -> returns a new character
    use cases: reseting the game, creating a new game
- /guess POST (json payload of gameCookie and a guess: str) -> returns either an error json or a {correct: bool, message: str} json
    use cases: lettting a user take their guess as to who the mystery person is
    future additions:
        - maybe validating the guess count is below some max guess number
        - having the response be ai generated as well
TOMORROWS GOALS FROM A BIRDS EYE
- get chat feature working in the same way, however chat messages are only stored on the brwoser in the react states (if they reload the page then they lose their previous messages)
- unnecessary for tomorrow but nice:
    - refactor backend (easy)
    - add tests for backend routes (medium)
    - refactor frontend, this means finally making components and pages (hard)

REMEMBER - ONLY THE GUESS AND RESET FEATURES ARE WORKING WITH COOKIE STORAGE FOR THE TIME BEING
