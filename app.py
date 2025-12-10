from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# --- Q&A MODE ---
@app.route("/generate-qa", methods=["POST"])
def generate_qa():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 12)  # default ~12 instead of 20

    flashcards = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if ":" in line:
            parts = line.split(":", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " is " in line.lower():
            idx = line.lower().index(" is ")
            q = "What is " + line[:idx].strip() + "?"
            a = line[idx+4:].strip()
        else:
            continue

        if q and a:
            # Ensure answer ends cleanly
            if not a.endswith((".", "?", "!", ";")):
                a += "."
            # Cap very long answers but keep whole words
            words = a.split()
            if len(words) > 30:
                a = " ".join(words[:30]) + "..."
            flashcards.append({"question": q, "answer": a})

    # Limit to max_cards
    flashcards = flashcards[:max_cards]

    return jsonify({"flashcards": flashcards})


# --- MCQ MODE ---
@app.route("/generate-mcq", methods=["POST"])
def generate_mcq():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 12)  # default ~12

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
            # Ensure answer ends cleanly
            if not a.endswith((".", "?", "!", ";")):
                a += "."
            # Cap very long answers but keep whole words
            words = a.split()
            if len(words) > 30:
                a = " ".join(words[:30]) + "..."

            # Collect distractors
            distractors = []
            for other in lines:
                other = other.strip()
                if other and other != line and ":" in other:
                    wrong = other.split(":", 1)[1].strip()
                    if len(wrong.split()) >= 3 and wrong != a:
                        if not wrong.endswith((".", "?", "!", ";")):
                            wrong += "."
                        words_wrong = wrong.split()
                        if len(words_wrong) > 30:
                            wrong = " ".join(words_wrong[:30]) + "..."
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

    # Limit to max_cards
    flashcards = flashcards[:max_cards]

    return jsonify({"flashcards": flashcards})


# --- SUMMARY MODE (already improved) ---
@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"summary": ""})

    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return jsonify({"summary": ""})

    def score(s: str) -> float:
        length = len(s.split())
        verbs = len(re.findall(r"\b(is|are|was|were|has|have|does|do|did|can|could|should|shall|will|may|might)\b", s.lower()))
        punctuation = len(re.findall(r"[,:;–-]", s))
        return 0.5 * length + 0.3 * verbs + 0.2 * punctuation

    ranked = sorted(sentences, key=score, reverse=True)
    picked = ranked[:5]
    summary = " ".join(picked)

    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
