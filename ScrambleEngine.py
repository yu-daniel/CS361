import tkinter as tk
import requests  # handle HTTP requests
from PIL import ImageTk, Image  # for embedding images to Python/Tkinter
from io import BytesIO  # similar to previous
import random
import webbrowser
from dateutil import parser


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()  # using Tkinter's grid system over pack
        self.language = "en"

        # add access to status messages
        self.messenger = Messages()
        self.status_message = self.messenger.default



        # add status bar
        self.status_container = tk.Frame(relief="groove", borderwidth="2")
        self.status_bar = tk.Canvas(master=self.status_container, width=652, height=15)
        # self.status = tk.Label(self.status_container2, text=self.status_message, fg="#606060")
        self.status = self.status_bar.create_text(10, 0, anchor="nw", text=self.status_message, fill="#606060")

        # initiate the main toolbar

        self.toolbar = Toolbar(self)
        root.config(menu=self.toolbar)

        # add buttons to the UI
        self.news = ColorButtons(self, text="News", message="System: search <keyword> for the latest news articles.",
                                 status_container=self.status_bar, status_msg=self.status)
        self.images = ColorButtons(self, text="Images", message="System: explore current images for <keyword>.",
                                   status_container=self.status_bar, status_msg=self.status)

        self.back = ColorButtons(self, text="Previous", message="System: navigate to the previous search page.",
                                 status_container=self.status_bar, status_msg=self.status)

        self.forward = ColorButtons(self, text="Next", message="System: navigate to the next search page.",
                                    status_container=self.status_bar, status_msg=self.status)

        self.news.bind("<Button-1>", lambda arg=0: self.switch_page(0))
        self.images.bind("<Button-1>", lambda arg=1: self.switch_page(1))


        self.search_btn = ColorButtons(self, text="Search", message="Initiate a search query for <keyword>.",
                                       status_container=self.status_bar,
                                       status_msg=self.status)
        self.bored = ColorButtons(self, text="I'm Feeling Bored", message="No idea what to search for? Let me help!",
                                  status_container=self.status_bar,
                                  status_msg=self.status)

        self.bored.bind("<Button-1>", self.random_search)

        # RESULTS AREA
        self.container = tk.Frame(self, bg="black")

        self.back.grid(row=0, column=4, sticky=tk.W, padx=3, pady=7)
        self.forward.grid(row=0, column=5, sticky=tk.W, padx=3, pady=7)

        self.image_results = ImageResults(self)
        self.news_results = NewsResults(self)

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
        self.bored.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)

        # add search field, search button, and search results position
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))

        # position of status bar
        self.status_container.grid(row=3, column=0, columnspan=102, sticky=tk.SW, padx=(10, 0), pady=(5, 5))
        self.status_bar.grid(row=0, column=0, columnspan=102, sticky=tk.SW, padx=(0, 0), pady=(0, 0))

        self.frames = [self.news_results, self.image_results]


    def set_language(self, language):
        self.language = language

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
        placeholder = self.search.get()

        if placeholder == "Enter <keyword> to search...":
            return
        else:
            keyword = self.search.get()

            self.toolbar.add_search_history(keyword)

            # find images for the search
            self.news_api(keyword)
            self.image_api(keyword)

            self.search.delete(0, tk.END)
            self.search.insert(0, "Enter <keyword> to search...")
            root.focus()

    def random_search(self, event):
        # before hooking up with a microservice as a source for keywords,
        # we'll just create our own sample for now...
        sample = ['Microsoft', 'Bitcoin', 'Amazon', 'YouTube',
                  'Apple', 'Ethereum', 'Nvidia', 'Pepsi']

        num = random.randint(0, len(sample) - 1)

        keyword = sample[num]
        print("keyword = ", keyword)

        self.image_api(keyword)
        self.news_api(keyword)

    def news_api(self, keyword):
        key = 'dde38eb277ba442caaaa89a152952773'

        country = self.toolbar.get_themes_var()


        url = 'https://newsapi.org/v2/everything?q=' + keyword + '&apiKey=' + key + '&language=' + self.language

        if country != self.toolbar.get_countries()[0][0]:
            url = 'https://newsapi.org/v2/top-headlines?country=' + country + '&apiKey=' + key

        temp_news = []

        response = requests.get(url)
        results = response.json()

        for x in range(len(results['articles']) - 1):
            temp_news.append(results['articles'][x])

        self.news_results.set_news(temp_news)

    def image_api(self, keyword):
        temp_images = []
        images = []

        key = '563492ad6f91700001000001ecab8f7b0b9f4371b013fa9bc225c984'
        url = "https://api.pexels.com/v1/search?query={}&per_page={}&page={}".format(keyword, 27, 1)

        response = requests.get(url, headers={'Authorization': key, 'X-Ratelimit-Remaining': 'X-Ratelimit-Remaining'})
        for y in response.json()['photos']:
            images.append(y['src'])

        for x in images:
            response = requests.get(x['large'])
            im1 = Image.open(BytesIO(response.content))
            im1.thumbnail((800, 800))
            temp_images.append(im1)

        self.image_results.set_images(temp_images)

    def update_message(self, widget):
        self.messenger.set_current(widget)
        self.status_message = self.messenger.get_current()
        self.status_bar.itemconfig(self.status, text=self.status_message)

    def switch_page(self, page):

        frame = self.frames[page]
        if page == 0:
            # show News & hide Images
            self.frames[1].redCanvas.grid_remove()
            self.frames[1].scrollbar.grid_remove()
            self.frames[0].redCanvas.grid()
            self.frames[0].scrollbar.grid()
            self.forward.bind("<Button-1>", lambda root: self.news_results.increase_page(5, True))
            self.back.bind("<Button-1>", lambda root: self.news_results.increase_page(-5, False))
        else:
            # show Images & hide News
            self.frames[0].redCanvas.grid_remove()
            self.frames[0].scrollbar.grid_remove()
            self.frames[1].redCanvas.grid()
            self.frames[1].scrollbar.grid()
            self.forward.bind("<Button-1>", lambda root: self.image_results.increase_page(9, True))
            self.back.bind("<Button-1>", lambda root: self.image_results.increase_page(-9, False))

        frame.tkraise()


