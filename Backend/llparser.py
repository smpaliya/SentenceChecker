from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import defaultdict
app = Flask(__name__)
CORS(app,resources={r"/checksentence": {"origins": "http://localhost:3000"}})

grammar = {
    "Sentence": [["Subject", "Predicate"]],
    "Subject": [["NounPhrase"]],
    "NounPhrase": [["Article", "Noun"], ["Noun"]],
    "Predicate": [["VerbPhrase"]],
    "VerbPhrase": [["Verb", "NounPhrase"], ["Verb"]],
    "Article": [["a"], ["the"]],
    "Noun": [["cat"], ["dog"], ["man"], ["woman"],["ship"],["bird"]],
    "Verb": [["eats"], ["sees"], ["likes"],["speaks"],["floats"],["flew"]]
}
first_sets = defaultdict(set)
follow_sets = defaultdict(set)
parsing_table = {}
@app.route('/checksentence', methods=['POST'])
def check_sentence():
    print("In check sentence")
    data = request.get_json()
    line = data.get("sentence", "").strip()  # Clean whitespace

    if not line:
        return jsonify({"answer": False, "message": "No sentence provided"}), 400
    for non_terminal in grammar:
        compute_first(non_terminal)
    compute_follow()
    print("first , folllow calculated")

    for lhs, rules in grammar.items():
        parsing_table[lhs] = {}
        for rule in rules:
            first_set = set()

            # Compute FIRST of the rule
            for item in rule:
                first_part = compute_first(item)
                first_set.update(first_part - {'ε'})
                if 'ε' not in first_part:
                    break
            else:
                first_set.add('ε')

            # Populate parsing table
            for terminal in first_set:
                if terminal != 'ε':
                    parsing_table[lhs][terminal] = rule

            # Handle ε-productions using FOLLOW sets
            if 'ε' in first_set:
                for terminal in follow_sets[lhs]:
                    if terminal in parsing_table[lhs]:  # Avoid conflicts
                        print(f"⚠ Conflict in Parsing Table: {lhs}, {terminal}")
                    parsing_table[lhs][terminal] = rule
    answer=parse(line)
    if answer:
        print("✅ Valid Sentence!")
        return jsonify({"answer":True,"message":"Valid Sentence"}),200
    else:
        print("❌ Invalid Sentence!")
        return jsonify({"answer":False,"message":"Invalid Sentence"}),200


def compute_first(symbol):
    if symbol in first_sets and first_sets[symbol]:
        return first_sets[symbol]  # Return cached FIRST set

    if symbol not in grammar:  # Terminal symbol
        return {symbol}

    first = set()
    for rule in grammar[symbol]:
        for item in rule:
            first_part = compute_first(item)
            first.update(first_part - {'ε'})  # Add everything except ε
            if 'ε' not in first_part:
                break
        else:
            first.add('ε')  # All items in the rule can be ε

    first_sets[symbol] = first  # Cache the result
    return first

# Compute FIRST for all non-terminals
for non_terminal in grammar:
    compute_first(non_terminal)

# Function to compute FOLLOW sets
def compute_follow():
    follow_sets["Sentence"].add("$")  # Start symbol gets '$'

    while True:
        updated = False

        for lhs, rules in grammar.items():
            for rule in rules:
                follow = follow_sets[lhs]  # FOLLOW of LHS

                for i in range(len(rule) - 1, -1, -1):
                    symbol = rule[i]

                    if symbol in grammar:  # If it's a non-terminal
                        before_update = len(follow_sets[symbol])
                        follow_sets[symbol].update(follow)  # FOLLOW propagation

                        if i + 1 < len(rule):  # Check next symbol
                            first_next = compute_first(rule[i + 1])
                            follow_sets[symbol].update(first_next - {'ε'})

                            if 'ε' in first_next:
                                follow_sets[symbol].update(follow)

                        updated |= before_update != len(follow_sets[symbol])

                    follow = compute_first(symbol) if 'ε' in compute_first(symbol) else {symbol}

        if not updated:
            break

# LL(1) Parser Function
def parse(sentence):
    tokens = sentence.split() + ["$"]  # Tokenize input and add end marker
    stack = ["$", "Sentence"]  # Initialize stack with start symbol
    index = 0  # Position in input sentence

    print("\nParsing Steps:")
    while stack:
        top = stack.pop()
        current_token = tokens[index]

        print(f"Stack: {stack} | Current Token: {current_token}")

        if top == current_token:  # Terminal match
            index += 1
        elif top in parsing_table and current_token in parsing_table[top]:  # Apply rule
            production = parsing_table[top][current_token]
            print(f"Expanding {top} → {production}")
            stack.extend(reversed(production))  # Push rule in reverse
        else:
            print(f"Error: Unexpected token '{current_token}' at position {index}")
            return False  # Parsing failed

    return index == len(tokens)

if __name__ == '__main__':
    app.run(debug=True)