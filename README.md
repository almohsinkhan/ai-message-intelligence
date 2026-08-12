# AI Message Intelligence

A privacy-first message processing system that classifies messages, extracts tasks/events, and detects sensitive information.

## Features

- Message classification into six categories
- Task extraction
- Meeting/event extraction
- Deadline and time extraction
- Conservative person extraction
- Sensitive-information detection
- Sensitive-value masking
- Risk assessment
- Explainable classification decisions
- Deterministic and reproducible processing
- Chronological processing of messages

## Architecture

Raw Message
    |
    v
Sensitive Information Detector
    |
    +---- Sensitive ----> Mask + Sensitive Output
    |
    +---- Safe ---------> Message Classifier
                              |
                              +--> Action Required --> Task Extraction
                              |
                              +--> Meeting/Event ---> Event Extraction
                              |
                              +--> Other Categories

## Categories

1. Action Required
2. Meeting or Event
3. Personal Information
4. General Information
5. Promotional
6. Sensitive Information

## Approach

The system uses deterministic, explainable rules rather than relying entirely on an external LLM.

This was chosen because the supplied dataset does not provide labeled training data. A supervised fine-tuned classifier would therefore require manually labeled data or another labeling strategy.

Sensitive information is detected before downstream processing. Sensitive values are masked and are never intentionally sent to an external AI service.

## Task/Event Extraction

Tasks and events are extracted only when the classifier identifies the message as Action Required or Meeting/Event.

Unknown fields are represented using `null`.

The system does not invent missing dates, times, people, or deadlines.

## Sensitive Information

The detector identifies information such as:

- Passwords
- OTPs
- Account recovery codes
- Bank account numbers
- Card numbers
- Identification numbers
- Addresses
- Contact information
- Health information

Sensitive values are masked before being included in generated output.

## Testing

Run:

```bash
python -m pytest
Current test suite:

Classifier tests
Sensitive detector tests
Task/event extractor tests
Running

Create a Python 3.11 virtual environment:

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Run tests:

python -m pytest

Run the pipeline:

python -m src.pipeline
Dataset

The supplied dataset is intentionally excluded from this repository.

Place the local dataset at:

data/messages.csv

and the mandatory demonstration IDs at:

data/mandatory_demo_ids.csv
Current Results

The system processes 900 messages.

Category distribution:

Category	Count
General Information	265
Action Required	197
Meeting or Event	148
Sensitive Information	100
Promotional	100
Personal Information	90
Total	900

The system currently extracts:

143 tasks
130 events
Limitations
The classifier is rule-based rather than trained on labeled data.
Confidence scores are heuristic scores, not calibrated probabilities.
Entity/person extraction is intentionally conservative.
Regex-based sensitive detection can produce false positives or miss unusual formats.
More robust NLP models could improve classification and extraction with appropriate labeled data.
The current system is designed for the supplied message format and would require further validation on real-world data.
AI Tool Usage

AI development tools were used during implementation for debugging, architecture discussion, code review, and development assistance.

The final system does not rely on ChatGPT or an external LLM/API to process the supplied messages.

The implementation was reviewed and tested locally by the author.
