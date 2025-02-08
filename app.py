from telethon import TelegramClient, events, Button, functions
import os
import logging

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

# Replace with actual API credentials from https://my.telegram.org
api_id = 20315645
api_hash = '4b643a7d1ab5a3171aa4c3046b21973a'

roll_number_to_user_id = {
    "101": 703761568,  # Example: roll number mapped to a phone number
    # "102": "+0987654321",
    # "103": "+1122334455"
}
logging.info("Starting Telegram Bot...")

enqno = 0
LOCK = True  # Assuming LOCK is defined elsewhere
attendance_lock = False

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

@client.on(events.NewMessage())
async def grpmessage(event):
    global attendance_lock

    logging.debug(f"Received message: {event.message.message} with {attendance_lock} ")

    if LOCK:
        if "result" in event.message.message:
            logging.info("Detected 'result' in message. Sending expected response.")
            await client.send_message(event.chat_id, "Expecting in 2 weeks")
        elif event.message.message == '/start':
            sender = await event.get_sender()
            user_id = sender.id  # Get the user's unique Telegram ID
            logging.info(f"User {sender.id} started the bot.")
            await event.respond(f"Hello! Your Telegram User ID is: {user_id}")
            logging.info("User sent /start command. Showing menu options.")
            await client.send_message(event.chat_id, "Choose an option:", buttons=keyboard)
        elif event.message.message.lower() in ['', 'poda', 'podi']:
            sender = await event.get_sender()
            logging.warning(f"User {sender.id} used a banned word. Attempting to kick.")
            try:
                msg = await client.kick_participant(event.chat_id, sender.id)
                await msg.delete()
                logging.info(f"User {sender.id} was removed from the chat.")
            except Exception as e:
                logging.error(f"Failed to kick user {sender.id}: {e}")

    if attendance_lock:
        message_text = event.message.message.strip()
        if message_text:
            absentees = [a.strip() for a in message_text.split(",")]
            logging.info(f"Marking absentees: {absentees}")
            await client.send_message(event.chat_id, f"Following roll nos are added as absentees and Notifications are sent to parents: {'  '.join(absentees)}")
            for roll_no in absentees:
                if roll_no in roll_number_to_user_id:
                    user_identifier = roll_number_to_user_id[roll_no]
                    try:
                        await client.send_message(user_identifier, f"Your ward (Roll No: {roll_no}) is marked absent today.")
                        logging.info(f"Sent notification to {user_identifier} for Roll No: {roll_no}")
                    except Exception as e:
                        logging.error(f"Failed to send message to {user_identifier}: {e}")
                else:
                    logging.warning(f"No contact found for Roll No: {roll_no}")
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
