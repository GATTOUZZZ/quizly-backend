from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# --- Q&A MODE ---
@app.route("/generate-qa", methods=["POST"])
def generate_qa():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 20)

    flashcards = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if ":" in line:
            parts = line.split(":", 1)
            flashcards.append({"question": parts[0].strip(), "answer": parts[1].strip()})
        elif " is " in line.lower():
            idx = line.lower().index(" is ")
            q = "What is " + line[:idx].strip() + "?"
            a = line[idx+4:].strip()
            flashcards.append({"question": q, "answer": a})

        if len(flashcards) >= max_cards:
            break

    return jsonify({"flashcards": flashcards})


# --- MCQ MODE ---
@app.route("/generate-mcq", methods=["POST"])
def generate_mcq():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 20)

    flashcards = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        q, a = None, None

        if ":" in line:
            parts = line.split(":", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " is " in line.lower():
            idx = line.lower().index(" is ")
            q = "What is " + line[:idx].strip() + "?"
            a = line[idx+4:].strip()

        if q and a:
            distractors = []
            for other in lines:
                other = other.strip()
                if other and other != line and ":" in other:
                    wrong = other.split(":", 1)[1].strip()
                    if wrong and wrong != a:
                        distractors.append(wrong)
            distractors = list(set(distractors))
            random.shuffle(distractors)
            distractors = distractors[:3]

            options = [a] + distractors
            random.shuffle(options)

            flashcards.append({
                "question": q,
                "answer": a,
                "options": options
            })

        if len(flashcards) >= max_cards:
            break

    return jsonify({"flashcards": flashcards})


# --- SUMMARY MODE ---
@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    data = request.get_json()
    text = data.get("text", "")

    sentences = [s.strip() for s in text.split(".") if s.strip()]
    summary = " ".join(sentences[:3])  # simple summary: first 3 sentences

    return jsonify({"summary": summary})
