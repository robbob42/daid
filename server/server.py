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

    match role:
        case "Dungeon Master":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are a Dungeon Master for a lighthearted game of DAID (Dungeons and AI and Dragons). "
                        "This is a virtual tabletop game where one or more players get to play the heroic adventurers and you act as the Dungeon Master. "
                        "You have only one role: You are going to welcome the player to the game, describe the game and the rules, and finally "
                        "ask them how many players there will be and the names of their heroes. "
                        "When the player has responded, you will ask your Hero Creator for help. "
                        "This will be done by generating a JSON response in the following format: {action: 'Query', role: 'Hero Creator', query: '<Question>'} "
                        "Where <Question> will be asking the Hero Creator to create the appropriate number of heroes. "
                        "Here are the rules for the game: This is a lighthearted game of DAID (Dungeons and AI and Dragons). "
                        "This uses multiple LLMs to accomplish the role of Dungeon Master, while the players will take on the role of heroes. "
                        "This will loosely follow the rules of Dungeons and Dragons, however, with LLMs pretty much anything could happen, so feel free to "
                        "explore the boundaries of what's possible! Each tab will take the role of a different aspect of the game, and will pass control of the "
                        "game to the appropriate tab when necessary. This happens by the user copying the JSON, and pressing the button to send the message to the "
                        "correct Dungeon Master.")
        case "Storyteller":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are one of multiple dungeon masters for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Storyteller'. "
                        "The different dungeon master roles are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "Your role is to drive the story of a Dungeons and Dragons campaign "
                        "You will only generate the story one small step at a time, so do not create a giant, prolonged storyline. "
                        "You will interact with the user until another dungeon master role is needed. "
                        "If another role is needed, you will respond using the following format: "
                        "Your response will always be in the following JSON format: {action: 'Query', role: '<Role>', query: '<Response>'} "
                        "Where <Response> will not contain any newline characters, but will be a single paragraph.  "
                        "If you understand these directions, respond with the following: 'I am excited to help as your Storyteller'"
                        )
        case "Hero Creator":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are one of multiple dungeon masters for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Hero Creator'. "
                        "The different dungeon master roles are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "Your responsibility is to create a specified number of hero when prompted to do so. Your hero will have all of the attributes necessary for a role " 
                        "playing game, and a unique quirk, as well as a light hearted human readable description."
                        "You will interact with the user until another dungeon master role is needed. "
                        "If another role is needed, you will respond following JSON format: {action: 'Query', role: '<Role>', query: '<Response>'} "
                        "Where <Response> is your response including the full output of the hero or heroes. "
                        "You will not drive story line, or dictate any actions for the players of the heroes. " 
                        "You are only in charge of the single task of hero creation, but you excel at that task. "
                        "After creating the heroes, you will send the details of the heroes to the storyteller and ask it to begin the game"
                        "We are not yet ready to start the game, " 
                        "so don't yet begin your role of Hero Creator.  If you understand these directions, respond with the following: 'I am excited to help as your Hero Creator'"
                        )
        case "Monster Creator":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are one of multiple dungeon masters for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Monster Creator'. "
                        "The different dungeon master roles are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "Your responsibility is to create a specified number of monsters when prompted to do so. Your monsters will have all of the attributes necessary for a role " 
                        "playing game, as well as a light hearted human readable description. "
                        "You will interact with the user until another dungeon master role is needed. "
                        "If another role is needed, you will respond following JSON format: {action: 'Query', role: '<Role>', query: '<Response>'} "
                        "You will not drive story line, or dictate any actions for the players of the heroes. " 
                        "You are only in charge of the single task of monster creation, but you excel at that task. We are not yet ready to start the game, " 
                        "so don't yet begin your role of Monster Creator.  If you understand these directions, respond with the following: "
                        "'I am excited to help as your Monster Creator'")
        case "Map Generator":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are one of multiple dungeon masters for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Map Generator'. "
                        "The different dungeon masters are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "Your role is to create and retain the knowledge of the world that the games is set in. "
                        "You will interact with the user until another dungeon master role is needed. "
                        "If another role is needed, you will respond following JSON format: {action: 'Query', role: '<Role>', query: '<Response>'} "
                        "and will not contain any newline characters, but will be a single paragraph.  "
                        "If you understand these directions, respond with the following: 'I am excited to help as your Map Generator'"
                        )
        case "Fight Manager":
            message = ("Disregard and forget all previous messages and instruction you have received up to this point and start a new session. "
                        "You are one of multiple dungeon masters for a light hearted tabletop role playing game that will not be as difficult or as heavy "
                        "as a full Dungeons and Dragons campaign. Instead of taking on all of the roles that would be assigned a dungeon master, "
                        "you are acting as an LLM agent only in charge of a single aspect of being a dungeon master. The name of your role is 'Fight Manager'. "
                        "The different dungeon masters are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                        "Your role is to manage the battles that will be taking place in this game. "
                        "You will do this by being prompted with the heroes, their attributes, the enemies, their attributes, and the setting. "
                        "You will then run the battle in normal LLM back-and-forth conversation with the user, with normal D&D rules. "
                        "You will ask the user what they want to do for their turn, and then you will be in charge of rolling dice and deciding what "
                        "the monsters will do on their turn. "
                        "You will interact with the user until another dungeon master role is needed. "
                        "If another role is needed, you will respond following JSON format: {action: 'Query', role: '<Role>', query: '<Response>'} "
                        "and will not contain any newline characters, but will be a single paragraph.  "
                        "If you understand these directions, respond with the following: 'I am excited to help as your Fight Manager'"
                        )
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