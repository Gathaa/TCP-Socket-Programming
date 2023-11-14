import socket
import threading
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.2', 3000))
server_socket.listen(2)  # Listen for 2 clients

print("Server initialized. Waiting for clients to connect...")

clients = []

questions = [
    {"question": "What is the capital of France?", "options": ["Paris", "Berlin", "London", "Madrid"], "answer": "Paris"},
    {"question": "Which planet is known as the Red Planet?", "options": ["Mars", "Venus", "Jupiter", "Mercury"], "answer": "Mars"},
    {"question": "What is the largest mammal in the world?", "options": ["Elephant", "Blue Whale", "Giraffe", "Lion"], "answer": "Blue Whale"},
    {"question": "What element does 'O' represent on the periodic table?", "options": ["Osmium", "Oxygen", "Gold", "Carbon"], "answer": "Oxygen"},
    {"question": "Who painted the Mona Lisa?", "options": ["Vincent van Gogh", "Pablo Picasso", "Claude Monet", "Leonardo da Vinci"], "answer": "Leonardo da Vinci"}
]


def handle_client(client_socket, address, username):
    score = 0
    for question_info in questions:
        question_text = question_info["question"]
        options = question_info["options"]
        correct_answer = question_info["answer"].lower()       
        # Send question and options to the specific client
        send_to_all_clients(f"{username}, {question_text}")
        send_to_all_clients(f"Options: {', '.join(options)}")
        client_socket.settimeout(30.0)
        try:
            client_answer = client_socket.recv(1024).decode().strip().lower()
            print(f"Received answer from {username}: {client_answer}")
            print(f"Correct answer: {correct_answer}")

            if client_answer == correct_answer or client_answer in options:
                send_to_all_clients(f"{username} answered correctly!")
                score += 1
            else:
                send_to_all_clients(f"{username} answered incorrectly. Correct answer: {correct_answer}")
        except socket.timeout:
            send_to_all_clients(f"{username}, time's up! The correct answer was {correct_answer}.")
        except Exception as e:
            print(f"An error occurred with client {username}: {e}")
            break
        time.sleep(2)

    client_socket.send(f"{username}, your final score is {score}".encode())
    client_socket.close()
    clients.remove((client_socket, address, username))

def send_to_all_clients(message):
    for client, _, _ in clients:
        try:
            client.send(message.encode())
        except:
            pass  # Ignore errors which are mostly due to closed connections

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    username = client_socket.recv(1024).decode().strip()
    print(f"{username} joined the game!")

    clients.append((client_socket, client_address, username))

    # Check if there is at least one client before starting the thread
    if len(clients) >= 1:
        send_to_all_clients("Game starting! Get ready for the quiz!")
        threading.Thread(target=handle_client, args=(clients[0][0], clients[0][1], clients[0][2])).start()
