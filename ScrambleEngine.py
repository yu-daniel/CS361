import tkinter as tk
from pexels_api import API
import requests
from PIL import ImageTk, Image
from io import BytesIO


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()  # using Tkinter's grid system over pack

        # initiate the main toolbar
        self.toolbar = Toolbar(self)
        root.config(menu=self.toolbar)

        # add results area

        # add access to status messages
        self.messenger = Messages()
        self.status_message = self.messenger.default

        # add status bar
        self.status = tk.Label(text=self.status_message, fg="#606060")

        # add buttons to the UI
        self.news = ColorButtons(self, text="News", message="This is the News button!", status_bar=self.status)
        self.images = ColorButtons(self, text="Images", message="This is the Images button!", status_bar=self.status)

        self.news.bind("<Button-1>", lambda arg=0: self.switch_page(0))
        self.images.bind("<Button-1>", lambda arg=1: self.switch_page(1))

        self.videos = ColorButtons(self, text="Videos", message="This is the Videos button!", status_bar=self.status)
        self.search_btn = ColorButtons(self, text="Search", message="This is the Search button!",
                                       status_bar=self.status)
        self.bored = ColorButtons(self, text="I'm Feeling Bored", message='This is the "Random" button!',
                                  status_bar=self.status)

        # RESULTS AREA
        self.container = tk.Frame(self, bg="black")

        self.image_results = ImageResults()
        self.news_results = NewsResults()

        self.frames = [self.news_results, self.image_results]

        # add search field
        self.search = tk.Entry(self, width=100, fg="#606060")
        self.search.insert(0, "Enter <keyword> to search...")
        self.search.bind("<Button-1>", self.search_text)  # bind mouse click to search field's placeholder
        self.search_btn.bind("<Button-1>", self.click_search)

        self.search.bind("<Enter>", lambda event, arg=self.messenger.search_field: self.update_message(arg))
        self.search.bind("<Leave>", lambda event, arg=self.messenger.default: self.update_message(arg))

        # position of objects (buttons, search entry, labels)
        self.news.grid(row=0, column=0, sticky=tk.W, padx=(10, 3), pady=7)
        self.images.grid(row=0, column=1, sticky=tk.W, padx=3, pady=7)
        self.videos.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)
        self.bored.grid(row=0, column=3, sticky=tk.W, padx=3, pady=7)

        # add search field, search button, and search results position
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))
        self.container.grid(row=2, column=0, columnspan=102, sticky=tk.W, padx=(10, 0), pady=7)

        self.news_results.grid(row=3, column=0)
        self.image_results.grid(row=3, column=0)

        # position of status bar
        self.status.grid(row=4, column=0, columnspan=102, sticky=tk.SW, padx=(10, 0), pady=(5, 5))


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

            # find images for the search
            self.image_api(keyword)
            self.news_api(keyword)

            self.search.delete(0, tk.END)
            self.search.insert(0, "Enter <keyword> to search...")
            root.focus()

    def news_api(self, keyword):
        key = 'dde38eb277ba442caaaa89a152952773'
        url = 'https://newsapi.org/v2/everything?q=' + 'bitcoin' + '&apiKey=' + 'dde38eb277ba442caaaa89a152952773'

        temp_news = []

        response = requests.get(url)
        results = response.json()

        for x in range(5):
            temp_news.append(results['articles'][x])

        print(results['articles'][0])
        self.news_results.set_news(temp_news)

    def image_api(self, keyword):
        temp_images = []

        PEXELS_API_KEY = '563492ad6f91700001000001ecab8f7b0b9f4371b013fa9bc225c984'
        api = API(PEXELS_API_KEY)
        api.search('kitten', page=1, results_per_page=6)
        images = api.get_entries()

        # for img in range(6):
        for img in images:
            # url_1 = "https://images.pexels.com/photos/416160/pexels-photo-416160.jpeg"
            # url_1 = "https://drive.google.com/uc?id=1FumEJWkRjQ6DA7UevruTgnuINlmKThmQ"
            response = requests.get(img.original)
            # response = requests.get(url_1)

            im1 = Image.open(BytesIO(response.content)).resize((600, 600))
            temp_images.append(im1)

        self.image_results.set_images(temp_images)

    def update_message(self, widget):
        self.messenger.set_current(widget)
        self.status_message = self.messenger.get_current()

        self.status.config(text=self.status_message)

    def switch_page(self, page):
        frame = self.frames[page]
        # print("switch to: ", page, "frame = ", frame)
        if page == 0:
            self.frames[1].grid_remove()
            self.frames[0].grid()
        else:
            self.frames[0].grid_remove()
            self.frames[1].grid()

        frame.tkraise()


