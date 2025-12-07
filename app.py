from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/generate-flashcards", methods=["POST"])
def generate_flashcards():
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
