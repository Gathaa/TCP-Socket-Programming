import socket
import threading

# Initialize the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('192.168.1.2', 3000)
client_socket.connect(server_address)

def receive_messages(sock):
    """ Receives messages from the server and prints them. """
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                print("Disconnected from server.")
                sock.close()
                break
            print(message)
        except OSError:  # Possibly client has left the game.
            break
        except Exception as e:
            print(f"Error: {e}")
            sock.close()
            break

def main():
    # Send username to the server
    username = input("Enter your username:")
    client_socket.send(username.encode())

    # Start the thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Continuously read answers and send them to the server
    try:
        while True:
            answer = input()
            print()
            client_socket.send(answer.encode())
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
