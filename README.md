# AI Message Intelligence

A privacy-first, explainable message processing system built for the AI/ML Engineer Intern assignment at KaStack Labs.

The system processes messages in chronological order and performs three main tasks:

1. Classifies messages into six categories.
2. Extracts actionable tasks and meetings/events.
3. Detects, masks, and assesses sensitive information.

The system is implemented as a deterministic NLP pipeline using Python, regular expressions, rule-based scoring, and structured extraction. It does not send raw messages to external LLM or AI APIs.

---

## Live Demo

### Cloud API

The application is deployed as a FastAPI service on Render:

https://ai-message-intelligence.onrender.com/

### Interactive API Documentation

FastAPI automatically provides Swagger documentation:

https://ai-message-intelligence.onrender.com/docs

The `/analyze` endpoint accepts a message and returns classification, extraction, and sensitive-information results as JSON.

---

## Project Overview

The supplied dataset contains 900 fictional messages arranged chronologically.

Each message contains:

- Message ID
- Timestamp
- Sender
- Message

The system processes each message independently while preserving the chronological processing order.

The processing pipeline is:

```text
                    Input Message
                         |
                         v
              Sensitive Information
                    Detection
                         |
              +----------+----------+
              |                     |
          Sensitive               Safe
              |                     |
              v                     v
        Mask / Assess          Classification
                                    |
                 +------------------+------------------+
                 |                  |                  |
                 v                  v                  v
          Action Required     Meeting/Event       Other Categories
                 |                  |
                 v                  v
           Task Extraction    Event Extraction
                 |                  |
                 +----------+-------+
                            |
                            v
                   Structured Output
````

---

# Features

## 1. Message Classification

Every message is assigned to one of six categories:

* `action_required`
* `meeting_or_event`
* `personal_information`
* `general_information`
* `promotional`
* `sensitive_information`

For every classification, the system generates:

* Message ID
* Predicted category
* Confidence score
* Short explanation/reason

Example:

```json
{
  "message_id": "MSG_0002",
  "category": "action_required",
  "confidence": 0.84,
  "reason": "contains an explicit request to perform an action; contains an action with a date/deadline"
}
```

### Classification approach

The classifier uses deterministic weighted signals rather than a trained neural network.

Examples of signals include:

* Explicit request phrases
* Action verbs
* Deadline/date expressions
* Meeting/event keywords
* Promotional terms
* Personal-information indicators
* Sensitive-information detection

Different signals contribute different weights to the category score.

The final confidence value is derived from the resulting heuristic score.

### Important note about confidence

The confidence score is a **heuristic confidence score**, not a calibrated probability.

This distinction is important because the system was not trained using a labeled classification dataset.

---

# 2. Task and Event Extraction

Messages containing actionable requests or meetings/events are passed to the extraction layer.

## Task extraction

The system extracts:

* Task ID
* Task title
* Description
* Deadline
* Date
* Time
* Person
* Priority
* Source message ID

Example:

```json
{
  "item_id": "TASK_001",
  "type": "task",
  "title": "Submit the report",
  "description": "submit the report",
  "date": null,
  "deadline": "2026-09-09",
  "time": null,
  "person": null,
  "priority": "medium",
  "source_message_id": "API_MESSAGE"
}
```

## Event extraction

The system extracts:

* Event ID
* Event title
* Description
* Date
* Time
* Person
* Priority
* Source message ID

Example:

```json
{
  "item_id": "EVENT_001",
  "type": "event",
  "title": "team meeting",
  "description": "Team meeting is scheduled for 2026-09-12 at 11:00.",
  "date": "2026-09-12",
  "deadline": null,
  "time": "11:00",
  "person": null,
  "priority": "medium",
  "source_message_id": "API_MESSAGE"
}
```

## Missing information

The system does not invent information.

If a field cannot be reliably extracted, it is represented as:

```text
null
```

For example:

```json
{
  "date": null,
  "time": null,
  "person": null
}
```

This follows the assignment requirement not to guess missing information.

---

# 3. Sensitive Information Detection

Sensitive-information detection is performed locally.

The detector looks for sensitive-looking information such as:

* Passwords
* One-time passwords
* Account recovery codes
* Bank account numbers
* Card numbers
* Identification numbers
* Home addresses
* Other supported sensitive patterns

When sensitive information is detected, the sensitive value is masked before it is returned in structured output.

Example:

```text
Original:

My card number is 4111 1111 1111 1111.

Processed:

