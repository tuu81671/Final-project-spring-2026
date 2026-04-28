import discord

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

intents = discord.Intents.default()
intents.message_content = True

client=Client(intents = intents)
client.run('MTQ5ODQ3MTU1NjY4NTIzODMxNA.GuRL_i.7AABz645jojW-X8CLEWWhtQGbYqA47My5B5lAw')

