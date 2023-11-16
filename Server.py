import socket
import threading
import json
import time

def handle_client(client_socket, address, username):
    score = 0
    for question, options in questions_and_options:
        question_data = json.dumps({"question": question, "options": options})
        client_socket.send(f"Question:{question_data}".encode())
        client_socket.settimeout(30.0)
        
        try:
            answer = json.loads(client_socket.recv(1024).decode())
            if answer["answer"].lower() == answers[questions_and_options.index([question, options])].lower():
                score += 1
                client_socket.send("Correct!".encode())
            else:
                client_socket.send(f"Incorrect! Correct answer: {answers[questions_and_options.index([question, options])]}".encode())
            time.sleep(2)  # Small delay before next question
        except socket.timeout:
            client_socket.send(f"Time's up! The correct answer was {answers[questions_and_options.index([question, options])]}.".encode())
        except Exception as e:
            print(f"An error occurred with client {username}: {e}")
            break

    client_socket.send(f"Your final score is {score}".encode())
    client_socket.close()
    clients.remove((client_socket, address, username))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.51.65', 3000))
server_socket.listen(2)
print("Server initialized. Waiting for clients to connect...")

clients = []
questions_and_options = [
    ["What is the capital of France?", ["Paris", "Berlin", "London", "Madrid"]],
    ["Which planet is known as the Red Planet?", ["Mars", "Venus", "Jupiter", "Mercury"]],
    ["What is the largest mammal in the world?", ["Elephant", "Blue Whale", "Giraffe", "Lion"]],
    ["What element does 'O' represent on the periodic table?", ["Osmium", "Oxygen", "Gold", "Carbon"]],
    ["Who painted the Mona Lisa?", ["Vincent van Gogh", "Pablo Picasso", "Claude Monet", "Leonardo da Vinci"]]
]
answers = ["Paris", "Mars", "Blue Whale", "Oxygen", "Leonardo da Vinci"]

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")
    username = client_socket.recv(1024).decode().strip()
    print(f"{username} joined the game!")
    clients.append((client_socket, client_address, username))
    threading.Thread(target=handle_client, args=(client_socket, client_address, username)).start()
