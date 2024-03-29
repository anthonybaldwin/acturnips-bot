# For hosting on Heroku we'll need to use the OS library to pull the Token
# from the Enviroment Variables

import os
import random
import asyncio
import discord
import RedditScrape as rs
import psycopg2

subs = ['acturnips']
keywords = ['buy', 'sell', 'for', 'nook', 'turn', 'nmt', 'tim', 'tom', 'twin', 'SW']
channelid = 707097847530782721
roleid = 707108605551312936

token = os.environ['DISCORDBOT_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(channelid)
    print(channel)
    # await client.wait_until_ready()
    while True:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Creating a cursor (a DB cursor is an abstraction, meant for data set traversal)
        cur = conn.cursor()
        for i in range(len(subs)):
            sub = subs[i]
            posts = rs.ScrapePosts(sub, keywords[i])
            for p in posts:
                # Executing your PostgreSQL query
                cur.execute("SELECT EXISTS (SELECT 1 FROM redditpostalerts WHERE post_id = '" + str(p.id) + "');")
                post_id = cur.fetchone()[0]
                if post_id == False:
                    cur.execute("INSERT INTO redditpostalerts (post_id) VALUES ('" + p.id + "');")
                    # In order to make the changes to the database permanent, we now commit our changes
                    conn.commit()
                    await channel.send("<@&" + str(roleid) + "> " + p.title + "\n" + p.url)
                #await channel.send(p.url)
        # We have committed the necessary changes and can now close out our connection
        cur.close()
        conn.close()
        await asyncio.sleep(35)

client.run(token)
