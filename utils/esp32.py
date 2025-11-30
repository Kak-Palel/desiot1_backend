import serial
import serial.tools.list_ports # <-- FIX: Import the tool to list ports
import numpy as np
import json
import requests

class Esp32:
    # <-- FIX: Corrected the special method name from _init_ to __init__
    def __init__(self, port="auto", baudrate=115200, timeout=1, cache_size=100):
        """Initializes the serial connection."""
        if port == "auto":
            port = self.find_esp32_port()
            if not port:
                raise ValueError("No ESP32 device found. Please check the USB connection and ensure drivers are installed.")
        self.port = port

        try:
            self.ser = serial.Serial(self.port, baudrate, timeout=timeout)
            print(f"Successfully connected to {port}")
        except serial.SerialException as e:
            print(f"Error connecting to {port}: {e}")
            self.ser = None # Set ser to None if connection fails
        
        self.latest_data_temp = 0.0
        self.latest_data_humd = 0.0
        self.latest_data_eco2 = 0
        self.latest_data_tvoc = 0
        self.latest_data_aqi = 0

        self.cache_size = cache_size
        self.cache_temp = np.array([], dtype=dict)
        
        self.write_url = "https://api.thingspeak.com/update?api_key=E45QIV0OXGFP2V90"

    def get_latest_data(self):
        """Returns the latest sensor data."""
        return {
            "temperature": self.latest_data_temp,
            "humidity": self.latest_data_humd,
            "eco2": self.latest_data_eco2,
            "tvoc": self.latest_data_tvoc,
            "aqi": self.latest_data_aqi
        }
    
    def get_historical_data(self):
        """Returns historical data. This is a placeholder as the ESP32 does not store historical data."""
        # In a real application, you might want to implement a way to store and retrieve historical data.
        return self.cache_temp.tolist()  # Convert numpy array to list for easier handling

    def find_esp32_port(self):
        """Scans all available serial ports and returns the one connected to an ESP32."""
        print("Scanning for ESP32...")
        ports = serial.tools.list_ports.comports()
        
        # Common VID/PID for ESP32 USB-to-Serial chips
        # CP210x: VID=0x10C4, PID=0xEA60
        # CH340:  VID=0x1A86, PID=0x7523
        esp32_identifiers = [
            (0x10C4, 0xEA60),
            (0x1A86, 0x7523)
        ]

        for port in ports:
            # Check if the port's VID and PID match any of our known identifiers
            if (port.vid, port.pid) in esp32_identifiers:
                print(f"Found device with VID={port.vid}, PID={port.pid} on port {port.device}")
                return port.device # Return the device name, e.g., '/dev/ttyUSB0'

        return None # Return None if no matching device is found

    def read_data(self):
        # <-- FIX: Check if the serial object was successfully created
        if self.ser and self.ser.isOpen():
            try:
                line = self.ser.readline().decode('utf-8').rstrip()
                if not line:
                    return

                data = json.loads(line)
                
                # Update local data
                self.latest_data_temp = data.get("temperature", 0.0)
                self.latest_data_humd = data.get("humidity", 0.0)
                self.latest_data_eco2 = data.get("eco2", 0)
                self.latest_data_tvoc = data.get("tvoc", 0)
                self.latest_data_aqi = data.get("aqi", 0)
                
                print(f"Received -> Temp: {self.latest_data_temp:.1f}C, Hum: {self.latest_data_humd:.1f}%, eCO2: {self.latest_data_eco2}ppm, TVOC: {self.latest_data_tvoc}ppb, AQI: {self.latest_data_aqi}")
                
                # Send to ThingSpeak
                # self.send_data()

                # simple caching
                if len(self.cache_temp) < self.cache_size:
                    print(f"Adding data to cache: {data}")
                    self.cache_temp = np.append(self.cache_temp, data)
                else:
                    self.cache_temp = np.roll(self.cache_temp, -1)
                    self.cache_temp[-1] = data

                return data  # Return the data for further processing if needed
            except json.JSONDecodeError:
                # This can happen if the ESP32 sends incomplete data (e.g., during reset)
                print("Received incomplete or malformed JSON data. Skipping.")
            except UnicodeDecodeError:
                print("Received non-UTF-8 data. Skipping.")
    
    # def send_data(self):
    #     """Sends the latest data to ThingSpeak."""
    #     # ThingSpeak has a rate limit of about 15 seconds.
    #     # This code sends data every time it's read, so ensure your ESP32 sends data slowly.
        
    #     # Construct the URL with all fields
    #     url = (f"{self.write_url}&field1={self.latest_data_temp:.2f}"
    #            f"&field2={self.latest_data_humd:.2f}&field3={self.latest_data_eco2}"
    #            f"&field4={self.latest_data_tvoc}&field5={self.latest_data_aqi}")
        
    #     try:
    #         response = requests.get(url, timeout=5) # Add a timeout
    #         print(f"ThingSpeak response status: {response.status_code}")
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error sending data to ThingSpeak: {e}")

# <-- FIX: Corrected the special name from "_main_" to "__main__"
if __name__ == "__main__":
    # <-- FIX: Call the auto-detection function first
    esp32_port_name = find_esp32_port()
    
    if esp32_port_name:
        print(f"ESP32 found at: {esp32_port_name}")
        # Create the Hub instance with the found port
        hub = Esp32(port=esp32_port_name, baudrate=115200, timeout=1)
        
        print("Starting data reading loop...")
        while True:
            hub.read_data()
            
    else:
        print("Error: Could not find an ESP32 device.")
        print("Please check the USB connection and ensure drivers are installed.")