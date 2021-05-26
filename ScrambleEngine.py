import tkinter as tk
import requests  # handle HTTP requests
from PIL import ImageTk, Image  # for embedding images to Python/Tkinter
from io import BytesIO  # similar to previous
import random
import webbrowser
from dateutil import parser
import re


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()  # using Tkinter's grid system over pack
        self.language = "en"
        self.root = root

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
        self.home_btn = ColorButtons(self, text="Home", message="System: return to the Home page.",
                                 status_container=self.status_bar, status_msg=self.status)

        self.news = ColorButtons(self, text="News", message="System: search <keyword> for the latest news articles.",
                                 status_container=self.status_bar, status_msg=self.status)

        self.images = ColorButtons(self, text="Images", message="System: explore current images for <keyword>.",
                                   status_container=self.status_bar, status_msg=self.status)

        self.back = ColorButtons(self, text="Previous", message="System: navigate to the previous search page.",
                                 status_container=self.status_bar, status_msg=self.status)

        self.forward = ColorButtons(self, text="Next", message="System: navigate to the next search page.",
                                    status_container=self.status_bar, status_msg=self.status)

        self.home_btn.bind("<Button-1>", lambda arg=0: self.switch_page(2))
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
        self.home = Home(self)


        # add search field
        self.search = tk.Entry(self, width=100, fg="#606060")
        self.search.insert(0, "Enter <keyword> to search...")
        self.search.bind("<Button-1>", self.search_text)  # bind mouse click to search field's placeholder
        self.search_btn.bind("<Button-1>", self.click_search)

        self.search.bind("<Enter>", lambda event, arg=self.messenger.search_field: self.update_message(arg))
        self.search.bind("<Leave>", lambda event, arg=self.messenger.default: self.update_message(arg))

        # position of objects (buttons, search entry, labels)
        self.home_btn.grid(row=0, column=0, sticky=tk.W, padx=(10, 3), pady=7)
        self.news.grid(row=0, column=1, sticky=tk.W, padx=3, pady=7)
        self.images.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)
        self.bored.grid(row=0, column=3, sticky=tk.W, padx=3, pady=7)

        # add search field, search button, and search results position
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))

        # position of status bar
        self.status_container.grid(row=3, column=0, columnspan=102, sticky=tk.SW, padx=(10, 0), pady=(5, 5))
        self.status_bar.grid(row=0, column=0, columnspan=102, sticky=tk.SW, padx=(0, 0), pady=(0, 0))

        self.frames = [self.news_results, self.image_results, self.home]
        self.buttons = [self.home_btn, self.news, self.images, self.back, self.forward, self.search_btn, self.bored]


    def set_language(self, language):
        self.language = language

    def search_text(self, event):
        placeholder = self.search.get()

        if placeholder == "":
            root.focus()
            return

        elif placeholder == "Enter <keyword> to search...":
            self.search.delete(0, tk.END)
            root.focus()

        elif placeholder != "Enter <keyword> to search...":
            self.search.delete(0, tk.END)
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

        self.switch_page(0)

    def random_search(self, event):

        # before hooking up with a microservice as a source for keywords,
        # we'll just create our own sample for now...
        sample = ['Microsoft', 'Bitcoin', 'Amazon', 'YouTube',
                  'Apple', 'Ethereum', 'Nvidia', 'Pepsi']

        keywords = []

        response = requests.get("https://daniel-yu.herokuapp.com/get_random")

        divided = re.split(" | ,", response.json()['content'])


        num = random.randint(0, len(divided) - 1)

        # print("num = ", num)
        # keyword = sample[num]
        keyword = divided[num]
        backup = keyword

        # print("main keyword = ", keyword)
        alex_response = requests.get("http://text-to-words.herokuapp.com/get_words/" + keyword)

        alex_response = alex_response.json()["words"]
        for x in alex_response:
            word_list = alex_response[x]
            for y in word_list:
                keywords.append(y)

        if len(keywords) != 0:
            num = random.randint(0, len(keywords) - 1)
            keyword = keywords[num]
            # for word in keywords:
            #     print(word)

        self.image_api(keyword)
        self.news_api(keyword)

    def news_api(self, keyword):
        key = 'dde38eb277ba442caaaa89a152952773'


        country = self.toolbar.get_themes_var()

        # print(self.language)
        url = 'https://newsapi.org/v2/everything?q=' + keyword + '&apiKey=' + key + '&language=' + self.language

        if country != self.toolbar.get_countries()[0][0]:
            url = 'https://newsapi.org/v2/top-headlines?country=' + country + '&apiKey=' + key

        temp_news = []

        # print("@befeore sending GET request.")

        response = requests.get(url)
        results = response.json()

        # print("@news response: ", results)

        # print("@got news GET response back.")

        if results['totalResults'] != 0:
            for x in range(len(results['articles']) - 1):
                temp_news.append(results['articles'][x])
                # print(results['articles'][x])

            self.news_results.set_news(temp_news)
        else:
            print("@No news articles were found.")
            self.status_bar.itemconfig(self.status, text="Results found: 0")

    def image_api(self, keyword):

        temp_images = []
        images = []

        size = self.toolbar.get_image_var()

        key = '563492ad6f91700001000001ecab8f7b0b9f4371b013fa9bc225c984'
        url = "https://api.pexels.com/v1/search?query={}&per_page={}&page={}".format(keyword, 27, 1)

        response = requests.get(url, headers={'Authorization': key, 'X-Ratelimit-Remaining': 'X-Ratelimit-Remaining'})

        if response.json()['total_results'] != 0:

            for y in response.json()['photos']:
                images.append(y['src'])

            for x in images:
                response = requests.get(x[size])
                im1 = Image.open(BytesIO(response.content))
                im1.thumbnail((800, 800))
                temp_images.append(im1)

            self.image_results.set_images(temp_images)
        else:
            print("@No images were found.")
            self.status_bar.itemconfig(self.status, text="Results found: 0")

    def update_message(self, widget):
        self.messenger.set_current(widget)
        self.status_message = self.messenger.get_current()
        self.status_bar.itemconfig(self.status, text=self.status_message)

    def switch_page(self, page):

        frame = self.frames[page]
        if page == 0:
            # show News & hide Images
            # print("Display News")

            self.frames[0].redCanvas.grid()
            self.frames[0].scrollbar.grid()
            self.frames[1].redCanvas.grid_remove()
            self.frames[1].scrollbar.grid_remove()

            self.frames[2].redCanvas.grid_remove()

            self.forward.bind("<Button-1>", lambda root: self.news_results.increase_page(5, True))
            self.back.bind("<Button-1>", lambda root: self.news_results.increase_page(-5, False))
            self.frames[0].redCanvas.bind_all("<MouseWheel>", self.frames[0].scroll_canvas)

        elif page == 1:
            # show Images & hide News
            # print("Display Images")

            self.frames[1].redCanvas.grid()
            self.frames[1].scrollbar.grid()

            self.frames[0].redCanvas.grid_remove()
            self.frames[0].scrollbar.grid_remove()
            self.frames[2].redCanvas.grid_remove()

            self.forward.bind("<Button-1>", lambda root: self.image_results.increase_page(9, True))
            self.back.bind("<Button-1>", lambda root: self.image_results.increase_page(-9, False))
            self.frames[1].redCanvas.bind_all("<MouseWheel>", self.frames[1].scroll_canvas)

        elif page == 2:
            self.frames[2].redCanvas.grid()

            self.frames[0].redCanvas.grid_remove()
            self.frames[0].scrollbar.grid_remove()
            self.frames[1].redCanvas.grid_remove()
            self.frames[1].scrollbar.grid_remove()

        frame.tkraise()

    def open_link(self, event, arg):
        webbrowser.open_new(arg)


