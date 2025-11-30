import serial
import json
import requests

class Hub:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        
        self.latest_data_temp = 0.0
        self.latest_data_humd = 0.0
        self.latest_data_eco2 = 0.0
        self.latest_data_tvoc = 0.0
        self.latest_data_aqi = 0.0
        
        self.write_url = "https://api.thingspeak.com/update?api_key=E45QIV0OXGFP2V90"

    def read_data(self):
        if self.ser.isOpen():
            # line = self.ser.readline().decode('utf-8').rstrip()
            # self.latest_data_temp, self.latest_data_humd = map(float, line.split(' '))
            line = self.ser.readline().decode('utf-8').rstrip()
            if not line:
                return
            data = json.loads(line)
            if not data:    
                return
            if data.get("temperature") == self.latest_data_temp and \
               data.get("humidity") == self.latest_data_humd and \
                data.get("eco2") == self.latest_data_eco2 and \
                data.get("tvoc") == self.latest_data_tvoc and \
                data.get("aqi") == self.latest_data_aqi:
                return
            self.latest_data_temp = data.get("temperature", 0.0)
            self.latest_data_humd = data.get("humidity", 0.0)
            self.latest_data_eco2 = data.get("eco2", 0.0)
            self.latest_data_tvoc = data.get("tvoc", 0.0)
            self.latest_data_aqi = data.get("aqi", 0.0)
            print(f"Temperature: {self.latest_data_temp}, Humidity: {self.latest_data_humd}, eCO2: {self.latest_data_eco2}, TVOC: {self.latest_data_tvoc}, AQI: {self.latest_data_aqi}")
            self.send_data()
    
    def send_data(self):
        url = self.write_url + f"&field1={self.latest_data_temp}&field2={self.latest_data_humd}&field3={self.latest_data_eco2}&field4={self.latest_data_tvoc}&field5={self.latest_data_aqi}"
        response = requests.get(url)
        print(f"Data sent to {url}, response status: {response.status_code}")

if __name__ == "__main__":
    hub = Hub(port='COM14', baudrate=115200, timeout=1)
    print("Starting data read...")
    
    while True:
        hub.read_data()