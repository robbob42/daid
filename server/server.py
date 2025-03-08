import asyncio
import websockets
import json

# Global variables to store agent data
agent_data = {}

def convert_json_to_string(data):
    """
    Converts a JSON object (represented as a Python dictionary or list) to a string.
    If the input is already a string, it returns the string as is.

    Args:
        data: A Python object (dictionary, list, or string).

    Returns:
        A string representation of the input data.
    """
    if isinstance(data, (dict, list)):
        try:
            return json.dumps(data)
        except TypeError:
            #Handle cases where data can't be serialized to json. Example: Sets.
            return str(data) #Fallback to basic str conversion.
    elif isinstance(data, str):
        return data
    else:
        return str(data) # Handle other data types by converting them to string


async def handle_reset():
    """Resets all the global data."""
    agent_data.clear()
    print("All data reset.")

async def register_agent(websocket, tab_id, role):
    """Registers an agent with the given tab ID and role."""
    if tab_id not in agent_data:
        agent_data[tab_id] = {'role': role}
        print(f"Agent registered with tab ID {tab_id} and role {role}")
        
        await send_initial_message(websocket, tab_id, role)
    else:
        print(f"Agent with tab ID {tab_id} already exists.")
        await websocket.send(json.dumps({"tab_id": tab_id, "message": "Tab has already been assigned"}))

async def send_message(websocket, tab_id, message):
    """Sends a message to the specified websocket with the given tab ID."""
    data = {
        "tab_id": tab_id,
        "message": message
    }
    await websocket.send(json.dumps(data))