card number is ****************
```

A sensitive finding contains:

* Sensitivity type
* Risk level
* Masked value
* Recommended action

Example:

```json
{
  "sensitivity_type": "card_number",
  "risk": "high",
  "masked_text": "card number is ****************",
  "recommended_action": "do_not_store"
}
```

## Privacy design

Sensitive detection is intentionally performed locally before any downstream processing.

The application does not send raw messages to an external AI service.

Sensitive values are never intentionally included in:

* Generated logs
* Demonstration screenshots
* Video recordings
* Public GitHub files
* Cloud deployment files

---

# Architecture

```text
                    +----------------------+
                    |      User / Client   |
                    +----------+-----------+
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
        +----------------+          +----------------+
        | Gradio UI      |          | FastAPI REST   |
        | Interactive    |          | POST /analyze  |
        | Demonstration  |          | Render         |
        +--------+-------+          +--------+-------+
                 |                           |
                 +-------------+-------------+
                               |
                               v
                  +-------------------------+
                  | Core Processing Pipeline|
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | Sensitive Detector      |
                  | Detect -> Mask -> Assess|
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | Message Classifier      |
                  | Six categories           |
                  +------------+------------+
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
        +----------------+          +----------------+
        | Task Extractor |          | Event Extractor|
        +--------+-------+          +--------+-------+
                 |                           |
                 +-------------+-------------+
                               |
                               v
                    +---------------------+
                    | Structured JSON     |
                    +---------------------+
```

---

# Why a Rule-Based Approach?

The supplied dataset contains messages but does not provide labeled training data for the six classification categories.

Because of that, directly fine-tuning a supervised model would require first creating a reliable labeled dataset.

I therefore implemented an explainable deterministic baseline instead of fabricating labels or relying completely on an external LLM.

This approach has several advantages for this assignment:

* No external API dependency
* No API key required
* No GPU required
* Reproducible results
* Easy to explain
* Easy to test
* Privacy-preserving
* Deterministic behavior
* Low computational requirements

The design also follows the assignment requirement:

> Do not send raw messages to external AI services.

A future version could introduce a trained classifier or locally hosted transformer after creating and validating a sufficiently large labeled dataset.

---

# Dataset Privacy

The original assignment dataset is intentionally **not included in this public repository**.

The following are excluded using `.gitignore`:

```text
data/
outputs/
.venv/
```

The supplied dataset must be placed locally at:

```text
data/messages.csv
```

The mandatory demonstration IDs should be placed locally at:

```text
data/mandatory_demo_ids.csv
```

The dataset should never be committed to the public GitHub repository.

---

# Results on the Supplied Dataset

The complete pipeline processed:

```text
900 messages
```

Category distribution:

| Category              | Messages |
| --------------------- | -------: |
| General Information   |      265 |
| Action Required       |      197 |
| Meeting or Event      |      148 |
| Sensitive Information |      100 |
| Promotional           |      100 |
| Personal Information  |       90 |
| **Total**             |  **900** |

The extraction pipeline identified:

```text
Tasks: 143
Events: 130
Total tasks/events: 273
```

Sensitive-information detection identified:

```text
Sensitive messages: 100
Non-sensitive messages: 800
```

These results were generated locally using the supplied dataset.

---

# Mandatory Demonstration IDs

The 15 mandatory message IDs were processed through the final pipeline.

The demonstration includes examples covering:

### Action Required

```text
MSG_0002
MSG_0007
```

### Meeting / Event

```text
MSG_0001
MSG_0003
```

### Personal Information

```text
MSG_0009
MSG_0016
```

### General Information

```text
MSG_0004
MSG_0006
MSG_0012
MSG_0037
```

### Promotional

```text
MSG_0014
MSG_0015
```

### Sensitive Information

```text
MSG_0005
MSG_0013
```

### Additional Personal Information example

```text
MSG_0024
```

The mandatory examples include:

* Tasks
* Meetings/events
* Personal information
* General information
* Promotional content
* Sensitive information
* An uncertain classification

Sensitive values from the supplied dataset are not included in this README.

---

# Example API Usage

The deployed application exposes:

```text
POST /analyze
```

Request:

```json
{
  "message": "Please submit the report by 2026-09-09."
}
```

Example response:

```json
{
  "message": {
    "message_id": "API_MESSAGE",
    "category": "action_required",
    "confidence": 0.95,
    "reason": "contains an explicit request to perform an action; contains 'submit'; contains an action with a date/deadline"
  },
  "task_event": {
    "item_id": "TASK_001",
    "type": "task",
    "title": "Submit the report",
    "description": "submit the report",
    "date": null,
    "deadline": "2026-09-09",
    "time": null,
    "person": null,
    "priority": "medium",
    "source_message_id": "API_MESSAGE"
  },
  "sensitive": null
}
```

The API is intentionally lightweight and does not require an external AI API key.

---

# API Architecture

The cloud deployment uses:

```text
Client
   |
   | POST /analyze
   v
