import discord
import nltk
import asyncio
import random
import os
import re
from collections import defaultdict

nltk.download('punkt')
nltk.download('punkt_tab')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

markov_chain = defaultdict(list)
word_list = []
original_sentences = set()

# Support for .txt files.
if not os.path.exists('downloaded-files'):
    os.makedirs('downloaded-files')

# You may put as many as you want here, just don't go overboard if you don't want it to go schizo. Look at line 76 for information to get messages from these channels.
channel_ids_to_collect_from = [
    12345,
    678910,
    1112131415
]

channel_to_send_messages = 12345
url_pattern = re.compile(r'(https?://\S+|www\.\S+)')
mention_pattern = re.compile(r'<(@!?|#|@&)?\d+>')
emoji_pattern = re.compile(r'<a?:\w+:\d+>')  
alphanumeric_pattern = re.compile(r'\b\w+\b') 

def build_markov_chain(words):
    for i in range(len(words) - 1):
        word, next_word = words[i], words[i + 1]
        markov_chain[word].append(next_word)

def generate_sentence():
    if not word_list:
        return None
    
    attempts = 0
    while attempts < 20:
        word = random.choice(word_list)
        sentence = [word]
        
        for _ in range(random.randint(5, 15)):
            next_words = markov_chain.get(word)
            if not next_words:
                break
            word = random.choice(next_words)
            sentence.append(word)
        
        sentence_str = ' '.join(sentence)
        
        if sentence_str not in original_sentences and not url_pattern.search(sentence_str):
            return sentence_str
        attempts += 1
    
    return None

@client.event
async def on_ready():
    global word_list
    
    print(f'Logged in as {client.user}')
    
    for channel_id in channel_ids_to_collect_from:
        channel = client.get_channel(channel_id)
        if channel:
            # Change 100 to what you want it to be: like if you set it to 50 it will grab 50 messages from each channel ID
            messages = [message async for message in channel.history(limit=100)]
            
            for message in messages:
                clean_content = re.sub(url_pattern, '', message.content.lower())
                clean_content = re.sub(mention_pattern, '', clean_content)
                clean_content = re.sub(emoji_pattern, '', clean_content)
                words = nltk.word_tokenize(clean_content)
                
                words = [word for word in words if alphanumeric_pattern.match(word)]
                
                word_list.extend(words)
                build_markov_chain(words)
                
                original_sentences.add(message.content.lower())
                print(f"Collected words from message: {words}")
        
            for filename in os.listdir('downloaded-attachments'):
                if filename.endswith('.txt'):
                    file_path = os.path.join('downloaded-attachments', filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read().lower()
                        file_content = re.sub(url_pattern, '', file_content)
                        file_content = re.sub(mention_pattern, '', file_content)
                        file_content = re.sub(emoji_pattern, '', file_content)
                        words = nltk.word_tokenize(file_content)
                        
                        words = [word for word in words if alphanumeric_pattern.match(word)]
                        
                        word_list.extend(words)
                        build_markov_chain(words)
                        
                        original_sentences.add(file_content)
                        print(f"Collected words from file {filename}: {words}")

    word_list = [word for word in word_list if not url_pattern.match(word)]
    
    channel = client.get_channel(channel_to_send_messages)
    if channel:
        client.loop.create_task(send_message_periodically(channel))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith('.txt'):
                file_path = f'downloaded-attachments/{attachment.filename}'
                await attachment.save(file_path)
                print(f"Downloaded file: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read().lower()
                    file_content = re.sub(url_pattern, '', file_content)
                    file_content = re.sub(mention_pattern, '', file_content)
                    file_content = re.sub(emoji_pattern, '', file_content)
                    words = nltk.word_tokenize(file_content)
                    
                    words = [word for word in words if alphanumeric_pattern.match(word)]
                    
                    word_list.extend(words)
                    build_markov_chain(words)
                    
                    original_sentences.add(file_content)
                    print(f"Collected words from file: {words}")
    
    try:
        clean_content = re.sub(url_pattern, '', message.content.lower())
        clean_content = re.sub(mention_pattern, '', clean_content)
        clean_content = re.sub(emoji_pattern, '', clean_content)
        words = nltk.word_tokenize(clean_content)
        
        words = [word for word in words if alphanumeric_pattern.match(word)]
        
        word_list.extend(words)
        build_markov_chain(words)
        
        original_sentences.add(message.content.lower())
        print(f"Collected words: {words}")
    except Exception as e:
        print(f"Error tokenizing message: {e}")

async def send_message_periodically(channel):
    while True:
        await asyncio.sleep(7)
        
        sentence = generate_sentence()
        if sentence:
            print(f"Sending message: {sentence}")
            await channel.send(sentence)
        else:
            print("No unique sentence generated.")

client.run('YOUR_BOT_TOKEN')
