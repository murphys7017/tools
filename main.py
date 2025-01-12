from ollama_qw import OllamaQW

def main():
    qw = OllamaQW(model_name='qwen2.5:3b')
    while True:
        msg = input(">: ")
        if msg.lower() == 'exit':
            break
        res = qw.chat(msg)
        print(f"Alice: {res['content']}")
        
        
if __name__ == "__main__":
    main()