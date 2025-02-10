from tkinter import Tk, Frame
from Sidebar import Sidebar
from login import LoginScreen
from dashboard import DashboardScreen
from members import MemberScreen  # Import the DashboardScreen

def show_dashboard(content_frame):
    # Initialize the DashboardScreen in the content frame
    dashboard_screen = DashboardScreen(content_frame)
    dashboard_screen.update_metrics(120, 45, 15, 3)  # Example metrics (replace with API later)

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
    LoginScreen(content_frame, on_success_callback=lambda: show_dashboard(content_frame))

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
