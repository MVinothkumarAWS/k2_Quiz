# GK Video Generator

Generate YouTube quiz videos from GK (General Knowledge) questions with text-to-speech narration.

## Features

- **Shorts format** (9:16) - One question per video, vertical format
- **Full video format** (16:9) - Multiple questions with score tracking
- **Text-to-Speech** - Free Edge TTS in English and Tamil
- **Auto images** - Automatically fetch images from Pixabay
- **Dark minimal theme** - Modern look with animations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Input Format

Create a JSON file with your questions:

```json
{
  "title": "My Quiz",
  "language": "english",
  "questions": [
    {
      "question": "What is the capital of France?",
      "options": ["London", "Paris", "Berlin", "Madrid"],
      "correct": 1,
      "image": "auto"
    }
  ]
}
```

- `correct`: Index of correct answer (0-3)
- `image`: "auto" to fetch from Pixabay, or filename from `images/` folder

### Generate Videos

```bash
# Shorts (one video per question)
python generate.py input/questions.json --format shorts

# Full video (multiple questions)
python generate.py input/questions.json --format full

# Tamil voice
python generate.py input/questions.json --format shorts --lang tamil

# Custom output name
python generate.py input/questions.json --format full --output "history_quiz"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | `shorts` or `full` | shorts |
| `--lang` | `english` or `tamil` | english |
| `--output` | Output filename base | from title |
| `--count` | Questions per full video | 10 |
| `--output-dir` | Output directory | output/ |

## Getting Questions from Gemini

Ask Gemini to generate questions in JSON format:

```
Generate 10 GK questions about Indian History in this JSON format:
{
  "title": "Indian History Quiz",
  "language": "english",
  "questions": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "image": "auto"
    }
  ]
}
```

## License

MIT
