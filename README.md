# Microservice_A_CS361
Microservice A for CS361.
## Requirements
- Python 3.6+
- Dependencies listed in `requirements.txt`

To run the program, you need to install the prerequisites. Uncomment some requirements if you wish to use a different email provider.  
```bash
pip install -r requirements.txt
```
Create your .env file by filling out  
```
EMAIL_PASSWORD=  
SENDER_EMAIL=  
RECIPIENT_EMAIL=
```
## 1. How to Programmatically REQUEST Data from the Microservice

To send data to the microservice, you need to:
1. Create a connection to the server
2. Format your message as a dictionary
3. Send the message using the connection

### Example Code

```python
from multiprocessing.connection import Client
from datetime import datetime

# Server connection details
address = ('localhost', 5000)

def sendData(data):
    """
    Send data to the action/event logger microservice.
    
    Parameters:
    - data: Dictionary with Date, Type, and detail keys
    
    Returns:
    - Server response message
    """
    with Client(address) as conn:
        conn.send(data)
        print(f"Sent message: {data}")
        print("Waiting for confirmation...")
        response = conn.recv()
        return response

# Example call
if __name__ == "__main__":
    # Create a message
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = {
        "Date": current_datetime,
        "Type": "action",  # Must be either "action" or "event"
        "detail": "Follow up with client about project timeline"
    }
    
    # Send to server
    response = sendData(message)
    print(f"Server response: {response}")
```

### Message Format

Each message must be a dictionary with these keys:
- `Date`: Timestamp string (format: "YYYY-MM-DD HH:MM:SS")
- `Type`: Either "action" or "event" (case-insensitive)
- `detail`: Description of the action or event

## 2. How to Programmatically RECEIVE Data from the Microservice

The microservice responds with a confirmation message after receiving your data. Here's how to receive and process this response:

### Example Code

```python
from multiprocessing.connection import Client

# Server connection details
address = ('localhost', 5000)

def sendAndReceive(message):
    """
    Send a message to the server and get the response.
    
    Parameters:
    - message: Dictionary containing the data to send
    
    Returns:
    - Server's confirmation message
    """
    with Client(address) as conn:
        # Send the data
        conn.send(message)
        
        # Wait for and return the response
        # This will block until the server sends a response
        response = conn.recv()
        return response

# Example call
if __name__ == "__main__":
    # Sample message
    message = {
        "Date": "2025-02-24 16:30:00",
        "Type": "event",
        "detail": "Weekly team meeting completed"
    }
    
    # Send and receive
    confirmation = sendAndReceive(message)
    print(f"Received from server: {confirmation}")
```

### Response Format

The server responds with a confirmation string:
```
Message #X received successfully
```

Where `X` is the number of the message in the current digest batch.

The data is in the inbox of whoever the data is being sent to.
To programatically read the data you must read your inbox.

### Example code to read inbox in gmail.
```
import imaplib
import email
import os


username = os.environ.get('GMAIL_USERNAME', 'your.email@gmail.com')
password = os.environ.get('GMAIL_PASSWORD', 'your-app-password')  # Use app password


mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(username, password)
mail.select('inbox')


_, data = mail.search(None, 'ALL')
latest_email_id = data[0].split()[-1]  # Get the latest email ID
_, msg_data = mail.fetch(latest_email_id, '(RFC822)')
msg = email.message_from_bytes(msg_data[0][1])


print(f"From: {msg.get('From')}")
print(f"Subject: {msg.get('Subject')}")
print(f"Date: {msg.get('Date')}")


if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            print(part.get_payload(decode=True).decode())
            break
else:
    print(msg.get_payload(decode=True).decode())

mail.logout()
```
