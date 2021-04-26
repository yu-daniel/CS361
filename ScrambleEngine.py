import tkinter as tk

from pexels_api import API
import requests
from PIL import ImageTk, Image

import urllib.request as urllib
from io import BytesIO

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()  # using Tkinter's grid system over pack

        # initiate the main toolbar
        self.toolbar = Toolbar(self)
        root.config(menu=self.toolbar)

        # add results area
        self.box = Box(self)

        # add buttons to the UI
        self.news = tk.Button(self, text="News")
        self.images = tk.Button(self, text="Images")
        self.videos = tk.Button(self, text="Videos")
        self.search_btn = tk.Button(self, text="Search")
        self.bored = tk.Button(self, text="I'm Feeling Bored")

        # add status bar
        self.status = tk.Label(text="Status messages will go here.", bg="#3463ad", fg="white")

        # add search field
        self.search = tk.Entry(self, width=100)
        self.search.insert(0, "Enter <keyword> to search...")
        self.search.bind("<Button-1>", self.search_text)            # bind mouse click to search field's placeholder
        self.search_btn.bind("<Button-1>", self.click_search)

        # position of objects (buttons, search entry, labels)
        self.news.grid(row=0, column=0, sticky=tk.W, padx=(10, 3), pady=7)
        self.images.grid(row=0, column=1, sticky=tk.W, padx=3, pady=7)
        self.videos.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)
        self.bored.grid(row=0, column=3, sticky=tk.W, padx=3, pady=7)

        # add search field, search button, and search results position
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))
        self.box.grid(row=2, column=0, columnspan=102, sticky=tk.W, padx=(10, 0), pady=7)

        # position of status bar
        self.status.grid(row=3, column=0, columnspan=102, sticky=tk.W, padx=(10, 0), pady=5)

    def delete_text(self, event):
        self.search.delete(0, tk.END)

    def add_text(self, event):
        self.search.delete(0, tk.END)
        self.search.insert(0, "Enter <keyword> to search...")

    def search_text(self, event):
        placeholder = self.search.get()

        if placeholder == "":
            root.focus()
            return

        if placeholder == "Enter <keyword> to search...":
            self.search.delete(0, tk.END)

        if placeholder != "Enter <keyword> to search...":
            self.search.insert(0, "Enter <keyword> to search...")
            root.focus()

    def click_search(self, event):
        # print("Search button pressed.")
        placeholder = self.search.get()

        if placeholder == "Enter <keyword> to search...":
            return
        else:
            keyword = self.search.get()
            print("keyword = ", keyword)
            self.image_api(keyword)

            self.search.delete(0, tk.END)
            self.search.insert(0, "Enter <keyword> to search...")
            root.focus()

    def image_api(self, keyword):
        temp_images = []

        # PEXELS_API_KEY = '563492ad6f91700001000001ecab8f7b0b9f4371b013fa9bc225c984'
        # api = API(PEXELS_API_KEY)
        # api.search('kitten', page=1, results_per_page=6)
        # images = api.get_entries()

        for img in range(6):
        # for img in images:

            # url_1 = "https://images.pexels.com/photos/416160/pexels-photo-416160.jpeg"
            url_1 = "https://drive.google.com/uc?id=1FumEJWkRjQ6DA7UevruTgnuINlmKThmQ"
            # response = requests.get(img.original)
            response = requests.get(url_1)

            im1 = Image.open(BytesIO(response.content)).resize((600, 600))
            temp_images.append(im1)


        self.box.set_images(temp_images)

class Toolbar(tk.Menu):
    def __init__(self, root):
        super().__init__(root)
        self.menu = tk.Menu(self)

        # file menu
        self.file = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="File")

        # view menu
        self.view = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="View")

        # help menu
        self.help = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Help")


class Box(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=660, height=500)

        self.images = []
        self.images_canvas = []

        for x in range(2):
            for y in range(3):
                print("Creating canvas: #", x)
                image = tk.Canvas(self, height=200, width=206)
                image.grid(row=x, column=y, sticky=tk.W, padx=(0, 15), pady=(0, 15))
                self.images_canvas.append(image)

    def set_images(self, img_set):
        total_img = len(img_set)

        # add images to canvas
        for x in range(total_img):

            self.img = ImageTk.PhotoImage(img_set[x])

            self.images.append(self.img)


            self.images_canvas[x].create_image(0, 0, image=self.img)
            self.images_canvas[x].image = self.img
            self.images_canvas[x].bind("<Button-1>", lambda event, arg=self.images[x]: self.enlarge_images(event, arg))


    def enlarge_images(self, event, arg):
        print("Arg = ", arg)

        image_window = tk.Toplevel(self)
        image_window.geometry("600x600")
        image_window.resizable(False, False)

        image_label = tk.Label(image_window, image=arg)
        image_label.grid(row=0, column=0)
        image_label.bind("<Button-1>", lambda event, arg=image_window: self.close_image(event, arg))

    def close_image(self, event, arg):
        arg.destroy()









if __name__ == '__main__':
    root = tk.Tk()
    root.title("Scramble Engine")  # add title to the app
    root.resizable(False, False)  # don't allow resizing window
    root.geometry("680x620")
    app = Main(root)  # initiate the main interface
    root.mainloop()  # keep Tkinter running
