import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import threading
import google.generativeai as genai
import re
import time

# --- Default Config ---
API_KEY = "AIzaSyACx1g9kuhtuJvJKuCJpw1lej3zaPEAWEY"
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

dark_mode = True

# --- Clean markdown formatting ---
def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

# --- Typing animation ---
def type_text(tag, text):
    chat_display.insert(tk.END, "\n", tag)
    for char in text:
        chat_display.insert(tk.END, char, tag)
        chat_display.see(tk.END)
        chat_display.update()
        time.sleep(0.005)

# --- Handle response ---
def fetch_response(prompt):
    try:
        chat_display.insert(tk.END, "\nGemini is thinking...\n", 'thinking')
        chat_display.see(tk.END)
        instruction = system_prompt.get() or "Answer concisely. Keep it simple."
        current_model = model_var.get()
        temp_model = genai.GenerativeModel(current_model)
        response = temp_model.generate_content([instruction, prompt])
        reply = clean_text(response.text.strip())
    except Exception as e:
        reply = f"[Error] {str(e)}"
    finally:
        chat_display.tag_delete('thinking')

    type_text('gemini', f"Gemini: {reply}\n")

# --- Send Message ---
def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return
    chat_display.insert(tk.END, f"\nYou: {user_input}\n", 'user')
    user_entry.delete(0, tk.END)
    chat_display.see(tk.END)
    threading.Thread(target=fetch_response, args=(user_input,), daemon=True).start()

# --- Upload PDF ---
def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return
    chat_display.insert(tk.END, f"\nYou uploaded: {file_path.split('/')[-1]}\n", 'user')
    chat_display.insert(tk.END, "\nGemini is reading the PDF...\n", 'gemini')
    chat_display.see(tk.END)
    try:
        uploaded_file = genai.upload_file(path=file_path)
        response = model.generate_content([uploaded_file, "Summarize this PDF simply."])
        reply = clean_text(response.text.strip())
    except Exception as e:
        reply = f"[Error reading PDF] {str(e)}"
    type_text('gemini', f"Gemini: {reply}\n")

# --- Clear Chat ---
def clear_chat():
    chat_display.delete(1.0, tk.END)

# --- Save Chat to File ---
def save_chat():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(chat_display.get(1.0, tk.END))
        messagebox.showinfo("Saved", f"Chat saved to {file_path}")

# --- Theme toggle ---
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg_color = "#1e1e1e" if dark_mode else "#f0f0f0"
    fg_color = "#D4D4D4" if dark_mode else "#000000"
    entry_bg = "#2d2d2d" if dark_mode else "white"

    root.configure(bg=bg_color)
    input_frame.configure(bg=bg_color)
    chat_display.configure(bg="#252526" if dark_mode else "white", fg=fg_color)
    user_entry.configure(bg=entry_bg, fg=fg_color)
    system_prompt.configure(bg=entry_bg, fg=fg_color)

# --- UI Setup ---
root = tk.Tk()
root.title("Gemini Chat - Pro AI Tool")
root.geometry("960x680")
root.configure(bg="#1e1e1e")

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 13),
    bg="#252526", fg="#D4D4D4", insertbackground="white", borderwidth=0)
chat_display.pack(padx=12, pady=(12, 6), fill=tk.BOTH, expand=True)
chat_display.tag_config('user', foreground='#4FC3F7')
chat_display.tag_config('gemini', foreground='#81C784')
chat_display.tag_config('thinking', foreground='orange')

input_frame = tk.Frame(root, bg="#1e1e1e")
input_frame.pack(fill=tk.X, padx=12, pady=(6, 8))

user_entry = tk.Entry(input_frame, font=("Consolas", 13), bg="#2d2d2d", fg="white",
    insertbackground="white", borderwidth=0, relief=tk.FLAT)
user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
user_entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(input_frame, text="Send", command=send_message,
    font=("Consolas", 12), bg="#007ACC", fg="white", padx=12, pady=6)
send_button.pack(side=tk.RIGHT)

upload_button = tk.Button(input_frame, text="📎 PDF", command=upload_pdf,
    font=("Consolas", 12), bg="#393939", fg="white", padx=10, pady=6)
upload_button.pack(side=tk.RIGHT, padx=(0, 10))

# --- Extra Controls ---
control_frame = tk.Frame(root, bg="#1e1e1e")
control_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

clear_btn = tk.Button(control_frame, text="🧹 Clear", command=clear_chat,
    font=("Consolas", 11), bg="#5e5e5e", fg="white")
clear_btn.pack(side=tk.LEFT, padx=4)

save_btn = tk.Button(control_frame, text="💾 Save", command=save_chat,
    font=("Consolas", 11), bg="#5e5e5e", fg="white")
save_btn.pack(side=tk.LEFT, padx=4)

theme_btn = tk.Button(control_frame, text="🌗 Toggle Theme", command=toggle_theme,
    font=("Consolas", 11), bg="#5e5e5e", fg="white")
theme_btn.pack(side=tk.LEFT, padx=4)

model_var = tk.StringVar(value="gemini-2.5-pro")
model_dropdown = ttk.Combobox(control_frame, textvariable=model_var, state="readonly",
    values=["gemini-2.5-pro", "gemini-2.5-flash"], font=("Consolas", 11), width=20)
model_dropdown.pack(side=tk.RIGHT, padx=4)

# --- System Prompt Input ---
system_prompt = tk.Entry(control_frame, font=("Consolas", 11), width=40)
system_prompt.insert(0, "Answer concisely. Keep it simple.")
system_prompt.pack(side=tk.RIGHT, padx=4)

root.mainloop()
