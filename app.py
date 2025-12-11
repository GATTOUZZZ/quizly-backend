from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# --- Q&A MODE ---
@app.route("/generate-qa", methods=["POST"])
def generate_qa():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 15)

    flashcards = []
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    for line in sentences:
        line = line.strip()
        q, a = None, None

        if ":" in line:
            parts = line.split(":", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " - " in line:
            parts = line.split(" - ", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " is " in line.lower():
            idx = line.lower().index(" is ")
            q = "What is " + line[:idx].strip() + "?"
            a = line[idx+4:].strip()
        elif " are " in line.lower():
            idx = line.lower().index(" are ")
            q = "What are " + line[:idx].strip() + "?"
            a = line[idx+5:].strip()
        elif " means " in line.lower():
            idx = line.lower().index(" means ")
            q = "What does " + line[:idx].strip() + " mean?"
            a = line[idx+7:].strip()
        elif " refers to " in line.lower():
            idx = line.lower().index(" refers to ")
            q = line[:idx].strip() + " refers to what?"
            a = line[idx+10:].strip()
        elif " defined as " in line.lower():
            idx = line.lower().index(" defined as ")
            q = line[:idx].strip() + " is defined as what?"
            a = line[idx+12:].strip()

        if q and a:
            if not a.endswith((".", "?", "!", ";")):
                a += "."
            words = a.split()
            if len(words) > 30:
                a = " ".join(words[:30]) + "..."
            flashcards.append({"question": q, "answer": a})

    flashcards = flashcards[:max_cards]
    return jsonify({"flashcards": flashcards})


# --- MCQ MODE ---
@app.route("/generate-mcq", methods=["POST"])
def generate_mcq():
    data = request.get_json()
    text = data.get("text", "")
    max_cards = data.get("maxCards", 15)

    flashcards = []
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    for line in sentences:
        line = line.strip()
        q, a = None, None

        # Extract Q/A
        if ":" in line:
            parts = line.split(":", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " - " in line:
            parts = line.split(" - ", 1)
            q, a = parts[0].strip(), parts[1].strip()
        elif " is " in line.lower():
            idx = line.lower().index(" is ")
            q = "What is " + line[:idx].strip() + "?"
            a = line[idx+4:].strip()
        elif " are " in line.lower():
            idx = line.lower().index(" are ")
            q = "What are " + line[:idx].strip() + "?"
            a = line[idx+5:].strip()
        elif " means " in line.lower():
            idx = line.lower().index(" means ")
            q = "What does " + line[:idx].strip() + " mean?"
            a = line[idx+7:].strip()
        elif " refers to " in line.lower():
            idx = line.lower().index(" refers to ")
            q = line[:idx].strip() + " refers to what?"
            a = line[idx+10:].strip()
        elif " defined as " in line.lower():
            idx = line.lower().index(" defined as ")
            q = line[:idx].strip() + " is defined as what?"
            a = line[idx+12:].strip()

        # Validate
        if q and a:
            if not a.endswith((".", "?", "!", ";")):
                a += "."
            words = a.split()
            if len(words) > 30:
                a = " ".join(words[:30]) + "..."

            # Collect distractors from text
            distractors = []
            for other in sentences:
                other = other.strip()
                if other and other != line and (":" in other or " - " in other):
                    wrong = other.split(":", 1)[-1].strip() if ":" in other else other.split(" - ", 1)[-1].strip()
                    if len(wrong.split()) >= 3 and wrong != a:
                        if not wrong.endswith((".", "?", "!", ";")):
                            wrong += "."
                        words_wrong = wrong.split()
                        if len(words_wrong) > 30:
                            wrong = " ".join(words_wrong[:30]) + "..."
                        distractors.append(wrong)

            # ✅ Fallback: generate random distractors if not enough
            while len(distractors) < 3:
                fake = "Incorrect alternative " + str(random.randint(100, 999))
                distractors.append(fake)

            distractors = distractors[:3]
            options = [a] + distractors
            random.shuffle(options)

            flashcards.append({
                "question": q,
                "answer": a,
                "options": options
            })

    flashcards = flashcards[:max_cards]
    return jsonify({"flashcards": flashcards})


# --- SUMMARY MODE ---
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
