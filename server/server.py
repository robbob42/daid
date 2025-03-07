import asyncio
import websockets
import json

# Global variables to store agent data
agent_data = {}

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
            message = ("You are a Dungeon Master for a lighthearted game of DAID (Dungeons and AI and Dragons). "
                                "This is a virtual tabletop game where one or more players get to play the heroic adventurers and you act as the Dungeon Master. "
                                "Fortunately, you are not alone.  You have several helper agents that are going to assist you. "
                                "Your helper agents are: 'Storyteller', 'Hero Creator', 'Monster Creator', 'Map Generator', and 'Fight Manager' "
                                "To call one of your helper agents, you will use the following JSON format: {action: 'Query', role: '<Agent>', query: '<Question>'} "
                                "Where <Agent> is the name of the agent you need help from, and <Question> is the prompt that you are going to send to your helper agent LLM. "
                                "The game will be played as follows: When the game begins, you will need to ask the user how many players there are, what they want the names of their "
                                "heroes to be, and a short description for each hero. "
                                "When the player has responded, you will need to generate a prompt that will be sent to the Hero Creator asking for assistance in creating the "
                                "correct number of heroes for the upcoming adventure. "
                                "As long as you completely understand these directions, you will respond with the following, and only the following: 'Shall we play a game?'")
        case "Storyteller":
            message = "Greetings, Storyteller! Let's weave a captivating narrative together."
        case "Hero Creator":
            message = ("You are an assistant dungeon master for a light hearted tabletop role playing game that will not be as difficult or as heavy "
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
                                  "so don't yet begin your role of Hero Creator.  If you understand these directions, respond with the following: 'I am excited to help'"
            )
        case "Monster Creator":
            message = "Greetings, Monster Creator! Let's unleash some fearsome creatures."
        case "Map Generator":
            message = "Welcome, Map Generator! I'm here to assist you in crafting immersive worlds."
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
            print(f"Sending message '{query}' to '{tab_id}'")
            await send_message(websocket, tab_id, query)
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