class Results(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self['borderwidth'] = 1
        self['relief'] = 'groove'

        # main canvas (red) that will hold all News search results (blue),
        self.redCanvas = tk.Canvas(root, width=640, height=500, bg="red", bd=0, highlightthickness=0)

        # create another canvas (blue) that'll hold search entries
        self.blueCanvas = tk.Canvas(self.redCanvas, width=640, height=450, bg="#202020", bd=0, highlightthickness=0)
        self.redCanvas.create_window(0, 0, window=self.blueCanvas, anchor=tk.NW, width=640)

        # create scrollbar & assign it to 'red' canvas
        self.scrollbar = tk.Scrollbar(root, command=self.redCanvas.yview, orient=tk.VERTICAL)
        self.redCanvas.config(yscrollcommand=self.scrollbar.set)

        # position the 'red' frame and the scrollbar
        self.redCanvas.grid(row=2, column=0, columnspan=102, sticky=tk.NW, padx=(10, 0), pady=7)
        self.scrollbar.grid(row=2, column=101, columnspan=102, sticky=tk.NS, padx=(10, 0), pady=7)

        # listen for events that would change the size or drag (i.e scroll) the 'blue' canvas
        self.redCanvas.bind("<Configure>", self.update_scrollbar)

    def update_scrollbar(self, event):
        # set scrolling region of the 'red' canvas
        self.redCanvas.configure(scrollregion=self.redCanvas.bbox("all"))


class NewsResults(Results):
    def __init__(self, root):
        Results.__init__(self, root)

        self.news = []
        self.news_canvas = []
        self.canvas_objs = []
        self.start = 0
        self.end = 6

        # add search entries inside the 'blue' canvas
        for i in range(5):
            news = tk.Canvas(self.blueCanvas, height=200, width=615, bg="black")
            news.grid(row=i, column=0, sticky=tk.W, padx=(10, 15), pady=(10, 15))
            self.news_canvas.append(news)

        root.forward.bind("<Button-1>", lambda root: self.increase_page(5, True))
        root.back.bind("<Button-1>", lambda root: self.increase_page(-5, False))

    def increase_page(self, num, increase):
        if self.end <= 15 and increase is True:
            self.start += num
            self.end += num
            self.set_news(self.news)

        elif self.start > 0 and increase is False:
            self.start += num
            self.end += num
            self.set_news(self.news)


    def set_news(self, news_list):
        self.news = news_list
        categories = ['title', 'publishedAt', 'author', 'description']

        if len(self.canvas_objs) != 0:
            for canvas in self.news_canvas:
                for x in range(4):
                    canvas.delete(self.canvas_objs.pop(0))

        for x in range(5):
            content = []

            for y in categories:
                data = news_list[self.start + x][y]
                if data is None:
                    data = 'N/A'
                elif y == 'publishedAt':
                    data = parser.parse(data).date()
                content.append(data)

            # add title
            title = self.news_canvas[x].create_text(5, 25, text=content[0], anchor='nw', width=600,
                                                    fill="white", font=("Candara", 12, "bold"))

            # date
            date = self.news_canvas[x].create_text(5, 50, text=content[1], anchor='nw', width=600,
                                                   fill="#99FF33", font=("Candara", 12, "normal"))

            # add source
            source = self.news_canvas[x].create_text(5, 75, text="Source: " + content[2], anchor='nw', width=600,
                                                     fill="#99FF33", font=("Candara", 12, "normal"))

            # add content
            content = self.news_canvas[x].create_text(5, 125, text=content[3], anchor='nw', width=600,
                                                      fill="white")

            items = [title, date, source, content]
            for y in items:
                self.canvas_objs.append(y)

            self.news_canvas[x].grid(row=x)
            self.news_canvas[x].bind("<Button-1>", lambda event, arg=news_list[x]['url']: self.open_article(event, arg))
            self.news_canvas[x].bind("<Enter>", lambda event, arg=self.news_canvas[x]: self.mouse_in(event, arg))

    def open_article(self, event, arg):
        webbrowser.open_new(arg)

    def close_image(self, event, arg):
        arg.destroy()

    def mouse_in(self, event, widget):
        widget['cursor'] = "@icons8-hand-cursor-_2_.cur"


class ImageResults(Results):
    def __init__(self, root):
        Results.__init__(self, root)

        self.images = []
        self.images_canvas = []

        self.start = 0
        self.end = 9

        for x in range(3):
            for y in range(3):
                image = tk.Canvas(self.blueCanvas, height=180, width=180, bg="black")
                image.grid(row=x, column=y, sticky=tk.W, padx=(15, 15), pady=(15, 15))
                self.images_canvas.append(image)

    def increase_page(self, num, increase):
        if self.end < 27 and increase is True:
            self.start += num
            self.end += num
            self.set_images(self.images)

        elif self.start > 0 and increase is False:
            self.start += num
            self.end += num
            self.set_images(self.images)

    def set_images(self, img_set):
        self.images = img_set

        # clear any existing image and add new image to canvas
        for x in range(9):
            self.images_canvas[x].delete("all")

            img = ImageTk.PhotoImage(img_set[self.start + x])
            self.images_canvas[x].create_image(0, 0, image=img)
            self.images_canvas[x].bind("<Button-1>", lambda event, arg=img: self.enlarge_images(event, arg))
            self.images_canvas[x].bind("<Enter>", lambda event, arg=self.images_canvas[x]: self.mouse_in(event, arg))

    def enlarge_images(self, event, arg):
        image_window = tk.Toplevel(self)
        image_window.geometry("800x600")
        image_window.resizable(False, False)

        image_label = tk.Label(image_window, image=arg)
        image_label.grid(row=0, column=0)
        image_label.bind("<Button-1>", lambda event, arg=image_window: self.close_image(event, arg))
        image_label.bind("<Enter>", lambda event, arg=image_label: self.mouse_in(event, arg))

    def close_image(self, event, arg):
        arg.destroy()

    def mouse_in(self, event, widget):
        widget['cursor'] = "@icons8-hand-cursor-_2_.cur"


class Toolbar(tk.Menu):
    def __init__(self, root):
        super().__init__(root)
        self.menu = tk.Menu(self)
        self.root = root

        self.search_history = []
        self.countries = [("All", "All"),
                          ("Australia", "au"),
                          ("Brazil", "br"),
                          ("Canada", "ca"),
                          ("China", "zh"),
                          ("Germany", "de"),
                          ("United Kingdom", "gb"),
                          ("Hong Kong", "hk"),
                          ("Israel", "il"),
                          ("India", "in"),
                          ("Italy", "it"),
                          ("Japan", "jp"),
                          ("South Korea", "kr"),
                          ("Mexico", "mx"),
                          ("Malaysia", "ma"),
                          ("Russia", "ru"),
                          ("Saudi Arabia", "sa"),
                          ("Singapore", "sg"),
                          ("Thailand", "th"),
                          ("Taiwan", "tw"),
                          ("United States", "us")
                          ]

        # file menu
        self.file = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="File", menu=self.file)
        self.file.add_command(label="Export", command=None)
        # self.file.add_command(label="Settings", command=None)
        self.setting = tk.Menu(self.menu, tearoff=0)
        self.setting.add_separator()
        self.setting.add_command(label="Clear History", command=self.confirm)
        self.file.add_cascade(label="Settings", menu=self.setting)

        self.file.add_separator()
        self.file.add_command(label="Exit", command=self.exit)

        self.edit = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Edit", menu=self.edit)
        self.edit.add_command(label="Copy", command=None)
        self.edit.add_command(label="Paste", command=None)
        self.edit.add_separator()
        self.edit.add_command(label="Select All", command=None)

        # view menu
        self.view = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="View", menu=self.view)

        self.searches = tk.Menu(self.view, tearoff=0)

        self.view.add_cascade(label="Search History", menu=self.searches)
        self.view.add_separator()
        self.view.add_command(label="Tutorial", command=self.show_tutorial)

        # advanced menu
        self.themes_var = tk.StringVar()
        self.languages = tk.StringVar()
        self.themes_var.set(self.countries[0][0])
        self.languages.set(1)

        self.advanced = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Advanced", menu=self.advanced)

        self.themes = tk.Menu(self.advanced, tearoff=0)

        self.advanced.add_cascade(label="Top News By Location", menu=self.themes)


        for x in range(len(self.countries)):
            self.themes.add_radiobutton(label=self.countries[x][0], value=self.countries[x][1], variable=self.themes_var)

        self.advanced.add_separator()
        self.advanced.add_radiobutton(label="English", variable=self.languages, value=1,
                                      command=lambda: self.set_language("en"))
        self.advanced.add_radiobutton(label="Español", variable=self.languages, command=lambda: self.set_language("es"))
        self.advanced.add_radiobutton(label="中文", variable=self.languages, command=lambda: self.set_language("zh"))

        # help menu
        self.help = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Help", menu=self.help)
        self.help.add_command(label="Homepage", command=None)
        self.help.add_separator()
        self.help.add_command(label="About...", command=None)

    def show_tutorial(self):
        # add tutorial
        Tutorial(self.root)

    def get_countries(self):
        return self.countries

    def get_themes_var(self):
        return self.themes_var.get()

    def set_language(self, language):
        self.root.set_language(language)

    def add_search_history(self, keyword):
        self.search_history.append(keyword)

        self.searches.add_command(label=keyword, command=None)

    def confirm(self):
        confirm_screen = tk.Toplevel(self)
        x = self.root.winfo_x() + 250
        y = self.root.winfo_y() + 330

        confirm_screen.geometry("175x50+{x}+{y}".format(x=x, y=y))
        confirm_screen.resizable(False, False)
        confirm_screen.transient(self.root)

        frame = tk.Frame(confirm_screen)
        frame.grid(row=0, column=0)

        label = tk.Label(frame, text="Ready to clear all search history?")
        label.grid(row=0, column=0, columnspan=2)

        cancel = ColorButtons(frame, "Cancel operation.", self.root.status_bar, self.root.status, text="Cancel")
        cancel.bind("<Button-1>", lambda event, screen=confirm_screen: self.cancel(screen))
        cancel.grid(row=1, column=0, sticky=tk.SW, padx=(10, 0), pady=0)

        ok = ColorButtons(frame, "Confirm operation.", self.root.status_bar, self.root.status, text="Confirm")
        ok.grid(row=1, column=1, sticky=tk.SE, padx=(0, 10), pady=0)
        ok.bind("<Button-1>", lambda event, screen=confirm_screen: self.ok(screen))

    def ok(self, screen):
        history_total = self.searches.index("end")

        if history_total is not None:
            for num in range(history_total + 1):
                self.searches.delete(0)

        screen.destroy()

    def cancel(self, screen):
        screen.destroy()

    def exit(self):
        self.root.quit()


