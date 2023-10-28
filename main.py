import os
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import markdown
import tempfile
import webbrowser
import tkhtmlview

class MarkdownEditor:
    def __init__(self, root):
        self.root = root
        root.title("Markdown Editor")
        self.init_ui()
        self.project_folder = None
        self.selected_file_path = ""

    def init_ui(self):
        self.set_dark_theme()

        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Project", command=self.open_project)
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_command(label="Open in Browser", command=self.open_in_browser)

        self.root.config(menu=menu_bar)

        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        left_pane = tk.Frame(paned_window)
        paned_window.add(left_pane)

        right_pane = tk.Frame(paned_window)
        paned_window.add(right_pane)

        left_sidebar = tk.Frame(left_pane, width=200, bg='gray30')
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.file_list = tk.Listbox(left_sidebar, selectmode=tk.SINGLE, bg='gray30', fg='white')
        self.file_list.pack(fill=tk.Y)

        self.editor = ScrolledText(left_pane, wrap=tk.WORD, bg='gray10', fg='white', insertbackground='white', selectbackground='blue')
        self.editor.pack(fill=tk.BOTH, expand=True)

        self.output_term = ScrolledText(left_pane, wrap=tk.WORD, height=10, bg='gray10', fg='white')
        self.output_term.pack(fill=tk.BOTH, expand=True)

        self.file_list.bind('<Double-Button-1>', self.open_selected_file)

        self.root.bind("<Control-o>", lambda event: self.open_project())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-F1>", lambda event: self.create_new_file())
        self.root.bind("<F2>", lambda event: self.rename_selected_file())
        self.root.bind("<Control-a>", lambda event: self.select_all())

        self.preview_frame = tkhtmlview.HTMLLabel(right_pane, bg='gray10', fg='white')
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

    def set_dark_theme(self):
        self.root.tk_setPalette(background='#1e1e1e', foreground='white')

    def set_dark_file_dialog(self):
        filedialog.settings = {
            'background': '#1e1e1e',
            'foreground': 'white',
            'selectBackground': 'blue',
            'selectForeground': 'white',
            'fieldBackground': '#1e1e1e',
            'fieldForeground': 'white',
            'fieldText': 'white',
            'borderColor': 'white',
        }

    def open_project(self):
        self.set_dark_file_dialog()  # Set dark mode for file dialog
        folder = filedialog.askdirectory()
        if folder:
            self.project_folder = folder
            self.file_list.delete(0, tk.END)
            for file in os.listdir(folder):
                self.file_list.insert(tk.END, file)
            self.output_term.insert(tk.INSERT, f"Opened project in {folder}\n")

    def open_selected_file(self, event):
        selected_file = self.file_list.get(self.file_list.curselection())
        if os.path.isdir(selected_file):
            self.open_project(selected_file)
        elif self.project_folder:
            with open(os.path.join(self.project_folder, selected_file), "r") as f:
                self.clear_text_widget(self.editor)
                self.editor.insert(tk.INSERT, f.read())
                self.output_term.insert(tk.INSERT, f"Opened file: {selected_file}\n")
                self.selected_file_path = selected_file
                self.update_preview()
        else:
            self.output_term.insert(tk.INSERT, "No project folder selected. Please open a project first.\n")

    def save_file(self):
        if self.project_folder and self.selected_file_path:
            with open(os.path.join(self.project_folder, self.selected_file_path), "w") as f:
                file_content = self.editor.get("1.0", tk.END)
                f.write(file_content)
                self.output_term.insert(tk.INSERT, f"Saved file: {self.selected_file_path}\n")
                self.update_preview()
        else:
            self.output_term.insert(tk.INSERT, "No project folder selected or no file selected. Please open a project and select a file to save.\n")

    def create_new_file(self):
        if self.project_folder:
            file_name = filedialog.asksaveasfilename(defaultextension=".md", initialdir=self.project_folder)
            if file_name:
                with open(file_name, "w") as f:
                    self.clear_text_widget(self.editor)
                    self.selected_file_path = os.path.basename(file_name)
                    self.file_list.insert(tk.END, self.selected_file_path)
                    self.selected_file_path = file_name
                    self.output_term.insert(tk.INSERT, f"Created new file: {self.selected_file_path}\n")
                    self.update_preview()
        else:
            self.output_term.insert(tk.INSERT, "No project folder selected. Please open a project first.\n")

    def rename_selected_file(self):
        if self.project_folder and self.selected_file_path:
            new_file_name = filedialog.asksaveasfilename(defaultextension=".md", initialdir=self.project_folder)
            if new_file_name:
                new_file_path = os.path.join(self.project_folder, os.path.basename(new_file_name))
                os.rename(os.path.join(self.project_folder, self.selected_file_path), new_file_path)
                self.selected_file_path = os.path.basename(new_file_path)
                self.output_term.insert(tk.INSERT, f"Renamed file to: {self.selected_file_path}\n")
                self.open_project(self.project_folder)
                self.update_preview()
        else:
            self.output_term.insert(tk.INSERT, "No project folder selected or no file selected. Please open a project and select a file to rename.\n")

    def select_all(self):
        self.editor.tag_add("sel", "1.0", tk.END)

    def clear_text_widget(self, text_widget):
        text_widget.delete("1.0", tk.END)

    def update_preview(self):
        markdown_text = self.editor.get("1.0", tk.END)
        html_output = markdown.markdown(markdown_text)
        self.preview_html = html_output
        self.show_preview()

    def show_preview(self):
        if hasattr(self, 'preview_html'):
            self.preview_frame.set_html(self.preview_html)

    def open_in_browser(self):
        if hasattr(self, 'preview_html'):
            temp_dir = tempfile.mkdtemp()
            temp_html_path = os.path.join(temp_dir, "preview.html")
            with open(temp_html_path, "w") as f:
                f.write(self.preview_html)
            webbrowser.open(temp_html_path, new=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditor(root)
    root.mainloop()
