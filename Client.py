import socket
import threading
import tkinter as tk
from queue import Queue

# Initialize the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('192.168.48.196', 3000)
client_socket.connect(server_address)

# Declare entry_username and btn_username as global variables
entry_username = None
btn_username = None
text_display = None  # Variable to store a reference to the Text widget for displaying messages
message_queue = Queue()  # Queue to store messages received from the server

def receive_messages():
    """ Receives messages from the server and adds them to the message queue. """
    global message_queue
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Disconnected from the server.")
                client_socket.close()
                break

            message_queue.put(message)  # Put the message into the queue

        except OSError:
            break
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            break

    # Periodically check for new messages
    text_display.after(1000, receive_messages)

def process_message_queue():
    """ Process messages from the queue and update the text widget. """
    global text_display
    while True:
        try:
            message = message_queue.get(block=False)
            text_display.config(state=tk.NORMAL)
            text_display.insert(tk.END, message + '\n')
            text_display.config(state=tk.DISABLED)
            text_display.yview(tk.END)  # Auto-scroll to the bottom

        except queue.Empty:
            break
        except Exception as e:
            print(f"Error processing message queue: {e}")

    # Schedule the next call to process_message_queue
    text_display.after(100, process_message_queue)

def get_username():
    global entry_username, btn_username, text_display
    username = entry_username.get()
    if username:
        client_socket.send(username.encode())
        entry_username.config(state=tk.DISABLED)
        btn_username.config(state=tk.DISABLED)

def send_message(entry):
    try:
        answer = entry.get()
        client_socket.send(answer.encode())
        entry.delete(0, tk.END)
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    global entry_username, btn_username, text_display  # Declare entry_username, btn_username, and text_display as global variables
    # Create GUI window
    root = tk.Tk()
    root.title("Chat Client")

    # Username input
    label_username = tk.Label(root, text="Enter your username:")
    label_username.pack()

    entry_username = tk.Entry(root)
    entry_username.pack()

    btn_username = tk.Button(root, text="Submit Username", command=get_username)
    btn_username.pack()

    # Message display
    text_display = tk.Text(root, state=tk.DISABLED)
    text_display.pack()

    # Message input
    label_answer = tk.Label(root, text="Your answer:")
    label_answer.pack()

    entry_answer = tk.Entry(root)
    entry_answer.pack()

    entry_answer.bind("<Return>", lambda event, entry=entry_answer: send_message(entry))

    btn_send = tk.Button(root, text="Send", command=lambda entry=entry_answer: send_message(entry))
    btn_send.pack()

    # Start the thread to receive messages from the server
    threading.Thread(target=receive_messages).start()

    # Start the thread to process the message queue
    threading.Thread(target=process_message_queue).start()

    root.mainloop()

    # Close the socket when the GUI is closed
    client_socket.close()

if __name__ == "__main__":
    main()
