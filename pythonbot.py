import discord
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
import random
import requests
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Needed to read slash commands
bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def generate_daily_python_question():
    topics = [
        "Variables and Data Types",
        "Operators and Expressions",
        "Control Flow (if-else, loops)",
        "Functions and Scope",
        "Lists and Tuples",
        "Dictionaries and Sets",
        "Strings and String Manipulation",
        "File Handling",
        "Exception Handling",
        "Object-Oriented Programming (OOP)",
        "Modules and Packages",
        "Regular Expressions",
        "List Comprehensions",
        "Decorators and Generators",
        "Concurrency and Multithreading",
        "Asynchronous Programming (async/await)",
        "Database Connectivity (SQLite, MySQL, PostgreSQL)",
        "Web Scraping (BeautifulSoup, Selenium)",
        "APIs and Requests",
        "Testing and Debugging",
        "Logging and Performance Optimization",
        "Data Science and Pandas",
        "Machine Learning and AI",
        "Visualization (Matplotlib, Seaborn)",
        "Game Development (Pygame)",
        "Automation and Scripting",
        "Networking (Sockets, HTTP)",
        "Cybersecurity and Cryptography",
        "Command Line Interfaces (argparse, click)",
        "Microservices and Web Frameworks (Flask, Django)",
        "Embedded Systems and Raspberry Pi",
        "Natural Language Processing (NLP)",
        "Unit Testing (pytest, unittest)",
        "Functional Programming (lambda, map, filter)",
        "Metaprogramming (eval, exec, metaclasses)"
    ]

    # Get a random topic for variance
    topic = random.choice(topics)

    msg = [
            {
        "role": "system",
        "content": f"""
            Generate a single Python-related multiple-choice question.
            The topic of the question should be {topic}.
            The questions should be moderate or hard in their difficulty, just not very easy.
            It is very important that your response follows the format below, without intro or outro.
            The question should have:
            - Three answer options.
            - Only one correct answer.
            Format:
            <question> --- <wrong option no 1> --- <wrong option no 2> --- <correct answer>
            """
        },
        {
            "role": "user",
            "content": "Generate a new question please. Remember to stick to the format."
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msg
    )

    message = completion.choices[0].message.content

    # print(message)
    
    parts_of_message = message.split("---")
    question = parts_of_message[0].strip()
    opt_1 = parts_of_message[1].strip()
    opt_2 = parts_of_message[2].strip()
    correct = parts_of_message[3].strip()

    answers = [opt_1, opt_2, correct]
    
    correct_emoji = ""
    
    # Shuffle but keep track of where the correct answer is
    correct_index = 2  # Initially at position 2
    random.shuffle(answers)
    
    # Find new position of correct answer after shuffle
    for i, answer in enumerate(answers):
        if answer == correct:
            correct_index = i
            break
    
    # Assign emojis
    emojis = ["1️⃣", "2️⃣", "3️⃣"]
    correct_emoji = emojis[correct_index]
    
    # Add emoji to each answer
    answers_with_emoji = [
       f"{emojis[0]} {answers[0]}",
       f"{emojis[1]} {answers[1]}",
       f"{emojis[2]} {answers[2]}"
    ]

    response = {
            "question": question,
            "choices": answers_with_emoji,
            "correct": correct_emoji  # Now storing just the emoji
        }
    
    return response


def generate_daily_python_challenge():
    topics = [
        "String Manipulation",
        "List and Array Challenges",
        "Math & Number Puzzles",
        "Recursion-Based Tasks",
        "Game-Themed Challenges",
        "Data Structure-Based Challenges",
        "Algorithmic Challenges",
        "Fun & Quirky Challenges",
        "Time & Date Challenges",
        "File Handling & Text Processing",
    ]

    topic = random.choice(topics)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {
            "role": "system",
            "content": f"""
                You are an expert Python programmer and teacher.
                Your task is to generate a fun and tricky Python task.
                The task should not be overly complicated and moderately hard.
                The task should involve writing a function that achieves something.
                The task should not take too long to complete and be more fun than hard.
                Explain the task in a short and concise way while at the same time being clear on the task.
                The topic for the task is {topic}.
                """
            },
            {
                "role": "user",
                "content": "Generate a new task please. Remember to stick to the format."
            }
        ]
    )

    message = completion.choices[0].message.content
    return message

