from llama_cpp.llama import Llama, LlamaGrammar

def grammarInterpreter(elements):
    def interpretJson(element):
        output = ["[{] ws "]
        keys = list(element.keys())
        for i, key in enumerate(keys):
            content = element[key]
            output.extend(["[\"] \"", key, "\" [\"] ws \":\" ws "])
            if isinstance(content, str):
                if content.startswith("$"):
                    output.append(content[1:] + " ")
                else:
                    output.extend(["[\"] \"", content, "\" [\"] "])
            else:
                output.append(interpretJson(content))
            if i != len(keys) - 1:
                output.append("[,] ws ")
        output.append("ws [}]")
        return ''.join(output)

    grammar = """
    root ::= input output
    input ::= "Species: " species "\nName: " name "\nGender: " gender "\nCurrent time: " time "\nPersonality: " personality "\n\n"
    species ::= "Dog (Retriever)" | "Cat" | "Hamster" | [a-zA-Z]+
    name ::= [a-zA-Z]+
    gender ::= "Male" | "Female"
    time ::= ("AM" | "PM") " " [0-9]+ ":00"
    personality ::= [^\n]+
    output ::= paragraph
    paragraph ::= sentence+ 
    sentence ::= [^.!?]+ ("." | "!" | "?")
    float ::= "-"? [0-9]+ "." [0-9]+
    int ::= "-"? [0-9]+
    str ::= "\\"" [^\\"]* "\\""
    ws ::= [ \t\n]*
    """
    grammar_list = [grammar]
    for element, content in elements.items():
        if isinstance(content, str):
            parts = content.split("$")
            c = 0
            grammar_part = "\"" + parts[0] + "\""
            for part in parts[1:]:
                if part != "":
                    c += 1
                    if (c%2) == 1:
                        grammar_part += " " + part + " "
                    else:
                        grammar_part += "\"" + part + "\""
            grammar_list.append(f"{element} ::= {grammar_part}\n")
        else:
            grammar_list.append(f"{element} ::= {interpretJson(content)}\n")
    return ''.join(grammar_list)

llm = Llama(
    model_path="./ggml-model-Q4_0.gguf",
    n_gpu_layers=-1,
    n_ctx=1024,
    f16_kv=True,
    n_threads=4,
)

simple_grammar = {
    "root": "input output",
    "input": "\"Species: \" species \"\\nName: \" name \"\\nGender: \" gender \"\\nCurrent time: \" time \"\\nPersonality: \" personality \"\\n\\n\"",
    "species": "\"Dog (Retriever)\" | \"Cat\" | \"Hamster\" | [a-zA-Z]+",
    "name": "[a-zA-Z]+",
    "gender": "\"Male\" | \"Female\"",
    "time": "(\"AM\" | \"PM\") \" \" [0-9]+ \":00\"",
    "personality": "[^\\n]+",
    "output": "paragraph",
    "paragraph": "sentence+",
    "sentence": "[^.!?]+ (\".\" | \"!\" | \"?\")"
}

grammar_string = grammarInterpreter(simple_grammar)
grammar = LlamaGrammar.from_string(grammar_string)

input_text = """Species: Dog (Retriever)
Name: Maru
Gender: Male
Current time: PM 1:00
Personality: Cheerful but often engages in philosophical thinking
"""
prompt = f"{input_text}\nBased on the above information, please generate a short daily life story of about 300 characters portraying the persona of this animal."

response = llm(
    prompt=prompt,
    grammar=grammar, 
    max_tokens=256
)
print(response['choices'][0]['text'])