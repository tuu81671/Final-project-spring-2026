import discord
import bot_token
import json
import os
from openai import OpenAI

# Using your established names
TOKEN = bot_token.DISCORD_TOKEN
AITOKEN = bot_token.OPENAI_TOKEN

# Initialize the OpenAI client
ai_client = OpenAI(api_key=AITOKEN)

class Client(discord.Client):
    # --- NEW DATA HELPERS: Handles the pantry file ---
    def load_pantry(self):
        try:
            if os.path.exists("pantry.json"):
                with open("pantry.json", "r") as f:
                    return json.load(f)
            return {}
        except:
            return {}

    def save_pantry(self, data):
        with open("pantry.json", "w") as f:
            json.dump(data, f, indent=4)

    async def on_ready(self):
        # Creates pantry.json automatically if missing
        if not os.path.exists("pantry.json"):
            self.save_pantry({})
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f'Messsage from {message.author}:{message.content}')
        
        user_input = message.content.lower()
        user_id = str(message.author.id)

        # --- NEW COMMAND: Adding items to the separate file ---
        if user_input.startswith("!add "):
            items_string = message.content[5:] 
            new_items = [item.strip().lower() for item in items_string.split(",")]

            pantry_data = self.load_pantry()
            if user_id not in pantry_data:
                pantry_data[user_id] = []
            
            pantry_data[user_id].extend(new_items)
            self.save_pantry(pantry_data)

            await message.channel.send(f"Added {', '.join(new_items)} to your pantry file.")
            return

        # --- ORIGINAL MEAL LOGIC: Pulls from the file ---
        elif "what should i eat for" in user_input:
            meal = ""
            if "breakfast" in user_input:
                meal = "breakfast"
            elif "lunch" in user_input:
                meal = "lunch"
            elif "dinner" in user_input:
                meal = "dinner"

            if meal:
                pantry_data = self.load_pantry()
                user_items = pantry_data.get(user_id, [])

                if not user_items:
                    await message.channel.send("Your pantry is empty! Use !add [items] first.")
                    return

                async with message.channel.typing():
                    response = ai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"You are a chef. Suggest a {meal} recipe using ONLY the user's ingredients."},
                            {"role": "user", "content": f"I have: {', '.join(user_items)}"}
                        ]
                    )
                    await message.channel.send(response.choices[0].message.content)
            else:
                await message.channel.send("sorry I do not understand")
        
        else:
            # Strictly follows your requirement for anything else
            await message.channel.send("sorry I do not understand")

# Setup intents
intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(TOKEN)
