# server.py
from multiprocessing.connection import Listener
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
# Configuration
sender_email = os.getenv("SENDER_EMAIL")
recipient_email = os.getenv("RECIPIENT_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
address = ('localhost', 5000)
DIGEST_INTERVAL_MINUTES = 1  # Configurable interval

# Message storage
message_store = []
last_digest_time = time.time()  # Track when the last digest was sent

def should_send_digest():
    """Check if it's time to send a digest"""
    global last_digest_time
    elapsed_minutes = (time.time() - last_digest_time) / 60
    return elapsed_minutes >= DIGEST_INTERVAL_MINUTES

def send_digest():
    """Send a digest email with all stored messages"""
    global message_store, last_digest_time
    
    if not message_store:
        print("No messages to send in digest")
        return False
    
    # Create digest content
    action_items = [msg for msg in message_store if msg['Type'] == 'action']
    event_items = [msg for msg in message_store if msg['Type'] == 'event']
    
    digest_text = f"DIGEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # Add actions section
    digest_text += f"ACTIONS ({len(action_items)}):\n"
    digest_text += "=" * 50 + "\n"
    for item in action_items:
        digest_text += f"[{item['Date']}] {item['detail']}\n"
    digest_text += "\n\n"
    
    # Add events section
    digest_text += f"EVENTS ({len(event_items)}):\n"
    digest_text += "=" * 50 + "\n"
    for item in event_items:
        digest_text += f"[{item['Date']}] {item['detail']}\n"
    
    # Send the digest
    try:
        send_email("Activity Digest", digest_text)
        print(f"Digest sent with {len(message_store)} items")
        message_store = []  # Clear the message store after sending
        last_digest_time = time.time()  # Reset the timer
        return True
    except Exception as e:
        print(f"Failed to send digest: {e}")
        return False

def send_email(subject, body):
    """Send an email with the given subject and body"""
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.login(sender_email, email_password)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body))
    
    mailserver.sendmail(sender_email, recipient_email, msg.as_string())
    mailserver.quit()

def read_request():
    """Listen for and process incoming connections"""
    with Listener(address) as listener:
        print(f"Server started. Digest interval: {DIGEST_INTERVAL_MINUTES} minutes")
        
        while True:
            try:
                # Check if it's time to send a digest
                if should_send_digest():
                    send_digest()
                
                # Set a timeout so we can periodically check for digest timing
                # even if no messages are coming in
                listener._listener._socket.settimeout(1)  # Check every minute
                try:
                    with listener.accept() as conn:
                        message = conn.recv()
                        print(f"Received: {message}")
                        
                        # Store the message
                        message_store.append(message)
                        
                        # Send confirmation back to client
                        conn.send(f"Message #{len(message_store)} received successfully")
                except TimeoutError:
                    # This is expected when no connections arrive within the timeout
                    pass
                
            except KeyboardInterrupt:
                print("Server shutting down.")
                if message_store:  # Send a final digest if messages exist
                    send_digest()
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    read_request()