FastAPI
   |
   v
process_message()
   |
   +--> Sensitive Detector
   |
   +--> Classifier
   |
   +--> Task/Event Extractor
   |
   v
JSON Response
```

The service is deployed on Render.

---

# Testing

The project uses `pytest`.

Run the complete test suite:

```bash
python -m pytest
```

Current test result:

```text
21 passed
```

The tests cover:

### Classifier

* Action-required detection
* Meeting/event detection
* Personal-information detection
* General-information detection
* Promotional detection
* Sensitive-information classification
* Classification behavior for ambiguous messages

### Extractor

* Task extraction
* Deadline extraction
* Event extraction
* Date extraction
* Time extraction
* Missing information handling
* Event-vs-task precedence

### Sensitive detector

* OTP detection
* Password detection
* Card number detection
* Address detection
* Account recovery code detection
* Masking behavior

---

# Running Locally

## Requirements

Recommended environment:

```text
Python 3.11
```

Create a virtual environment:

```bash
python3.11 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Run Tests

```bash
python -m pytest
```

Expected result:

```text
21 passed
```

---

# Run the Full Dataset Pipeline

Place the dataset in:

```text
data/messages.csv
```

Then run:

```bash
python -m src.pipeline
```

The pipeline processes all messages and generates the classification/extraction results used for analysis.

---

# Run the Gradio Demonstration Interface

The project also contains an interactive Gradio interface used for demonstration.

Run:

```bash
python app.py
```

The interface is available locally at:

```text
http://127.0.0.1:7860
```

The interface allows a user to enter a message and inspect:

* Classification
* Confidence
* Reason
* Task/event extraction
* Sensitive-information detection
* Risk level
* Masked value
* Recommended action

The Gradio interface is intended primarily for interactive demonstration.

The cloud deployment uses FastAPI on Render.

---

# Helper Scripts

The repository contains several helper scripts used during development and validation.

### Classification validation

```bash
python check_classifier.py
```

### Task/event validation

```bash
python check_extractor.py
```

### Sensitive-information validation

```bash
python check_sensitive.py
```

### Mandatory message verification

```bash
python check_mandatory.py
```

The mandatory verification script processes all 15 required demonstration message IDs.

---

# Project Structure

```text
ai-message-intelligence/
│
├── src/
│   ├── __init__.py
│   ├── classifier.py
│   ├── extractor.py
│   ├── pipeline.py
│   └── sensitive_detector.py
│
├── tests/
│   ├── test_classifier.py
│   ├── test_extractor.py
│   └── test_sensitive_detector.py
│
├── app.py
├── main.py
│
├── check_classifier.py
├── check_extractor.py
├── check_mandatory.py
├── check_sensitive.py
├── run_pipeline.py
│
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    └── messages.csv              # local only, not committed
```

---

# Main Components

## `src/sensitive_detector.py`

Responsible for:

* Sensitive pattern detection
* Sensitive type classification
* Risk assessment
* Value masking
* Recommended action

The detector is designed so that raw sensitive values are not returned by the detection function.

---

## `src/classifier.py`

Responsible for:

* Six-category classification
* Weighted signal detection
* Confidence calculation
* Explanation generation

The classifier is deterministic and does not require model downloads or external APIs.

---

## `src/extractor.py`

Responsible for:

* Task extraction
* Event extraction
* Date extraction
* Time extraction
* Deadline extraction
* Priority determination
* Missing-value handling

Events are checked before generic task patterns to avoid incorrectly classifying messages such as:

```text
Please join the internship orientation...
```

as tasks.

---

## `src/pipeline.py`

Responsible for integrating the individual components into the complete processing pipeline.

It:

1. Reads the messages.
2. Processes them in chronological order.
3. Runs sensitive-information detection.
4. Classifies the message.
5. Extracts tasks/events where applicable.
6. Produces structured results.
7. Reports aggregate statistics.

---

# Privacy and Security Considerations

