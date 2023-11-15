import socket
import threading
import tkinter as tk

# Initialize the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('192.168.1.2', 3000)
client_socket.connect(server_address)

def receive_messages(sock, text_widget):
    """ Receives messages from the server and updates the UI. """
    while True:
        try:
            message = sock.recv(1024).decode().lower()
            if not message:
                print("Disconnected from server.")
                sock.close()
                break
            text_widget.insert(tk.END, message + "\n")
        except OSError:  # Possibly client has left the game.
            break
        except Exception as e:
            print(f"Error: {e}")
            sock.close()
            break

def send_answer(entry, sock):
    """ Sends the answer to the server. """
    answer = entry.get()
    sock.send(answer.lower().encode())
    entry.delete(0, tk.END)  # Clear the entry field

def main():
    # Send username to the server
    username = input("Enter your username:")
    client_socket.send(username.encode())

    # Create the UI window
    root = tk.Tk()
    root.title("Quiz Game")

    # Create a text widget to display messages
    text_widget = tk.Text(root, height=10, width=40)
    text_widget.pack()

    # Create an entry widget for the answer
    entry = tk.Entry(root, width=60)
    entry.pack()

    # Create a button to submit the answer
    submit_button = tk.Button(root, text="Submit", command=lambda: send_answer(entry, client_socket))
    submit_button.pack()

    # Start the thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client_socket, text_widget)).start()

    # Start the Tkinter main loop
    root.mainloop()

if _name_ == "_main_":
    main()
