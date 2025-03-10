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
# SENDER_EMAIL, RECIPIENT_EMAIL, EMAIL_PASSWORD are in .env
sender_email = os.getenv("SENDER_EMAIL")
recipient_email = os.getenv("RECIPIENT_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
address = ('localhost', 5000)
DIGEST_INTERVAL_MINUTES = 1  # Configurable interval

# Messages are stored in a list.
message_store = []
last_digest_time = time.time()  # Track when the last digest was sent

def should_send_digest():
    """Check if it's time to send a digest."""
    global last_digest_time
    return (time.time() - last_digest_time) / 60 >= DIGEST_INTERVAL_MINUTES

def build_digest_text(action_items, event_items):
    """Create digest content. Add actions section. Add events section."""
    dt = f"DIGEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    dt += f"ACTIONS ({len(action_items)}):\n{'='*50}\n"
    for i in action_items: dt += f"[{i['Date']}] {i['detail']}\n"
    dt += f"\n\nEVENTS ({len(event_items)}):\n{'='*50}\n"
    for i in event_items: dt += f"[{i['Date']}] {i['detail']}\n"
    return dt

def send_digest():
    """Send a digest email with all stored messages. No messages to send in digest.
    Create digest content. Send the digest. Clear the message store after sending. Reset the timer."""
    global message_store, last_digest_time
    if not message_store: print("No messages to send in digest");return False
    acts=[m for m in message_store if m['Type']=='action']
    evts=[m for m in message_store if m['Type']=='event']
    try:
        send_email("Activity Digest", build_digest_text(acts, evts))
        print(f"Digest sent with {len(message_store)} items")
        message_store=[]; last_digest_time=time.time()
        return True
    except Exception as e:
        print(f"Failed to send digest: {e}")
        return False

def send_email(subject, body):
    """Send an email with the given subject and body."""
    s=smtplib.SMTP('smtp.gmail.com',587); s.ehlo(); s.starttls(); s.login(sender_email,email_password)
    m=MIMEMultipart(); m['From']=sender_email; m['To']=recipient_email; m['Subject']=subject
    m.attach(MIMEText(body)); s.sendmail(sender_email,recipient_email,m.as_string()); s.quit()

def process_connection(l):
    """Set a timeout so we can periodically check for digest timing even if no messages
    are coming in. This is expected when no connections arrive within the timeout.
    Append the message to the list. Send confirmation back to client."""
    try:
        c=l.accept(); m=c.recv(); print(f"Received: {m}")
        message_store.append(m)
        c.send(f"Message #{len(message_store)} received successfully")
        c.close()
    except TimeoutError:
        pass

def handle_incoming_connections(l):
    """Check if it's time to send a digest. Server is shutting down. 
    Set a timeout so we can periodically check for digest timing."""
    while True:
        try:
            if should_send_digest(): send_digest(); l._listener._socket.settimeout(1)
            process_connection(l)
        except KeyboardInterrupt: 
            print("Server shutting down.")
            if message_store: send_digest()
            break
        except Exception as e:
            print(f"Error: {e}")

def read_request():
    """Listen for and process incoming connections. Server is shutting down expell 
    all messages by sending one last digest."""
    with Listener(address) as l:
        print(f"Server started. Digest interval: {DIGEST_INTERVAL_MINUTES} minutes")
        handle_incoming_connections(l)

if __name__ == "__main__":
    read_request()
