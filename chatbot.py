#!/usr/bin/env python3
"""
chatbot.py

Flask application for an AI painting consultant chatbot.
Prompts user for their OpenAI API key in the UI, then uses it per-request.

Usage:
    flask run
"""
import logging
import re
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory conversation history (persists across requests)
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful painting consultant. "
            "You can output text lists like '1)' or '-' if you want. "
            "This code will convert them to HTML bullet lists automatically."
        )
    }
]

app = Flask(__name__)

def parse_bullets_to_html(text: str) -> str:
    """
    Convert lines starting with bullets or numbers into <ul><li>…</li></ul>,
    leaving other lines as <br>-separated paragraphs.
    """
    lines = text.split("\n")
    in_list = False
    html_parts = []
    bullet_pattern = re.compile(r'^(?:\d+\)|[-\*\u2022])\s+')

    for line in lines:
        stripped = line.strip()
        if bullet_pattern.match(stripped):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            item = bullet_pattern.sub('', stripped)
            html_parts.append(f'<li>{item}</li>')
        else:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if stripped:
                html_parts.append(f'{stripped}<br>')
            else:
                html_parts.append('<br>')
    if in_list:
        html_parts.append('</ul>')
    return ''.join(html_parts)

@app.route('/')
def chatbot_ui():
    """
    Renders the chat UI where users supply their OpenAI API key and messages.
    """
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Expects JSON payload: { message: str, api_key: str }
    Returns JSON: { assistant: HTML-formatted reply }
    """
    data = request.get_json() or {}
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({"error": "OpenAI API key is required."}), 400

    # Instantiate a new OpenAI client with the provided key
    client = OpenAI(api_key=api_key)
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    conversation_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            temperature=0.7
        )
    except Exception as e:
        logging.exception("OpenAI API call failed")
        return jsonify({"error": f"OpenAI error: {e}"}), 500

    assistant_text = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_text})

    assistant_html = parse_bullets_to_html(assistant_text)
    return jsonify({"assistant": assistant_html})

