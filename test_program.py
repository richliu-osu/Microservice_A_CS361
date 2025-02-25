# client.py
from multiprocessing.connection import Client
from datetime import datetime
address = ('localhost', 5000)
def inputData():
    while True:
        print("Type q anytime to exit.")
        while True:
            type_input = input("Enter Action or Event? ").lower()
            if type_input == 'q':
                print("Exiting the program.")
                exit()
            if type_input in ['action', 'event']:
                break
            else:
                print("Please enter either 'Action' or 'Event'.")

        detail_input = input("Enter details: ")
        if detail_input.lower() == 'q':
            print("Exiting the program.")
            exit()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {"Date": current_datetime, "Type": type_input, "detail": detail_input}
        print(message)
        sendData(message)

def sendData(data):
    with Client(address) as conn:
        conn.send(data)
        print(f"Sent message: {data}")
        print("Waiting for confirmation...")
        response = conn.recv()
        print(f"Server response: {response}")
        
if __name__ == "__main__":
    inputData()
