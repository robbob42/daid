# Welcome to DAID! 
# A tabletop simulator game that uses AI as the Dungeon Master

## Setup
Setup of DAID requires getting the Python websocket server running, and installing the Chrome extension locally in your browser

### Setting up the Python websocket server
Prerequisites:
- Pipenv

Steps:
- Navigate to /server: `cd server`
- Install pipenv dependendencies: `pipenv sync`
- Start pipenv virtual environment: `pipenv shell`
- Start python websocket server: `python shell`

### Installing the extension in Chrome
Steps:
- From the Chrome menu, open Extensions -> Manage Extensions
- In the top right, make sure that `Developer Mode` is turned on
- In the top left, press the `Load unpacked` button
- Select the `gemini-agent-extension` folder

### Playing a game
- In Chrome, navigate to [Gemini](https://gemini.google.com/)
- A popup menu is displayed, asking if this tab will be part of the DAID setup.  Select `Dungeon Master` to act as the primary controller of all the other tabs
- The Dungeon Master is registered with the websocket, and a large text is automatically sent to teach the Dungeon Master how to complete its role.  This step is complete when Gemini responds with "Shall we play a game?"
- Open a new tab and navigate to [Gemini](https://gemini.google.com/)
- Select `Hero Creator` from the popup
- Similar to the Dungeon Master, the Hero Creator is registered with the websocket and is taught how to complete its role.
- Back on the Dungeon Master tab, repond that you would love to play a game
- The Dungeon Master will ask the user for some directions on setting up the players.  Respond appropriately.
- The Dungeon Master should generate a special box with the title `JSON`.  This is how the Dungeon Master requests information from one of the other Assistants.  Press the `Copy` button in the top right to copy the text to your clipboard, and then press the `Send Message` button in the bottom right.
- The code will be automatically sent to the appropriate tab.  In this case, it will go to the Hero Creator tab.  You can verify this by going to that tab and seeing Gemini's response being printed.  Once the response is complete, it should also be in a `JSON` box.  Again, press the `Copy` button and then `Send Message`.