The system was designed with the assignment's privacy requirements in mind.

### Sensitive values are masked

Sensitive values are not intentionally returned in structured results.

### Dataset is not public

The supplied CSV files are excluded from Git.

### No external LLM processing

The supplied messages are not sent to:

* OpenAI
* Gemini
* Groq
* Anthropic
* Other external LLM providers

### No API key required

The core message-processing pipeline does not require an external AI API key.

### Cloud deployment does not contain the dataset

The Render deployment contains the application code only.

The original 900-message assignment dataset is not required by the `/analyze` endpoint.

---

# Limitations

The current system is an explainable baseline and has several limitations.

## 1. Rule-based classification

The classifier relies on manually designed patterns and weighted signals.

This can result in:

* False positives
* False negatives
* Ambiguous classifications

## 2. Confidence is heuristic

The confidence score is not a statistically calibrated probability.

## 3. Limited language understanding

The system may struggle with:

* Indirect requests
* Complex sentence structures
* Sarcasm
* Context-dependent meaning
* Unusual wording

## 4. Regex-based sensitive detection

Pattern-based detection can miss unusual representations of sensitive information or occasionally detect benign text.

## 5. Entity extraction

Person and other entity extraction is conservative.

The system does not guess missing information.

## 6. No supervised training

Because labeled training data was not supplied, the current implementation does not use supervised model training or fine-tuning.

---

# Future Improvements

A future production version could include:

### 1. Human-labeled training dataset

Create a validated labeled dataset from the supplied messages.

### 2. Supervised classifier

Train a lightweight classifier such as:

* Logistic Regression
* Linear SVM
* Fine-tuned transformer

### 3. Local transformer model

A locally hosted transformer could improve semantic classification while keeping raw messages away from external APIs.

### 4. Better entity extraction

Use a local NER model to improve:

* Person extraction
* Organization extraction
* Location extraction
* Date/time extraction

### 5. Better sensitive-information detection

Combine:

```text
Regex
+
Checksum validation
+
NER
+
Context-aware detection
```

to reduce false positives.

### 6. Confidence calibration

Evaluate the classifier on a labeled validation set and calibrate confidence scores.

### 7. Database / message store

For a production system, structured non-sensitive results could be persisted in a database with appropriate retention and access controls.

Sensitive values should follow stricter retention policies.

---

# AI Tool Usage Declaration

AI development tools were used during development for:

* Architecture discussion
* Debugging
* Code assistance
* Test development
* Error analysis
* Documentation assistance

The author reviewed and tested the resulting implementation and understands the submitted code.

The final message-processing system does **not** rely on ChatGPT or an external LLM API to process the supplied dataset.

The classification and extraction results are generated by the implemented local Python pipeline.

---

# Assignment Compliance

| Requirement                                 | Status     |
| ------------------------------------------- | ---------- |
| Process 900 messages                        | Completed  |
| Six message categories                      | Completed  |
| Classification confidence                   | Completed  |
| Classification explanation                  | Completed  |
| Task extraction                             | Completed  |
| Event extraction                            | Completed  |
| Missing information handling                | Completed  |
| Sensitive information detection             | Completed  |
| Sensitive value masking                     | Completed  |
| Risk assessment                             | Completed  |
| Recommended action                          | Completed  |
| 15 mandatory message IDs                    | Verified   |
| Automated tests                             | 21 passing |
| Public GitHub repository                    | Completed  |
| Dataset excluded from public repository     | Yes        |
| Cloud-hosted application                    | Completed  |
| REST API                                    | Completed  |
| Interactive demonstration interface         | Completed  |
| No raw messages sent to external AI service | Yes        |

---

# Author

**Mohsin Khan**

B.Tech — Artificial Intelligence and Data Science

GitHub:

[https://github.com/almohsinkhan/ai-message-intelligence](https://github.com/almohsinkhan/ai-message-intelligence)

````

### One correction before you paste it

I intentionally changed the sensitive-message numbers to:

```text
Sensitive messages: 100
Non-sensitive messages: 800
````

because your **latest final pipeline output was 100 sensitive messages**, and `900 - 100 = 800`. Don't use the older `70/830` or `90/810` figures anywhere in the final README.

Also, your final README now clearly distinguishes:

* **Gradio** → interactive demonstration
* **FastAPI + Render** → cloud-hosted API
* **Rule-based NLP** → actual processing approach
* **No external LLM** → privacy/reproducibility decision

That is much safer than implying you trained an ML model when you didn't.