class Results(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)

        # main canvas (red) that will hold all News search results (blue),
        self.redCanvas = tk.Canvas(self, width=640, height=500, bg="red")
        # self.redCanvas.config(highlightbackground="red")

        # create another canvas (blue) that'll hold search entries
        self.blueCanvas = tk.Canvas(self.redCanvas, width=640, height=450)
        self.redCanvas.create_window(0, 0, window=self.blueCanvas, anchor=tk.NW, width=640)

        # create scrollbar & assign it to 'red' canvas
        self.scrollbar = tk.Scrollbar(self, command=self.redCanvas.yview)
        self.redCanvas.config(yscrollcommand=self.scrollbar.set)

        # position the 'red' frame and the scrollbar
        self.redCanvas.grid(row=0, column=0, sticky=tk.NW)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # listen for events that would change the size or drag (i.e scroll) the 'blue' canvas
        self.redCanvas.bind("<Configure>", self.update_scrollbar)

    def update_scrollbar(self, event):
        self.redCanvas.configure(scrollregion=self.redCanvas.bbox("all"))


class NewsResults(Results):
    def __init__(self):
        Results.__init__(self)

        self.news_canvas = []

        # add search entries inside the 'blue' canvas
        for i in range(5):
            news = tk.Canvas(self.blueCanvas, height=200, width=480, bg="black")
            news.grid(row=i, column=0, sticky=tk.W, padx=(10, 15), pady=(10, 15))
            self.news_canvas.append(news)

    def set_news(self, news_list):
        for x in range(len(news_list)):
            print(news_list[x]['title'])

            self.news_canvas[x].create_text(5, 25, text=news_list[x]['description'], anchor='nw', width=420,
                                            fill="white")
            self.news_canvas[x].grid(row=x)


class ImageResults(Results):
    def __init__(self):
        Results.__init__(self)

        self.images = []
        self.images_canvas = []

        for x in range(5):
            for y in range(3):
                image = tk.Canvas(self.blueCanvas, height=180, width=180, bg="black")
                image.grid(row=x, column=y, sticky=tk.W, padx=(15, 15), pady=(15, 15))
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
            self.images_canvas[x].bind("<Enter>", lambda event, arg=self: self.mouse_in(event, arg))

    def enlarge_images(self, event, arg):
        image_window = tk.Toplevel(self)
        image_window.geometry("600x600")
        image_window.resizable(False, False)

        image_label = tk.Label(image_window, image=arg)
        image_label.grid(row=0, column=0)
        image_label.bind("<Button-1>", lambda event, arg=image_window: self.close_image(event, arg))
        # image_label.bind("<Enter>", self.mouse_in)
        image_label.bind("<Enter>", lambda event, arg=image_label: self.mouse_in(event, arg))

    def close_image(self, event, arg):
        arg.destroy()

    def mouse_in(self, event, widget):
        widget['cursor'] = "@icons8-hand-cursor-_2_.cur"


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


class Messages:
    def __init__(self):
        self.default = ""
        self.search_field = "This is the search field"

        self.current = self.default

    def get_current(self):
        return self.current

    def set_current(self, widget):
        self.current = widget


class ColorButtons(tk.Button):
    def __init__(self, event, message, status_bar, **kw):  # kw for all extra arguments
        tk.Button.__init__(self, event, **kw)
        self.status_bar = status_bar
        self.defaultBackground = self["background"]
        self.status_message = ""
        self.default = True

        self.bind("<Enter>", lambda event, arg=message: self.update_message(arg))
        self.bind("<Leave>", lambda event, arg=self.status_message: self.update_message(arg))

    def update_message(self, widget):
        self.status_message = widget
        self.status_bar.config(text=self.status_message)

        if self.default:
            self['background'] = '#E5F3FF'
            self.default = False
        else:
            self['background'] = self.defaultBackground
            self.default = True


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Scramble Engine")  # add title to the app
    root.resizable(False, False)  # don't allow resizing window
    root.geometry("680x620")
    app = Main(root)  # initiate the main interface
    root.mainloop()  # keep Tkinter running
