from tkinter import Tk, Frame
from Sidebar import Sidebar
from login import LoginScreen

def show_dashboard():
    print("Login successful! Redirecting to the dashboard...")  # Placeholder action

def main():
    # Create the main Tkinter window
    root = Tk()
    root.title("School Library System")
    root.geometry("800x600")  # Set window size

    # Create a frame for the main content area
    content_frame = Frame(root)
    content_frame.pack(side="right", fill="both", expand=True)

    # Initialize the sidebar for navigation
    Sidebar(root, content_frame)

    # Start with the Login screen
    LoginScreen(content_frame, on_success_callback=show_dashboard)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
