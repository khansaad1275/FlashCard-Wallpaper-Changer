import os
import random
import ctypes
import requests
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Import PIL for image handling
from io import BytesIO
import threading  # For parallel downloads

# Define the path to your wallpaper folder
wallpaper_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Flash Cards")

# Function to download images in the background
def download_images():
    # Download 5 random images from Lorem Picsum
    for i in range(5):
        image_url = f"https://picsum.photos/1920/1080?random={i}"  # URL for random images
        try:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_path = os.path.join(wallpaper_folder, f"image_{i+1}.jpg")
                with open(image_path, 'wb') as file:
                    file.write(image_response.content)
                    print(f"Downloaded: image_{i+1}.jpg")
        except Exception as e:
            print(f"Error downloading image {i+1}: {e}")

# Function to create a guided walkthrough GUI
def start_walkthrough():
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.title("Wallpaper Changer Setup Guide")
    root.geometry("350x380")  # More compact size

    # Define a better font style
    font_style = ("Arial", 11, "bold")

    # Icons URLs for each step
    icons_urls = [
        "https://cdn-icons-png.flaticon.com/512/2383/2383605.png",
        "https://cdn-icons-png.flaticon.com/512/1160/1160158.png",
        "https://cdn-icons-png.flaticon.com/512/3208/3208758.png",
        "https://cdn-icons-png.flaticon.com/512/1549/1549292.png",
        "https://cdn-icons-png.flaticon.com/512/190/190411.png"
    ]

    # Function to fetch icons from the provided URLs
    def fetch_icon(url):
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data)).resize((50, 50))
        return ImageTk.PhotoImage(img)

    # Fetch icons for the tutorial steps
    icons = [fetch_icon(url) for url in icons_urls]

    # Set window icon to the "Welcome" icon
    root.iconphoto(False, icons[0])

    # Initialize notebook (tabbed interface)
    notebook = ttk.Notebook(root)

    # Frames with content and icons
    steps = [
        ("Welcome", "Welcome to the Wallpaper Changer Tool!\n\nThis guide will help you set up and use the tool.", icons[0]),
        ("Step 1: Folder", "The tool needs a 'Flash Cards' folder to store wallpapers.\n\nIf it doesn't exist, we will create it for you.", icons[1]),
        ("Step 2: Download", "We will download 5 random wallpapers from the internet to get you started.\n\nThis may take a moment.", icons[2]),
        ("Step 3: Change Wallpaper", "Once the wallpapers are ready, the tool will randomly change your desktop wallpaper.\n\nEnjoy a new look every time!", icons[3]),
        ("Done", "Setup Complete!\n\nYou're ready to use the Wallpaper Changer Tool.", icons[4])
    ]

    # Create frames and add to notebook
    for step in steps:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=step[0])
        
        # Display icon
        icon_label = ttk.Label(frame, image=step[2])
        icon_label.image = step[2]  # Keep a reference to avoid garbage collection
        icon_label.pack(pady=10)
        
        # Display text
        step_label = ttk.Label(
            frame,
            text=step[1],
            wraplength=300,
            justify="center",
            font=font_style
        )
        step_label.pack(pady=10)

    # Pack and run the notebook
    notebook.pack(expand=True, fill='both')

    # Navigation Buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=10)  # Position buttons at the bottom

    def next_page():
        current = notebook.index(notebook.select())
        if current < notebook.index("end") - 1:
            notebook.select(current + 1)
        else:
            root.destroy()  # Close the window on "Finish"

    def previous_page():
        current = notebook.index(notebook.select())
        if current > 0:
            notebook.select(current - 1)

    # Add > icon to the "Next" button
    next_button = ttk.Button(button_frame, text="Next >", command=next_page)
    back_button = ttk.Button(button_frame, text="Back", command=previous_page)
    skip_button = ttk.Button(button_frame, text="Skip", command=root.destroy)  # Close the window on "Skip"

    back_button.grid(row=0, column=0, padx=5)
    skip_button.grid(row=0, column=1, padx=5)
    next_button.grid(row=0, column=2, padx=5)

    # Configure button text for "Finish" on the last page
    def update_button_text(event):
        current = notebook.index(notebook.select())
        if current == notebook.index("end") - 1:
            next_button.config(text="Finish")
        else:
            next_button.config(text="Next >")

    notebook.bind("<<NotebookTabChanged>>", update_button_text)

    root.mainloop()

# Function to get the current wallpaper
def get_current_wallpaper():
    buffer = ctypes.create_unicode_buffer(512)
    ctypes.windll.user32.SystemParametersInfoW(0x73, len(buffer), buffer, 0)
    return buffer.value

# Get the current wallpaper
current_wallpaper = get_current_wallpaper()

# Check if the folder exists
if not os.path.exists(wallpaper_folder):
    # Create the folder first
    os.makedirs(wallpaper_folder)
    print(f"Created folder: {wallpaper_folder}")

    # Start downloading images in a separate thread
    threading.Thread(target=download_images).start()

    # Show the guided walkthrough
    start_walkthrough()

else:
    print("Flash Cards folder already exists. Skipping setup.")

# List all files in the folder
all_files = os.listdir(wallpaper_folder)

# Filter out image files (jpg, png, bmp, jpeg, gif)
image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif'))]

# Check if there are any valid image files
if not image_files:
    print(f"No images found in folder: {wallpaper_folder}")
    sys.exit()  # Use sys.exit() instead of exit()

# Select a random image that is different from the current wallpaper
random_image = None
while True:
    random_image_candidate = random.choice(image_files)
    random_image_path = os.path.join(wallpaper_folder, random_image_candidate)
    
    # Check if the selected image is not the current wallpaper
    if random_image_path != current_wallpaper:
        random_image = random_image_candidate
        break

# Change the wallpaper using ctypes
ctypes.windll.user32.SystemParametersInfoW(20, 0, random_image_path, 3)
print(f"Wallpaper changed to: {random_image_path}")
