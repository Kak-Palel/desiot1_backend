from flask import Flask, request, jsonify
from utils.esp32 import Esp32
from utils.rag_client import RAGClient
import threading
import time
import sys

app = Flask(__name__)
esp32 = Esp32(port="/dev/ttyACM0", baudrate=115200, timeout=1)
rag_client = RAGClient(api_url="http://10.143.202.13:5678/webhook/desiotone/ragchat")

def read_data():
    while True:
        """Continuously read data from the ESP32 and send it to ThingSpeak."""
        try:
            esp32.read_data()
        except Exception as e:
            print(f"[ERROR] Failed to read data: {e}")
        time.sleep(10)  # Adjust the sleep time as needed

@app.route('/', methods=['GET'])
def simple_home():
    html = """<!doctype html>
<html lang="en">
    <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Desiot1 API</title>
    </head>
    <body style="font-family: Arial, Helvetica, sans-serif; margin: 2rem;">
    <h1>Welcome to Desiot1</h1>
    <p>ESP32 data collector and RAG API.</p>
    <ul>
        <li><a href="/get_latest_data">/get_latest_data</a> - latest sensor reading</li>
        <li><a href="/get_historical_data">/get_historical_data</a> - historical readings</li>
        <li>/get_recommendation - POST to get a recommendation</li>
        <li>/chat - POST to chat with the RAG API</li>
    </ul>
    </body>
</html>"""
    return html


@app.route('/sensor/latest', methods=['GET'])
def get_latest_data():
    """Endpoint to get the latest data from the ESP32."""
    try:
        data = esp32.get_latest_data()
        if not data:
            return jsonify({"status": "error", "message": "No data available"}), 400
        
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sensor/history', methods=['GET'])
def get_historical_data():
    """Endpoint to get historical data from the ESP32."""
    try:
        data = esp32.get_historical_data()
        if not data:
            return jsonify({"status": "error", "message": "No historical data available"}), 400
        
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/ai/advice', methods=['GET'])
def get_recommendation():
    """Endpoint to get a recommendation based on the latest data from the ESP32."""
    try:
        data = esp32.get_latest_data()
        if not data:
            return jsonify({"status": "error", "message": "No data available"}), 400
        
        recommendation = rag_client.get_recommendation(data)
        return jsonify({"status": "success", "recommendation": recommendation}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to send a chat message to the RAG API."""
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({"status": "error", "message": "No message provided"}), 400
        
        response = rag_client.chat(message)
        return jsonify({"status": "success", "response": response}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':

    # Allow port to be specified as a command line argument, default to 5000
    thread1 = threading.Thread(target=read_data)
    thread1.start()
    # port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=5000, debug=True)