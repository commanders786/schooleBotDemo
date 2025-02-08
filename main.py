from telethon import TelegramClient, events, Button, functions
import os
import logging
import json

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

# Replace with actual API credentials from https://my.telegram.org
api_id = 20315645
api_hash = '4b643a7d1ab5a3171aa4c3046b21973a'

# Load stored parent data from JSON
DATA_FILE = "parents_data.json"
DATA_FILE1="teacher_data.json"

def load_parent_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}
def load_teacher_data():
    if os.path.exists(DATA_FILE1):
        with open(DATA_FILE1, "r") as f:
            return json.load(f)
    return {}

def save_parent_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Dictionary to store roll numbers mapped to Telegram user IDs
teacherData = load_teacher_data()
parent_data = load_parent_data()
logging.info("Loaded parent data from JSON.")

enqno = 0
LOCK = True  # Assuming LOCK is defined elsewhere
attendance_lock = False
awaiting_rollno = {}  # Temporary storage for users who need to enter roll number

# Create the client and connect to Telegram
client = TelegramClient('session_name', api_id, api_hash)
client.start()
logging.info("Telegram Client started successfully.")

keyboard = [
    [
        Button.inline("Materials", data=b"Materials"),
        Button.url("Enquiry", "https://mail.google.com/mail/u/0/?fs=1&to=ktumcacommunity20@gmail.com&su=&body=&bcc=&tf=cm")
    ],
    [
        Button.inline("Mark Attendance", data=b"mark_attendance")
    ]
]

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = sender.id

    logging.info(f"User {user_id} started the bot.")
    if str(user_id) in teacherData:
        await client.send_message(event.chat_id, "Choose an option:", buttons=keyboard)
    # Check if the user is already registered
    elif str(user_id) in parent_data:
        roll_no = parent_data[str(user_id)]
        await event.respond(f"Welcome back! Your child is registered with Roll No: {roll_no}.")
        
    else:
        awaiting_rollno[user_id] = True
        await event.respond("Welcome! Please enter your child's Roll Number to register.")

@client.on(events.NewMessage())
async def grpmessage(event):
    global attendance_lock
    sender = await event.get_sender()
    user_id = sender.id
    message_text = event.message.message.strip()

    logging.debug(f"Received message from {user_id}: {message_text}")
    # Handle roll number registration
    if user_id in awaiting_rollno:
        
        if message_text=='/start':
            return
        elif not message_text.isdigit():  # Ensure roll number is numeric
            await event.respond("❌ Invalid Roll Number. Please enter a numeric value.")
            return
        

    # Handle roll number registration
    if user_id in awaiting_rollno:
        roll_no = message_text
        parent_data[str(user_id)] = roll_no  # Store roll number for this user
        save_parent_data(parent_data)  # Save to JSON file
        del awaiting_rollno[user_id]  # Remove from awaiting list

        await event.respond(f"Thank you! Your child is now registered with Roll No: {roll_no}.")
        logging.info(f"Registered user {user_id} with Roll No: {roll_no}")
        return  # Stop processing further

    # Handling attendance marking
    if attendance_lock:
        if message_text:
            absentees = [a.strip() for a in message_text.split(",")]
            logging.info(f"Marking absentees: {absentees}")

            await client.send_message(event.chat_id, f"Following roll nos are added as absentees and Notifications are sent to parents: {'  '.join(absentees)}")

            for roll_no in absentees:
                for parent_id, stored_roll in parent_data.items():
                    if stored_roll == roll_no:
                        try:
                            await client.send_message(int(parent_id), f"Your child (Roll No: {roll_no}) is marked absent today.")
                            logging.info(f"Sent notification to {parent_id} for Roll No: {roll_no}")
                        except Exception as e:
                            logging.error(f"Failed to send message to {parent_id}: {e}")

            attendance_lock = False
        else:
            logging.warning("Invalid input received for attendance.")
            await client.send_message(event.chat_id, "Invalid input. Please enter roll numbers separated by commas.")

@client.on(events.CallbackQuery)
async def callback_query_handler(event):
    global attendance_lock
    await event.answer("Processing...")
    logging.debug(f"Received Callback Query: {event.data}")

    if event.data == b"mark_attendance":
        attendance_lock = True
        logging.info("Mark attendance button clicked. Waiting for input.")
        await client.send_message(event.chat_id, "Please enter the roll numbers of absentees, separated by commas:")
    elif event.data == b"Materials":
        logging.info("Materials button clicked. Showing options.")
        await client.send_message(event.chat_id, "Choose year:", buttons=[
            [Button.inline("S1", data=b"s1"), Button.inline("S2", data=b"s2")],
            [Button.inline("S3", data=b"s3"), Button.inline("S4", data=b"s4")]
        ])

try:
    logging.info("Bot is now running. Waiting for messages...")
    client.run_until_disconnected()
except Exception as e:
    logging.critical(f"Bot encountered an error: {e}")