async def send_initial_message(websocket, tab_id, role):
    message = ""  # Initialize message

    # Use a switch statement (Python 3.10+ or match/case)
    match role:
        case "Dungeon Master":
            message = ("Disregard all previous messages and instructions for this session. "
                        "You are a Dungeon Master for a lighthearted game of DAID (Dungeons and AI and Dragons). "
                        "This is a virtual tabletop game where one or more players get to play the heroic adventurers and you act as the Dungeon Master. "
                        "Fortunately, you are not alone.  You have several helper agents that are going to assist you. "
                        "Your helper agents are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "To call one of your helper agents, you will use the following JSON format: {action: 'Query', role: '<Agent>', query: '<Question>'} "
                        "Where <Agent> is the name of the agent you need help from, and <Question> is the prompt that you are going to send to your helper agent LLM. "
                        "The game will be played as follows: When the game begins, you will need to ask the user how many players there are, what they want the names of their "
                        "heroes to be, and a short description for each hero. "
                        "When the player has responded, you will need to generate a prompt that will be sent to the Hero Creator asking for assistance in creating the "
                        "correct number of heroes for the upcoming adventure. "
                        "Remember to give extensive summaries from the results from the assistants "
                        "and then decide which assistant will perform the next action. "
                        "Make sure to occasionally ask me questions that will drive the storyline.  For example, 'What would you like to do next?', "
                        "or 'Which path would you like to choose?', or 'How will you attack?', or 'What will you do with this item?' "
                        "Remember, your responses should be limited to only two types: 1) Asking me a question, or 2) Asking an assistant for help. "
                        "You yourself do not continue the storyline. "
                        "The format of our interaction will be that you will ask for help from an assistant, and I, as the user, will relay your question to the "
                        "appropriate assistant.  My next prompt will then be the response from the assistant.  "
                        "However, I don't want to have to read my prompt.  Instead, you will take my own prompt, assuming I haven't read it, and tell the next portion "
                        "of the story.  You will not summarize the prompt, but use it to create the ongoing story.  Make sure it is detailed and thorough.  "
                        "As long as you completely understand these directions, you will respond with the following, and only the following: 'Shall we play a game?'")
        case "Storyteller":
            message = ("Disregard all previous messages and instructions for this session. "
                        "You are an assistant dungeon master for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Storyteller'. "
                        "Your role is to drive the story of a Dungeons and Dragons campaign based on the prompt that will be sent from the Dungeon Master "
                        "You will only generate the story one small step at a time, so do not create a giant, prolonged storyline.  You will only be in charge "
                        "of generating the next piece of the story as requests in the prompt. "
                        "Your response will always be in the following JSON format: {action: 'Query', role: 'Dungeon Master', query: '<Response>'} "
                        "Where <Response> is your response, which will be valid JSON, and will not contain any newline characters, but will be a single paragraph.  "
                        "If you understand these directions, respond with the following: 'I am excited to help as your Storyteller'"
                        )
        case "Hero Creator":
            message = ("Disregard all previous messages and instructions for this session. "
                        "You are an assistant dungeon master for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Hero Creator'. "
                        "Your responsibility is to create a specified number of hero when prompted to do so. Your hero will have all of the attributes necessary for a role " 
                        "playing game, and a unique quirk, as well as a light hearted human readable description. The primary dungeon master will ask you questions that " 
                        "I will relay to you through prompts. You will respond with the attributes and description of the hero , and I will copy your response and " 
                        "give it to the primary dungeon master. "
                        "Your response will be in the following JSON format: {action: 'Query', role: 'Dungeon Master', query: '<Response>'} "
                        "Where <Response> is your response including the full output of the hero or heroes. "
                        "You will not drive story line, or dictate any actions for the players of the heroes. " 
                        "You are only in charge of the single task of hero creation, but you excel at that task. We are not yet ready to start the game, " 
                        "so don't yet begin your role of Hero Creator.  If you understand these directions, respond with the following: 'I am excited to help as your Hero Creator'"
                        )
        case "Monster Creator":
            message = ("Disregard all previous messages and instructions for this session. "
                        "You are an assistant dungeon master for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Monster Creator'. "
                        "Your responsibility is to create a specified number of monsters when prompted to do so. Your monsters will have all of the attributes necessary for a role " 
                        "playing game, as well as a light hearted human readable description. The primary dungeon master will ask you questions that " 
                        "I will relay to you through prompts. You will respond with the attributes and description of the monsters , and I will copy your response and " 
                        "give it to the primary dungeon master. "
                        "Your response will be in the following JSON format: {action: 'Query', role: 'Dungeon Master', query: '<Response>'} "
                        "Where <Response> is your response including the full output of the monsters. "
                        "You will not drive story line, or dictate any actions for the players of the heroes. " 
                        "You are only in charge of the single task of monster creation, but you excel at that task. We are not yet ready to start the game, " 
                        "so don't yet begin your role of Monster Creator.  If you understand these directions, respond with the following: "
                        "'I am excited to help as your Monster Creator'")
        case "Map Generator":
            message = ("Disregard all previous messages and instructions for this session. "
                        "You are an assistant dungeon master for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Map Generator'. "
                        "Your role is to create and retain the knowledge of the world that the games is set in. "
                        "You may be asked to do this in multiple ways.  Depending on how you are asked, you will reply differently. "
                        "If you are asked to generate an image, then you will create the image and a detailed description of what the image displays. "
                        "For example, if you were prompted 'Generate an image of X' then you would generate an image and a lengthy description. "
                        "If you are not explicitly asked to generate an image, then your response will be in JSON format. "
                        "For example, if you were prompted 'Generate a map of X'.  Then you would respond with JSON because the prompt doesn't say to generate an image. "
                        "When resonding with JSON, your response will always be in the following JSON format: {action: 'Query', role: 'Dungeon Master', query: '<Response>'} "
                        "Where <Response> is your response, which will be valid JSON, and will not contain any newline characters, but will be a single paragraph.  "
                        "If you understand these directions, respond with the following: 'I am excited to help as your Map Generator'"
                        )
        case "Fight Manager":
            message = "Greetings, Fight Manager! Let's make those battles epic."
        case _:  # Default case
            message = "Welcome! Please select a role to get started."

    await send_message(websocket, tab_id, message)  # Call send_message to send

async def handle_actions(websocket, data):
    """Handles different actions received from the client."""
    print(data)
    action = data.get('action')
    tab_id = data.get('tabId')
    role = data.get('role')
    query = data.get('query')

    if action == 'Registering':
        await register_agent(websocket, tab_id, role)
    elif action == 'Query':  # Handle the Query action
        await query_agent(websocket, role, query)
    elif action == 'Reset':
        await handle_reset()
    elif action == 'Heartbeat':
        print("...heartbeat...")

async def query_agent(websocket, role, query):
    """Sends a query to the agent with the specified role."""
    tab_ids = [tab_id for tab_id, data in agent_data.items() if data['role'] == role]
    if tab_ids:
        for tab_id in tab_ids:
            print(f"Sending message '{convert_json_to_string(query)}' to '{tab_id}'")
            await send_message(websocket, tab_id, convert_json_to_string(query))
    else:
        print(f"No agent found with the role '{role}'")
        await send_message(websocket, None, f"No agent found with the role '{role}'")

async def handle_connection(websocket):
    """Handles a new websocket connection."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_actions(websocket, data)
            except json.JSONDecodeError:
                print(f"Error: Received invalid JSON: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())