import requests
import json

class RAGClient:
    def __init__(self, api_url="http://172.18.96.13:5678/webhook/desiotone/ragchat", recommendation_session_id="dc4eed223c5446f5935de3f83e363a06", chat_session_id="0f04b2f595af4c8d91e41f138798e03f", api_key=None):
        """Initializes the RAG client with the API URL and key."""
        self.api_url = api_url
        self.recommendation_session_id = recommendation_session_id
        self.chat_session_id = chat_session_id
    
    def call_api(self, chat, sessionId):
        """Calls the RAG API with the provided chat message."""
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "sessionId": sessionId,
            "action": "sendMessage",
            "chatInput": chat
        }

        response = requests.post(self.api_url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get_recommendation(self, data):
        """Gets a recommendation based on the provided data."""
        
        temp = data.get("temperature", 0.0)
        humid = data.get("humidity", 0.0)
        eco2 = data.get("eco2", 0)
        tvoc = data.get("tvoc", 0)
        aqi = data.get("aqi", 0)

        print(f"[RAG_CLIENT][INFO] Getting recommendation for data: {data}")

        data = {"data": {"temperature": {temp}, "humidity": {humid}, "eco2": {eco2}, "tvoc": {tvoc}, "aqi": {aqi}}}
        return self.call_api(f"given air quality data: {data}. analyze each parameters whether its normal or too low or too high, if they're not normal, you have to specify it in your response and give some known consequence of such abnormal parameter (if found in the vector database) and also give actionable recommentations to the user such as opening window, turning up the integrated humidifier or purifier fan, clean the room using vacoom cleaner, etc", self.recommendation_session_id)[0].get("output")

    def chat(self, message):
        """Sends a chat message to the RAG API."""
        print(f"[RAG_CLIENT][INFO] Sending chat message: {message}")
        return self.call_api(message, self.chat_session_id)[0].get("output")

if __name__ == "__main__":
    client = RAGClient()
    sample_data = {
        "temperature": 35.05,
        "humidity": 42.221,
        "eco2": 401.12,
        "tvoc": 149.21,
        "aqi": 48.213
    }
    # recommendation = client.get_recommendation(sample_data)
    # print(recommendation)
    # print(type(recommendation))

    chat = "okay doing it now, thanks!"
    response = client.chat(chat)
    print(response)

"""
The prompts given are from the system that have acces to the ENS160 sensor and also actuators. namely, air humidifier and purifier.  There are several task that you need to do based on the 'action' field in the given prompt. The details of instruction for each 'action' are given below

1. getRecommendation
for this action, the prompt will have 'data' field which contains the data reading from sensors. What you need to do is analyze each data (temp, humidity, eco2, tvoc). whether its normal or too low or too high, if they're not normal, you have to specify it in your response and give some known consequence of such abnormal parameter (if found in the vector database) and also give actionable recommentations to the user such as opening window, turning up the integrated humidifier or purifier fan, clean the room using vacoom cleaner, etc.

2. assistantChat
in this task, you just need to be a regular chatbot that gives helpfull answer to the user's prompts based on your knowledge from the semantic database, but never mentions that you get it from the snippets given from the database. Talks confidently as if youre talking to a person that said the words given in the "message" field inside of the "human" json. Have a friendly and helpfull persona instead of some data analyzer robot

some prompts may include references to some pdfs, remember, you have tool to access a semantic database, use the references to your advantage to d query
"""
