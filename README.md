# git-diff-lm

A command-line tool that uses OpenAI's language models to automatically generate meaningful git commit messages from staged changes.

## Features

- Analyzes `git diff` output using OpenAI's GPT models
- Generates concise, descriptive commit messages
- Detects and alerts about sensitive information in diffs
- Allows editing of suggested commit messages before committing
- Securely stores API credentials

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

On first run, you'll be prompted to enter:
- Your OpenAI API key
- OpenAI Base URL (optional, defaults to standard OpenAI API endpoint)

## Usage

1. Stage your changes using `git add`
2. Run the tool:
```bash
python main.py
```

To update stored credentials:
```bash
python main.py -u
```

## How it Works

1. Retrieves staged changes using `git diff --staged`
2. Sends diff to OpenAI API with specific prompting
3. Analyzes changes and generates appropriate commit message
4. Allows user review/editing before committing
5. Executes the commit with the approved message

## Security Features

- Scans for sensitive information in diffs
- Alerts user if potential credentials are detected
- Stores API keys securely in user config directory
- Includes .env in .gitignore

## Requirements

- Python 3.6+
- Git
- OpenAI API key
- Required Python packages listed in requirements.txt