class Messages:
    def __init__(self):
        self.default = "Status: "
        self.search_field = "System: enter a <keyword> to begin the search."
        self.current = self.default

    def get_current(self):
        return self.current

    def set_current(self, widget):
        self.current = widget


class ColorButtons(tk.Button):
    def __init__(self, event, message, status_container, status_msg, **kw):  # kw for all extra arguments
        tk.Button.__init__(self, event, **kw)
        self.status_container = status_container
        self.status = status_msg
        self.defaultBackground = self["background"]
        self.status_message = "Status: "
        self.default = True

        self.bind("<Enter>", lambda event, arg=message: self.update_message(arg))
        self.bind("<Leave>", lambda event, arg=self.status_message: self.update_message(arg))

    def update_message(self, widget):
        self.status_message = widget
        self.status_container.itemconfig(self.status, text=self.status_message)

        if self.default:
            self['background'] = '#E5F3FF'
            self.default = False
        else:
            self['background'] = self.defaultBackground
            self.default = True


class Tutorial(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)

        # find parent window's position
        x = root.winfo_x() + 250
        y = root.winfo_y() + 230

        # (width)x(height)+(x-position)+(y-position)
        self.geometry("500x350+{x}+{y}".format(x=x, y=y))

        self.resizable(False, False)
        self.transient(root)

        self.main = tk.Frame(self, bg="#202020")
        self.main.grid(row=0, column=0)

        self.bg = tk.Canvas(self.main, width=500, height=350, bg="green", bd=0, highlightthickness=0)
        self.bg.grid(row=0, column=0, columnspan=3)

        self.cancel = ColorButtons(self.main, "Exit tutorial.", root.status_bar, root.status, text="Ok")
        self.cancel.grid(row=0, column=2, sticky=tk.S)

        self.next = ColorButtons(self.main, "Next tip.", root.status_bar, root.status, text="Next")
        self.next.grid(row=0, column=1, sticky=tk.S)

        self.previous = ColorButtons(self.main, "Previous tip.", root.status_bar, root.status, text="Previous")
        self.previous.grid(row=0, column=0, sticky=tk.S)

        self.count = 1
        front_img = 'test1.jpg'

        self.img = ImageTk.PhotoImage(Image.open(front_img).resize((500, 350)))
        self.bg.background = self.img
        self.bg_image = self.bg.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.cancel.bind("<Button-1>", lambda event, root=self: self.close(root))
        self.next.bind("<Button-1>", lambda event, root=self, increase=True: self.change_tip(root, increase))
        self.previous.bind("<Button-1>", lambda event, root=self, increase=False: self.change_tip(root, increase))


    def close(self, root):
        root.destroy()

    def change_tip(self, root, increase):
        if self.count < 6 and increase is True:
            self.count += 1
        elif self.count > 1 and increase is False:
            self.count -= 1

        img2 = 'test{num}.jpg'.format(num=self.count)
        self.img = ImageTk.PhotoImage(Image.open(img2).resize((500, 350)))
        self.bg.itemconfig(self.bg_image, image=self.img)



if __name__ == '__main__':
    root = tk.Tk()
    root.title("Scramble Engine")   # add title to the app
    root.resizable(False, False)    # don't allow resizing window
    root.geometry("680x620")
    app = Main(root)                # initiate the main interface
    root.mainloop()                 # keep Tkinter running
