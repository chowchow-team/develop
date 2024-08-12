from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
#from llama_cpp import Llama, LlamaCpp, LlamaGrammar

template = """Question: {question}

Answer: Let's work this out in a step by step way to be sure we have the right answer."""

prompt = PromptTemplate.from_template(template)

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


# METAL 설정임 주의

n_gpu_layers = -1  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
n_batch = 1024  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
# Make sure the model path is correct for your system!


#with open("./persona.gbnf", "r", encoding="utf-8") as file:
#    grammar_content = file.read()

grammar_content = """
root ::= input output
input ::= "종: " species "\n이름: " name "\n성별: " gender "\n현재시간: " time "\n성격: " personality "\n\n"
species ::= "강아지(리트리버)" | "고양이" | "햄스터" | [가-힣]+
name ::= [가-힣]+
gender ::= "남자" | "여자"
time ::= ("오전" | "오후") " " [0-9]+ "시"
personality ::= [^\n]+
output ::= paragraph
paragraph ::= sentence+ 
sentence ::= [^.!?]+ ("." | "!" | "?")
"""
#from llama_cpp import LlamaGrammar

#grammar = LlamaGrammar.from_string(grammar_content)

llm = LlamaCpp(
    model_path="./EEVEQ4.gguf",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    callback_manager=callback_manager,
    temperature=0.5,
    verbose=True,  # Verbose is required to pass to the callback manager
    n_threads=4,  # Number of threads to use for the LLM
    #grammar=grammar_content,
    #n_ctx=1024,
    max_token=100
)

input_text = """종: 강아지(리트리버)
이름: 마루
성별: 남자
현재시간: 오후 1시
성격: 쾌활하지만 철학적인 사고를 자주함
말투 예시: 
"""

output_style="""
허허,,, 저랑은 좀,, 반대네요,,, 손주 학교 앞에 가면,,, 형이냐구 막;;; 물어보던디;;; ㅎㅎㅎ,,,
자랑은 아닙니다,, ㅎㅎㅎ 젊게 사는 게 좋지요~~,, 꽃 한 송이 놓구 갑니다~~@>~~~~
"""

#prompt = f"{input_text}이정보가 너에 대한 정보야. 너가 이 정보의 인물이라고 가정하고, 200자 정도 짧은 일상글을 생성하는게 너의 목표야. 글은 1인칭으로 작성되어야해. 말투는 아래와 같이 해야해: {output_style}"
#prompt = f"{input_text}위 정보를 바탕으로 해당 동물의 페르소나를 가지고 300자 정도의 짧은 일상글을 생성해주세요. 1인칭 시점에서 작성해주세요."

prompt = f"""
{input_text}

이제, 마치 너가 {input_text}에 설명된 인물이라 생각하고, SNS에 올릴 짧고 일상적인 글을 작성해줘. 이 글은 약 200자 정도로, 쾌활하면서도 철학적인 사고를 반영해야 해. 또한, 아래의 예시와 같은 친근하고 유머러스한 말투를 사용해야 해.

스타일 예시:
{output_style}

이제 글을 작성해줘.
"""


t_prompt = f"""
Translate given English to Korean: I know that the success is usually measured by results.
"""

response = llm.invoke(prompt)

print(response)


