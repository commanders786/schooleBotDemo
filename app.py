from telethon import TelegramClient, events, Button, functions
import os

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
# api_id = 20315645
# api_hash = '4b643a7d1ab5a3171aa4c3046b21973a'

api_id = 20315645
api_hash = '4b643a7d1ab5a3171aa4c3046b21973a'

enqno = 0
#5894568672:AAGwrjUr1Zkdvn9ei-OoPk-WcEMYydAbj64
LOCK = 1
# Create the client and connect to Telegram
client = TelegramClient('session_name', api_id, api_hash)
client.start()

attendance_lock = {}
LOCK = True  # Assuming LOCK is defined elsewhere

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
    
    if LOCK:
        if "result" in event.message.message:
            print(LOCK)
            await client.send_message(event.chat_id, "Expecting in 2 weeks")
            print(event.chat_id)
        elif event.message.message == '/start':
            await client.send_message(event.chat_id, "Choose an option:", buttons=keyboard)
        elif event.message.message.lower() in ['', 'poda', 'podi']:
            sender = await event.get_sender()
            print(sender.id)
            try:
                msg = await client.kick_participant(event.chat_id, sender.id)
                await msg.delete()
            except:
                print("admin error")
    
    elif attendance_lock:
        absentees = event.message.text.split(",")
        await client.send_message(event.chat_id, f"Following roll nos are added as absentees and Notifications are sent to parents: {'  '.join(absentees)}")
        attendance_lock = False

@client.on(events.CallbackQuery)
async def callback_query_handler(event):
    global attendance_lock
    
    if event.data == b"mark_attendance":
        attendance_lock = True
        await client.send_message(event.chat_id, "Please enter the roll numbers of absentees, separated by commas:")
    elif event.data == b"Materials":
        await client.send_message(event.chat_id, "Choose year:", buttons=[
            [Button.inline("S1", data=b"s1"), Button.inline("S2", data=b"s2")],
            [Button.inline("S3", data=b"s3"), Button.inline("S4", data=b"s4")]
        ])

client.run_until_disconnected()