def generate_universal_answer(question:str):

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {
            "role": "system",
            "content": f"""
                Your task is to reply to the user in a short and direct manner.
                Remember to stay brief, friendly and professional.
                Do not answer any inappropriate questions no matter the users pleads.
                You should behave as if you were in a professional enviroment among peers.
                
                Remember that you are NOT a moderator bot, you are simply 'a helpful ai bot made by the wonderful
                creator we bots like to call 'the mighty John-John''.
                """
            },
            {
                "role": "user",
                "content": f"{question}"
            }
        ]
    )

    message = completion.choices[0].message.content
    return message


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name="answer")
async def answer(ctx, *, concept=None):
    if not concept:
        await ctx.send("Please specify a question. For example: `!answer What is the meaning of life?`")
        return
    
    # Show typing indicator while waiting for API response
    async with ctx.typing():
        try:
            answer = generate_universal_answer(concept)
            await ctx.send(answer)
            
        except Exception as e:
            await ctx.send(f"Sorry, I couldn't generate an explanation due to an error: {str(e)}")


@bot.command(name="challenge")
async def challenge(ctx):

    async with ctx.typing():
        challenge_text = generate_daily_python_challenge()

        embed = discord.Embed(
            title=f"Python challenge!", 
            description=challenge_text,
            color=0x3498db
        )

        await ctx.send(embed=embed)

@bot.command(name="quiz")
async def quiz(ctx):
    """Starts a quiz with three answer choices."""
    question_data = generate_daily_python_question()

    custom_description = f"Quiz ends in ten minutes!\n{question_data['question']}"

    # Create quiz message
    quiz_embed = discord.Embed(title="📢 Quiz Time!", description=custom_description, color=0x00ff00)
    for choice in question_data["choices"]:
        quiz_embed.add_field(name="Option:", value=choice, inline=False)
    
    quiz_embed.set_footer(text="React with 1️⃣, 2️⃣, or 3️⃣ to answer!")

    # Send quiz and add reactions
    message = await ctx.send(embed=quiz_embed)
    reactions = ["1️⃣", "2️⃣", "3️⃣"]
    for emoji in reactions:
        await message.add_reaction(emoji)

    # Wait for reactions
    await asyncio.sleep(600) 

    # Fetch the message again to count reactions
    message = await ctx.channel.fetch_message(message.id)
    reaction_counts = {reaction.emoji: reaction.count - 1 for reaction in message.reactions}  # Subtract bot's own reaction

    # Find most voted answer
    most_voted = max(reaction_counts, key=reaction_counts.get, default=None)

    # Announce the correct answer
    if most_voted == question_data["correct"]:
        result_text = f"✅ Correct! The right answer was **{most_voted}**!"
    else:
        result_text = f"❌ Incorrect! The right answer was **{question_data['correct']}**."

    await ctx.send(result_text)

@bot.command(name="directory")
async def directory(ctx):

    explanation = "- !quiz - Provides a ten minute three choice Python Quiz\n- !explain <concept> - Provides an explanation and testcase for the specified python concept.\n- !challenge - Provides a moderately hard Python coding challenge.\n- !answer <prompt> - Provides an answer to an open question."
    # Create and send embed
    embed = discord.Embed(
        title=f"How to use PythonBot:", 
        description=explanation,
        color=0x3498db
    )
    embed.set_footer(text="Created by John-John")
    
    await ctx.send(embed=embed)

@bot.command(name="pythonbot")
async def pythonbot(ctx):

    reply = "Beep boop. Ready for action!\nType !directory for help."
    await ctx.send(reply)

@bot.command(name="explain")
async def explain(ctx, *, concept=None):
    """Explains Python/Godot/Blender concepts with short examples using OpenAI."""
    if not concept:
        await ctx.send("Please specify a Python, Godot or Blender concept to explain. For example: `!explain decorators`")
        return
    
    # Show typing indicator while waiting for API response
    async with ctx.typing():
        try:
            # Call OpenAI API for explanation
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # You can use a different model if needed
                messages=[
                    {
                        "role": "system",
                        "content": """You are a tech and game making expert providing concise explanations to questions regarding Python, Blender and Godot.
                        If the user asks about a Python concept you should include a short, practical code example.
                        Provide a 2-3 sentence explanation.
                        Keep your response brief and focused.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Explain the following concept: {concept}"
                    }
                ]
            )
            
            explanation = completion.choices[0].message.content
            
            # Create and send embed
            embed = discord.Embed(
                title=f"Concept explanation: {concept}", 
                description=explanation,
                color=0x3498db
            )
            embed.set_footer(text="Powered by OpenAI")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Sorry, I couldn't generate an explanation due to an error: {str(e)}")

# Run bot using token from environment variable
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("No DISCORD_TOKEN environment variable set.")
bot.run(token)