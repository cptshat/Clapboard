import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip
import re  # For text formatting


class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")

        self.history = []

        # Clipboard History Listbox
        self.history_listbox = tk.Listbox(root, width=80, height=15)
        self.history_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons Frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        # Copy Button
        copy_button = tk.Button(button_frame, text="Copy Selected", command=self.copy_selected)
        copy_button.pack(side=tk.LEFT, padx=5)

        # Clear Button
        clear_button = tk.Button(button_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Format Menu Button
        format_button = tk.Menubutton(button_frame, text="Format Text")
        format_menu = tk.Menu(format_button, tearoff=0)
        format_menu.add_command(label="Remove Extra Spaces", command=self.remove_extra_spaces)
        format_menu.add_command(label="Convert to Plain Text", command=self.convert_to_plain_text)
        format_button['menu'] = format_menu
        format_button.pack(side=tk.LEFT, padx=5)

        # Bottom Frame (For Display Area)
        display_frame = tk.Frame(root)
        display_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Text Area
        self.display_area = scrolledtext.ScrolledText(display_frame, height=5, wrap=tk.WORD, state=tk.DISABLED)
        self.display_area.pack(fill=tk.BOTH, expand=True)

        # Key binding to update display on selection
        self.history_listbox.bind('<<ListboxSelect>>', self.update_display_area)

        # Start listening to the clipboard
        self.listen_clipboard()

    def listen_clipboard(self):
        try:
            clipboard_content = pyperclip.paste()
        except pyperclip.PyperclipException:
            # This usually happens when no X server or wayland compositor available
            messagebox.showwarning("Clipboard Access Error", "Clipboard access is not available. Clipboard changes will not be tracked.")
            self.root.after(1000, self.listen_clipboard) # retry with a short timeout
            return

        if clipboard_content and clipboard_content not in self.history:
            self.history.insert(0, clipboard_content)
            self.history_listbox.insert(0, clipboard_content[:100] + "..." if len(clipboard_content) > 100 else clipboard_content)
        self.root.after(500, self.listen_clipboard) # Check clipboard every 500 milliseconds

    def copy_selected(self):
        selected_indices = self.history_listbox.curselection()
        if selected_indices:
            selected_text = self.history[selected_indices[0]]
            pyperclip.copy(selected_text)
            messagebox.showinfo("Copied", "Text copied to clipboard")

    def clear_history(self):
        self.history.clear()
        self.history_listbox.delete(0, tk.END)
        self.display_area.config(state=tk.NORMAL) # Change text area to normal to allow text clear
        self.display_area.delete(1.0, tk.END)
        self.display_area.config(state=tk.DISABLED)

    def update_display_area(self, event):
        selected_indices = self.history_listbox.curselection()
        if selected_indices:
            selected_text = self.history[selected_indices[0]]
            self.display_area.config(state=tk.NORMAL) # Change text area to normal to allow write
            self.display_area.delete(1.0, tk.END)
            self.display_area.insert(tk.END, selected_text)
            self.display_area.config(state=tk.DISABLED) # Change text area to disabled to prevent accidental edits

    def remove_extra_spaces(self):
        selected_indices = self.history_listbox.curselection()
        if selected_indices:
            selected_text = self.history[selected_indices[0]]
            formatted_text = re.sub(r'\s+', ' ', selected_text).strip()
            self.history[selected_indices[0]] = formatted_text
            self.update_history_listbox(selected_indices[0], formatted_text)
            self.update_display_area(None) # Force the display to update with the new text

    def convert_to_plain_text(self):
       selected_indices = self.history_listbox.curselection()
       if selected_indices:
           selected_text = self.history[selected_indices[0]]
           formatted_text = re.sub(r'<[^>]*>', '', selected_text) # Remove HTML/XML tags
           formatted_text = formatted_text.replace('\n', '')  # Remove newlines
           self.history[selected_indices[0]] = formatted_text
           self.update_history_listbox(selected_indices[0], formatted_text)
           self.update_display_area(None) # Force the display to update with the new text

    def update_history_listbox(self, index, new_text):
         text_preview = new_text[:100] + "..." if len(new_text) > 100 else new_text
         self.history_listbox.delete(index)
         self.history_listbox.insert(index, text_preview)


if __name__ == "__main__":
    root = tk.Tk()
    manager = ClipboardManager(root)
    root.mainloop()
