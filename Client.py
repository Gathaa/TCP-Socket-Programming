import tkinter as tk
from tkinter import messagebox, ttk
import socket
import threading
import json

class QuizClientUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Modern Quiz Client")
        self.master.geometry("800x600")
        self.master.config(bg="white")

        # Initialize socket
        self.client_socket = None

        # UI setup
        self.setup_ui()

        # Thread for listening to server messages
        self.listen_thread = None

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=10, font=("Helvetica", 14), background="#9400D3", foreground="white", borderwidth=0, highlightthickness=0)

        self.username_label = tk.Label(self.master, text="Enter your username:", font=("Helvetica", 16), bg="white", fg="black")
        self.username_label.pack(pady=(300, 10))

        self.username_entry = tk.Entry(self.master, font=("Helvetica", 14))
        self.username_entry.pack(pady=(20, 10))

        self.connect_button = tk.Button(self.master, text="     Connect     ", command=self.connect_to_server)
        self.connect_button.configure(bg="#9400D3", fg="white", font=("Helvetica", 14), pady=10, bd=0)
        self.connect_button.pack(pady=30)

        self.connection_label = tk.Label(self.master, text="", font=("Helvetica", 16), bg="white", fg="#9400D3")
        self.connection_label.pack(pady=40)

        self.attempt_button = tk.Button(self.master, text="Attempt Quiz", command=self.attempt_quiz)
        self.attempt_button.configure(bg="#9400D3", fg="white", font=("Helvetica", 14), pady=10, bd=0)

        self.options_frame = tk.Frame(self.master, bg="white")
        self.var_option = tk.StringVar()
        style.configure("TRadiobutton", font=("Helvetica", 14), background="white", foreground="black")

        self.option_radio_a = ttk.Radiobutton(self.options_frame, text="", variable=self.var_option, value="A", style="TRadiobutton", padding=(10, 5))
        self.option_radio_b = ttk.Radiobutton(self.options_frame, text="", variable=self.var_option, value="B", style="TRadiobutton", padding=(10, 5))
        self.option_radio_c = ttk.Radiobutton(self.options_frame, text="", variable=self.var_option, value="C", style="TRadiobutton", padding=(10, 5))
        self.option_radio_d = ttk.Radiobutton(self.options_frame, text="", variable=self.var_option, value="D", style="TRadiobutton", padding=(10, 5))

        self.option_radio_a.grid(row=0, column=0, padx=40, pady=(10, 0))
        self.option_radio_b.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.option_radio_c.grid(row=1, column=0, padx=10, pady=(10, 0))
        self.option_radio_d.grid(row=1, column=1, padx=10, pady=(10, 0))

        self.submit_button = tk.Button(self.master, text="Submit Answer", command=self.submit_answer)
        self.submit_button.configure(bg="#9400D3", fg="white", font=("Helvetica", 14), pady=10, bd=0)

        self.message_label = tk.Label(self.master, text="", font=("Helvetica", 14), bg="white", fg="#9400D3")

        self.question_label = tk.Label(self.master, text="Question:", font=("Helvetica", 18, "bold"), bg="white", fg="black")

        self.answer_status_label = tk.Label(self.master, text="", font=("Helvetica", 14), bg="white", fg="green")

        self.options_frame.pack_forget()
        self.submit_button.pack_forget()
        self.message_label.pack_forget()
        self.attempt_button.pack_forget()
        self.question_label.pack_forget()
        self.answer_status_label.pack_forget()

    def connect_to_server(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        try:
            server_address = ('192.168.51.65', 3000)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(server_address)
            self.client_socket.send(username.encode())

            self.listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
            self.listen_thread.start()

            self.update_connection_message("Connected successfully!")
            self.connect_button.config(state=tk.DISABLED)
            self.username_entry.config(state=tk.DISABLED)
            self.attempt_button.pack()

        except Exception as e:
            messagebox.showerror("Connection Error", f"Unable to connect to the server: {e}")
            self.update_connection_message("Connection failure!")

    def listen_to_server(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.process_server_message(message)
            except Exception as e:
                print(f"Error: {e}")
                break

    def process_server_message(self, message):
        if message.startswith("Question:"):
            question_data = json.loads(message[len("Question:"):])
            self.update_question_and_options(question_data)
        elif "Correct!" in message or "Incorrect!" in message:
            self.update_answer_status(message, "green" if "Correct!" in message else "red")
            time.sleep(1)  # Small delay before requesting the next question
            self.client_socket.send("request_question".encode())

    def attempt_quiz(self):
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.connect_button.pack_forget()
        self.connection_label.pack_forget()
        self.attempt_button.pack_forget()

        self.question_label.pack()
        self.options_frame.pack(pady=10)
        self.submit_button.pack(pady=(30, 20))
        self.message_label.pack()
        self.answer_status_label.pack()

        self.client_socket.send("request_question".encode())

    def submit_answer(self):
        answer = self.var_option.get().strip()
        if not answer:
            messagebox.showerror("Error", "Please select an answer.")
            return
        self.client_socket.send(json.dumps({"answer": answer}).encode())

    def update_connection_message(self, message):
        self.connection_label.config(text=message)

    def update_question_and_options(self, question_info):
        question = question_info["question"]
        options = question_info["options"]

        self.question_label.config(text=f"Question: {question}")
        self.option_radio_a.config(text=f"A: {options[0]}")
        
        self.option_radio_b.config(text=f"B: {options[1]}")
        self.option_radio_c.config(text=f"C: {options[2]}")
        self.option_radio_d.config(text=f"D: {options[3]}")

        self.var_option.set(None)  # Reset the selected option

    def update_answer_status(self, status, color):
        self.answer_status_label.config(text=status, fg=color)

def main():
    root = tk.Tk()
    app = QuizClientUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
