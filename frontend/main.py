import tkinter as tk
from Sidebar import Sidebar
from login import LoginScreen

def main():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("School Library System")
    root.geometry("800x600")  # Set window size

    # Create a frame for the main content area
    content_frame = tk.Frame(root)
    content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Initialize the sidebar for navigation
    Sidebar(root, content_frame)

    # Start with the Login screen
    LoginScreen(content_frame)

    root.mainloop()

if __name__ == "__main__":
    main()
