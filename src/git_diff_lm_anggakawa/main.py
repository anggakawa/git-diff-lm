import os
from openai import OpenAI
from dotenv import load_dotenv, set_key
import subprocess
from pathlib import Path
import argparse
from prompt_toolkit import prompt
from getpass import getpass
import sys


ENV_PATH = Path.home() / '.config' / 'git-diff-lm' / '.env'
# Ensure the directory exists
ENV_PATH.parent.mkdir(parents=True, exist_ok=True)

load_dotenv(ENV_PATH)

SYSTEM_PROMPT = """
You are a commit message generator. Your task is to analyze git diff output and create a clear, concise commit message that describes the changes.

Guidelines:
- Check for sensitive/private information (API keys, passwords, tokens, credentials, etc) and notify user with `[ALERT]` prefix
- If sensitive information is detected, stop processing and indicate the specific line where it was found and explain why it appears to be sensitive (e.g. "matches API key format", "contains password pattern", etc)
- Start with a brief summary line (max 50 chars)
- Use bullet points for multiple changes
- Focus on WHAT changed and WHY (if apparent)
- Be specific but concise
- Use present tense (e.g. "Add" not "Added")
- Omit unnecessary punctuation

Example format:
Add user authentication system
- Implement login/signup forms
- Add password hashing
- Set up session management

Analyze the following git diff and generate an appropriate commit message:
"""

def check_for_creds(env_path, update=False):
    def get_system_prompt():
        current_prompt = os.environ.get('SYSTEM_PROMPT', SYSTEM_PROMPT)
        print("\nCurrent system prompt:")
        print(current_prompt)
        edit = input("\nWould you like to edit the system prompt? (y/N): ").lower().strip()
        if edit == 'y':
            new_prompt = prompt("Enter new system prompt (press Esc+Enter when done):\n", multiline=True)
            set_key(env_path, 'SYSTEM_PROMPT', new_prompt)
            os.environ['SYSTEM_PROMPT'] = new_prompt
            print("\nSystem prompt updated successfully!")
    def get_api_key():
        api_key = getpass("Please enter your OpenAI API key: ").strip()
        set_key(env_path, 'OPENAI_API_KEY', api_key)
        os.environ['OPENAI_API_KEY'] = api_key
        
    def get_base_url():
        base_url = input("Please enter your OpenAI Base URL (fill blank for default): ").strip()
        if not base_url:
            base_url = 'https://api.openai.com/v1'
        set_key(env_path, 'OPENAI_BASE_URL', base_url)
        os.environ['OPENAI_BASE_URL'] = base_url
        
    if update:
        get_api_key()
        get_base_url()
        get_system_prompt()
    else:
        if not os.environ.get('OPENAI_API_KEY'):
            get_api_key()
        if not os.environ.get('OPENAI_BASE_URL'):
            get_base_url()

def fetch_openai(message):

    try:
        client = OpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL'),
            api_key=os.environ.get('OPENAI_API_KEY'),
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": os.environ.get('SYSTEM_PROMPT', SYSTEM_PROMPT)},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def main():
    try:
        parser = argparse.ArgumentParser(description='Generate commit messages from git diff')
        parser.add_argument('-u', '--update', action='store_true', help='Update credentials')
        args = parser.parse_args()

        check_for_creds(ENV_PATH, args.update)
        result = subprocess.run('git diff --staged', capture_output=True, text=True, shell=True)
        if not result.stdout:
            print("No staged changes found. Please stage your changes using 'git add' first.")
            sys.exit(1)
        commit_message = fetch_openai(result.stdout)
        if "[ALERT]" in commit_message:
            print("\nWarning: The diff contains '[ALERT]' marker!\n")
        commit_message = prompt("This is the commit message: \n\n---\n", default=commit_message)

        subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == '__main__':
    main()