class Home(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self['borderwidth'] = 1
        self['relief'] = 'groove'


        self.redCanvas = tk.Canvas(root, width=650, height=500, bg="white", bd=1, highlightthickness=2, highlightbackground="green")

        # self.blueCanvas = tk.Canvas(self.redCanvas, width=660, height=500, bg="#202020", bd=0, highlightthickness=0)
        # self.redCanvas.create_window(0, 0, window=self.blueCanvas, anchor=tk.NW, width=660)

        self.bg = ImageTk.PhotoImage(Image.open("bg.png").resize((600, 88)))
        self.redCanvas.background = self.bg
        self.bg_image = self.redCanvas.create_image(660/2, 400/2, anchor=tk.CENTER, image=self.bg)

        self.redCanvas.grid(row=2, column=0, columnspan=102, sticky=tk.NW, padx=(10, 0), pady=7)


class Results(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self['borderwidth'] = 5
        self['relief'] = 'groove'

        # main canvas (red) that will hold all News search results (blue),
        self.redCanvas = tk.Canvas(root, width=640, height=500, bg="red", bd=0, highlightthickness=0)

        # create another canvas (blue) that'll hold search entries
        self.blueCanvas = tk.Canvas(self.redCanvas, width=640, height=450, bg="white", bd=0, highlightthickness=0)
        self.redCanvas.create_window(0, 0, window=self.blueCanvas, anchor=tk.NW, width=640)

        # create scrollbar & assign it to 'red' canvas
        self.scrollbar = tk.Scrollbar(root, command=self.redCanvas.yview, orient=tk.VERTICAL)
        self.redCanvas.config(yscrollcommand=self.scrollbar.set)

        # position the 'red' frame and the scrollbar
        self.redCanvas.grid(row=2, column=0, columnspan=102, sticky=tk.NW, padx=(10, 0), pady=7)
        self.scrollbar.grid(row=2, column=101, columnspan=102, sticky=tk.NS, padx=(10, 0), pady=7)

        # listen for events that would change the size or drag (i.e scroll) the 'blue' canvas
        self.redCanvas.bind("<Configure>", self.update_scrollbar)
        self.redCanvas.bind_all("<MouseWheel>", self.scroll_canvas)


    def scroll_canvas(self, event):
        # print("Scrolling canvas: ", self)
        increment = 0

        if event.delta == 120:
            # print('hi', event.delta)
            increment = -1
        elif event.delta == -120:
            # print('bye', event.delta)
            increment = 1

        self.redCanvas.yview_scroll(increment, "units")



    def update_scrollbar(self, event):
        # set scrolling region of the 'red' canvas
        self.redCanvas.configure(scrollregion=self.redCanvas.bbox("all"))


class NewsResults(Results):
    def __init__(self, root):
        Results.__init__(self, root)
        self.root = root

        self.news = []
        self.news_canvas = []
        self.canvas_objs = []
        self.start = 0
        self.end = 6

        # add search entries inside the 'blue' canvas
        for i in range(5):
            news = tk.Canvas(self.blueCanvas, height=200, width=615, bg="white", bd=1, highlightthickness=2, highlightbackground="green")
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

        if len(news_list) == 0:
            return None

        if len(self.canvas_objs) != 0:
            for canvas in self.news_canvas:
                for x in range(4):
                    canvas.delete(self.canvas_objs.pop(0))

        for x in range(5):
            content = []
            if (self.start + x) < len(news_list):
                for y in categories:
                    data = news_list[self.start + x][y]
                    if data is None:
                        data = 'N/A'
                    elif y == 'publishedAt':
                        data = parser.parse(data).date()
                    content.append(data)

                # add title
                title = self.news_canvas[x].create_text(5, 25, text=content[0], anchor='nw', width=600,
                                                        fill="white", font=("Arial", 10, "bold"))

                # date
                date = self.news_canvas[x].create_text(5, 60, text=content[1], anchor='nw', width=600,
                                                       fill="#99FF33", font=("Arial", 8, "normal"))

                # add source
                source = self.news_canvas[x].create_text(5, 75, text="Source: " + content[2], anchor='nw', width=600,
                                                         fill="#99FF33", font=("Arial", 8, "normal"))

                # add content
                content = self.news_canvas[x].create_text(5, 105, text=content[3], anchor='nw', width=600,
                                                          fill="white")

                items = [title, date, source, content]
                for y in items:
                    self.canvas_objs.append(y)

                self.news_canvas[x].grid(row=x)
                self.news_canvas[x].bind("<Button-1>", lambda event, arg=news_list[x]['url']: self.root.open_link(event, arg))
                self.news_canvas[x].bind("<Enter>", lambda event, arg=self.news_canvas[x]: self.mouse_in(event, arg))



    def close_image(self, event, arg):
        arg.destroy()

    def mouse_in(self, event, widget):
        widget['cursor'] = "@icons8-hand-cursor-_2_.cur"


class ImageResults(Results):
    def __init__(self, root):
        Results.__init__(self, root)
        self.root = root

        self.images = []
        self.images_canvas = []

        self.start = 0
        self.end = 9

        for x in range(3):
            for y in range(3):
                image = tk.Canvas(self.blueCanvas, height=180, width=180, bg="white", bd=1, highlightthickness=2, highlightbackground="green")
                image.grid(row=x, column=y, sticky=tk.W, padx=(15, 15), pady=(15, 15))
                self.images_canvas.append(image)

    def increase_page(self, num, increase):
        if len(self.images) == 0:
            return

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
            if (self.start + x) < len(img_set):
                img = ImageTk.PhotoImage(img_set[self.start + x])
                self.images_canvas[x].create_image(0, 0, image=img)
                self.images_canvas[x].bind("<Button-1>", lambda event, arg=img: self.enlarge_images(event, arg))
                self.images_canvas[x].bind("<Enter>", lambda event, arg=self.images_canvas[x]: self.mouse_in(event, arg))

    def enlarge_images(self, event, arg):
        image_window = tk.Toplevel(self)
        image_window.geometry(self.find_size())
        image_window.resizable(False, False)

        image_label = tk.Label(image_window, image=arg)
        image_label.grid(row=0, column=0)
        image_label.bind("<Button-1>", lambda event, arg=image_window: self.close_image(event, arg))
        image_label.bind("<Enter>", lambda event, arg=image_label: self.mouse_in(event, arg))

    def find_size(self):
        size = self.root.toolbar.get_image_var()

        dimensions = {"small": "400x200", "medium": "600x400", "large": "800x600"}

        print(dimensions[size])
        return dimensions[size]

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

        self.setting = tk.Menu(self.menu, tearoff=0)
        self.setting.add_command(label="Clear History", command=self.confirm, accelerator="Ctrl+Q")
        self.file.add_cascade(label="Settings", menu=self.setting)

        self.file.add_separator()
        self.file.add_command(label="Exit", command=self.exit)

        # view menu
        self.view = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="View", menu=self.view)

        self.searches = tk.Menu(self.view, tearoff=0)
        self.color_mode = tk.Menu(self.view, tearoff=0)
        self.view.add_cascade(label="Theme", menu=self.color_mode)
        self.view.add_separator()
        self.view.add_cascade(label="Search History", menu=self.searches)


        # advanced menu
        self.themes_var = tk.StringVar()
        self.languages = tk.StringVar()
        self.image_var = tk.StringVar()
        self.themes_var.set(self.countries[0][0])
        self.languages.set(1)
        self.image_var.set("medium")
        self.color = tk.StringVar()
        self.color.set(0)

        self.color_mode.add_radiobutton(label="Light", value=0, variable=self.color, command=lambda: self.change_theme(0))
        self.color_mode.add_radiobutton(label="Dark", value=1, variable=self.color, command=lambda: self.change_theme(1))

        self.advanced = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Advanced", menu=self.advanced)

        self.themes = tk.Menu(self.advanced, tearoff=0)

        self.advanced.add_cascade(label="Top News By Location", menu=self.themes)
        self.advanced.add_separator()


        for x in range(len(self.countries)):
            self.themes.add_radiobutton(label=self.countries[x][0], value=self.countries[x][1], variable=self.themes_var)


        self.image_sizes = tk.Menu(self.advanced, tearoff=0)
        self.image_sizes.add_radiobutton(label="Small", value="small", variable=self.image_var)
        self.image_sizes.add_radiobutton(label="Medium", value="medium", variable=self.image_var)
        self.image_sizes.add_radiobutton(label="Large", value="large", variable=self.image_var)
        self.advanced.add_cascade(label="Image Size", menu=self.image_sizes)


        self.advanced.add_separator()
        self.advanced.add_radiobutton(label="English", variable=self.languages, value=1,
                                      command=lambda: self.set_language("en"))
        self.advanced.add_radiobutton(label="Español", variable=self.languages, command=lambda: self.set_language("es"))
        self.advanced.add_radiobutton(label="中文", variable=self.languages, command=lambda: self.set_language("zh"))

        # help menu
        self.help = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Help", menu=self.help)
        self.help.add_command(label="Homepage", command=lambda: self.root.open_link(self.root, "https://github.com/yu-daniel/CS361"))
        self.help.add_command(label="Tutorial", command=self.show_tutorial)

        self.help.add_separator()
        self.help.add_command(label="About...", command=self.show_about)



    def show_tutorial(self):
        # add tutorial
        Tutorial(self.root)

    def get_countries(self):
        return self.countries

    def get_themes_var(self):
        return self.themes_var.get()

    def get_image_var(self):
        return self.image_var.get()

    def set_language(self, language):
        self.themes_var.set(self.countries[0][0])
        self.root.set_language(language)

    def add_search_history(self, keyword):
        self.search_history.append(keyword)

        self.searches.add_command(label=keyword, command=lambda: self.from_history(keyword))

    def from_history(self, keyword):
        self.root.image_api(keyword)
        self.root.news_api(keyword)

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

    def show_about(self):
        about = tk.Toplevel(self)

        x = root.winfo_x() + 150
        y = root.winfo_y() + 130

        about.geometry("320x130+{x}+{y}".format(x=x, y=y))
        about.title("About...")
        about.resizable(False, False)
        about.transient(self.root)
        about.focus()

        about_container = tk.Frame(about, width=320, height=130, bg="#202020", bd=0, highlightthickness=0)
        about_container.grid(row=0, column=0)

        logo = tk.Canvas(about_container, width=320, height=47, bg="green", bd=0, highlightthickness=0)
        logo.grid(row=0, column=0)

        logo_image = ImageTk.PhotoImage(Image.open("logo.png"))
        logo.background = logo_image
        logo.create_image(0, 0, ancho=tk.NW, image=logo_image)


        version = tk.Label(about_container, text="Version 1.1.1", fg="white", bg="#202020")
        version.grid(row=1, column=0)

        copyright = tk.Label(about_container, text="Copyright 2021 by Daniel Yu", fg="white", bg="#202020")
        copyright.grid(row=2, column=0)

        ok = ColorButtons(about_container, "Information regarding software version and creator.", self.root.status_bar,
                          self.root.status, text="Ok")

        ok.grid(row=3, column=0, sticky=tk.SE, padx=(0, 10), pady=(10, 10))
        ok.bind("<Button-1>", lambda event, screen=about: self.cancel(screen))

    def cancel(self, screen):
        screen.destroy()

    def exit(self):
        self.root.quit()

    def change_theme(self, theme):
        if theme == 0:
            self.root['bg'] = "#F0F0F0"
            self.root.root['bg'] = "#F0F0F0"

            self.root.status_bar.itemconfig(self.root.status, fill="#606060")

            self.root.status_container['bg'] = "#F0F0F0"
            self.root.status_container['bd'] = 1
            self.root.status_container['highlightthickness'] = 0
            self.root.status_container['highlightbackground'] = "#F0F0F0"

            self.root.status_bar['bg'] = "#F0F0F0"
            self.root.status_bar['bd'] = 1
            self.root.status_bar['highlightthickness'] = 1

            self.root.search['fg'] = "#606060"
            self.root.search['background'] = "#F0F0F0"

            self.root.home.redCanvas['background'] = "white"
            self.root.news_results.blueCanvas['background'] = "white"
            self.root.image_results.blueCanvas['background'] = "white"

            for canvas in self.root.news_results.news_canvas:
                canvas['background'] = "white"

            for canvas in self.root.image_results.images_canvas:
                canvas['background'] = "white"

            for button in self.root.buttons:
                button['background'] = "#F6FFEE"
                button.set_color("black", "#F6FFEE", "#CCFFCC")

        else:
            self.root['bg'] = "#202020"
            self.root.root['bg'] = "#202020"

            self.root.status_bar.itemconfig(self.root.status, fill="#29CB66")

            self.root.status_container['bg'] = "#202020"
            self.root.status_container['bd'] = 1
            self.root.status_container['highlightthickness'] = 1
            self.root.status_container['highlightbackground'] = "#22A753"

            self.root.status_bar['bg'] = "#202020"
            self.root.status_bar['bd'] = 0
            self.root.status_bar['highlightthickness'] = 0

            self.root.search['fg'] = "#99FF99"
            self.root.search['background'] = "#202020"

            self.root.home.redCanvas['background'] = "#202020"
            self.root.news_results.blueCanvas['background'] = "#202020"
            self.root.image_results.blueCanvas['background'] = "#202020"

            for canvas in self.root.news_results.news_canvas:
                canvas['background'] = "black"

            for canvas in self.root.image_results.images_canvas:
                canvas['background'] = "black"

            for button in self.root.buttons:
                button['background'] = "#29CB66"
                button.set_color("black", "#29CB66", "#FFFF99")



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
        self.status_message = "Status: "
        self.default = True

        self.fg = None
        self.bg_default = '#F6FFEE'
        self.bg_hover = '#CCFFCC'

        self['background'] = self.bg_default

        self.bind("<Enter>", lambda event, arg=message: self.update_message(arg))
        self.bind("<Leave>", lambda event, arg=self.status_message: self.update_message(arg))

    def update_message(self, widget):
        self.status_message = widget
        self.status_container.itemconfig(self.status, text=self.status_message)

        if self.default:
            self['background'] = self.bg_hover
            self.default = False
        else:
            self['background'] = self.bg_default
            self.default = True

    def set_color(self, fg, bg_default, bg_new):
        self.fg = fg
        self.bg_default = bg_default
        self.bg_hover = bg_new



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
    root.iconbitmap("logo64.ico")
    root.resizable(False, False)    # don't allow resizing window
    root.geometry("680x650")
    app = Main(root)                # initiate the main interface
    root.mainloop()                 # keep Tkinter running