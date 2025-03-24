import json
import requests

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_deepseek_response(prompt):
    # Prepare the request payload
    payload = {
        "model": "deepseek-r1:8b",  # Replace with the exact model name if different
        "prompt": prompt + "\nGenerate 10 research questions about this topic.",
        "stream": True
    }
    
    # Send the request to Ollama
    response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
    
    # Collect the final response
    final_response = ""
    for chunk in response.iter_lines():
        if chunk:
            chunk_data = json.loads(chunk.decode("utf-8"))
            # Append the response part to the final response
            final_response += chunk_data.get("response", "")
    
    # Extract only the research questions
    questions = []
    for line in final_response.split("\n"):
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
            questions.append(line.strip())
    
    return questions

def main():
    # Get input string from the user
    user_input = input("Enter your topic: ")
    
    # Get DeepSeek's response
    research_questions = get_deepseek_response(user_input)
    
    # Print DeepSeek's response
    print("\nResearch Questions:")
    for i, question in enumerate(research_questions, 1):
        print(f"{question}")

if __name__ == "__main__":
    main()
