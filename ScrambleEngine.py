import tkinter as tk
import requests  # GET requests from APIs & microservice(s)
from PIL import ImageTk, Image  # image handling
from io import BytesIO
import random
import webbrowser
from dateutil import parser
import re  # split strings
import time


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()
        self.language = "en"  # current language the News API will use; default is English
        self.root = root

        # initiate an instance for each area of the UI
        self.messenger = Messages(self)
        self.toolbar = Toolbar(self)
        self.status_container = StatusField(self)
        self.search_set = SearchField(self)
        self.image_results = ImageResults(self)
        self.news_results = NewsResults(self)
        self.home = Home(self)

        # allow switching different pages in the search results field
        self.frames = [self.news_results, self.image_results, self.home]

        self.root.config(menu=self.toolbar)

    def set_language(self, language):
        self.language = language

    def search_text(self, event):
        """
        Deletes any user input and replaces the search field's placeholder with the default text.
        """

        keyword = self.search_set.search.get()

        if keyword == "":
            root.focus()
            return

        self.search_set.search.delete(0, tk.END)

        # enter the default text if it is currently not
        if keyword != self.search_set.get_tooltip():
            self.search_set.search.insert(0, "Enter <keyword> to search...")

        root.focus()

    def click_search(self, event):
        """
        Callback function that listens for Button-1 clicks, which is bound to the Search button.
        Captures the user's <keyword> in the search field and passes it to the news & image APIs.
        """
        keyword = self.search_set.search.get()

        if keyword == self.search_set.get_tooltip():
            return
        else:
            # add the user's keyword to the Search History
            self.toolbar.add_search_history(keyword)

            self.news_api(keyword)
            self.image_api(keyword)

            self.search_set.search.delete(0, tk.END)
            self.search_set.search.insert(0, "Enter <keyword> to search...")
            root.focus()

        self.switch_page(0)

    def random_search(self, event):
        """
        Performs a "random" search for news & images, using a random <keyword>
        from a third party microservice (by Alex Shin).
        """

        # get a random <keyword> from a Wikipedia article
        keywords = []
        response = requests.get("https://daniel-yu.herokuapp.com/get_random")
        divided = re.split(" | ,", response.json()["content"])
        num = random.randint(0, len(divided) - 1)

        # use the above result as a keyword for the microservice - which we use to generate a second keyword
        keyword = divided[num]
        alex_response = requests.get("http://text-to-words.herokuapp.com/get_words/{k}".format(k=keyword))
        alex_response = alex_response.json()["words"]

        for x in alex_response:
            word_list = alex_response[x]
            for y in word_list:
                keywords.append(y)

        if len(keywords) != 0:
            num = random.randint(0, len(keywords) - 1)
            keyword = keywords[num]

        # the second keyword (if successfully returned), will be used for the news and images API
        self.image_api(keyword)
        self.news_api(keyword)

    def news_api(self, keyword):
        """
        Uses News API to search for <keyword> based articles or by location/country's top headlines
        """

        key = "dde38eb277ba442caaaa89a152952773"
        country = self.toolbar.get_themes_var()  # get current location/country that's selected

        # get news content from the API using the input <keyword>
        url = "https://newsapi.org/v2/everything?q=" \
              "{k}&apiKey={key}&language={l}".format(k=keyword, key=key, l=self.language)

        # use endpoint by top-headlines if any country is selected
        if country != self.toolbar.get_countries()[0][0]:
            url = "https://newsapi.org/v2/top-headlines?country={c}&apiKey={k}".format(c=country, k=key)
            self.toolbar.set_en()

        temp_news = []

        response = requests.get(url)
        results = response.json()

        if results["totalResults"] != 0:
            for x in range(len(results["articles"]) - 1):
                temp_news.append(results["articles"][x])
            self.news_results.set_news(temp_news)
        # when the API find no relevant articles, display a message to the user
        else:
            self.status_container.status_bar.itemconfig(self.status_container.status, text="Results found: 0")

    def image_api(self, keyword):
        """
        Use Pexel API to search images based on the keyword. Per page limit set to 27, and only use the
        first page to following hourly/monthly request limits (i.e. free tier).
        """

        temp_images, images = [], []

        size = self.toolbar.get_image_var()

        key = "563492ad6f91700001000001ecab8f7b0b9f4371b013fa9bc225c984"
        url = "https://api.pexels.com/v1/search?query=" \
              "{k}&per_page={total}&page={pg_num}".format(k=keyword, total=27, pg_num=1)

        response = requests.get(url, headers={"Authorization": key,
                                              "X-Ratelimit-Remaining": "X-Ratelimit-Remaining"})

        # when there is at least one "hit", extract and save the image from the JSON response
        if response.json()["total_results"] != 0:
            for y in response.json()["photos"]:
                images.append(y["src"])
            for x in images:
                response = requests.get(x[size])
                im1 = Image.open(BytesIO(response.content))
                im1.thumbnail((800, 800))
                temp_images.append(im1)
            self.image_results.set_images(temp_images)
        # inform the user if no results are found
        else:
            self.status_container.status_bar.itemconfig(self.status_container.status, text="Results found: 0")

    def update_message(self, widget):
        """
        Callback function that detects mouse hovering over the Search button.
        Updates the status bar's "tips" that corresponds to the search field.
        """
        self.messenger.set_current(widget)
        status_message = self.messenger.get_current()

        # update status bar's text to match the search field's
        self.status_container.status_bar.itemconfig(self.status_container.status, text=status_message)

    def switch_page(self, page):
        """
        Displays different type of contents in the search results area by allowing the user to
        use the Home, News, and Images button for toggling.
        """

        frame = self.frames[page]  # get the current page that the user selects
        num_entries = 0

        if page == 0:
            num_entries += 5
        else:
            num_entries += 9

        for x in range(3):
            # for News and Images page, show the scrollbar and bind the mousewheel for scrolling
            # each page of the search results.
            # bind the Previous and Next buttons for the user to navigate between different pages of search results.
            if page == 0 or page == 1:
                self.frames[x].scrollbar.grid()
                self.frames[page].redCanvas.bind_all("<MouseWheel>", self.frames[page].scroll_canvas)
                self.search_set.forward.bind("<Button-1>",
                                             lambda event: self.frames[page].increase_page(num_entries, True))
                self.search_set.back.bind("<Button-1>",
                                          lambda event: self.frames[page].increase_page(num_entries * -1, False))
            # show the frame for the current page
            if page == x:
                self.frames[x].redCanvas.grid()
            # hide all other frames besides the current one
            else:
                self.frames[x].redCanvas.grid_remove()
                self.frames[x].scrollbar.grid_remove()
        frame.tkraise()

    def open_link(self, link):
        """
        Opens the web browser that links to the argument link
        """
        webbrowser.open_new(link)

    def update_btns(self, buttons, data):
        """
        Add a label and "tip" for each button in the "buttons" list using the input dictionary data
        """
        for num in range(len(buttons)):
            text = data.get(num)[0]  # the button's label
            message = data.get(num)[1]  # the button's "tip"

            buttons[num].config(text=text)
            buttons[num].set_message(message)
            buttons[num].set_status(self.status_container.status_bar, self.status_container.status)


class StatusField(tk.Frame):
    """
    The status bar that is located at the button of the UI, which display "tips" to the user,
    whenever his/her mouse pointer hovers over a widget, such as a button or the search field.
    The status bar is a frame that contains a canvas with text (i.e. the tips).
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self["relief"], self["borderwidth"] = "groove", "2"
        self.status_message = self.root.messenger.get_current()

        # initiate the canvas which will hold the text/"tip"
        self.status_bar = tk.Canvas(self, width=655, height=15)
        self.status_bar.grid(row=0, column=0, columnspan=102, sticky=tk.SW, padx=(0, 0), pady=(0, 0))
        self.status = self.status_bar.create_text(10, 0, anchor="nw", text=self.status_message, fill="#606060")

        self.grid(row=3, column=0, columnspan=102, sticky=tk.SW, padx=(10, 0), pady=(5, 5))


class SearchField(tk.Frame):
    """
    Area of the UI that contains that hold all the buttons (i.e. Home, News, Images, etc) and the search field.
    Essentially it's a frame with buttons and an entry.
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        # initiate each of the buttons
        self.home_btn = ColorButtons(self)
        self.news = ColorButtons(self)
        self.images = ColorButtons(self)
        self.back = ColorButtons(self)
        self.forward = ColorButtons(self)
        self.search_btn = ColorButtons(self)
        self.bored = ColorButtons(self)

        # initiate the search field
        self.search = tk.Entry(self, width=100, fg="#606060")

        # set the position of the frame and all the buttons (& entry) that it holds
        self.grid(row=0, column=0, columnspan=102, sticky=tk.W)

        # set the position of buttons (and entry) within this frame
        self.home_btn.grid(row=0, column=0, sticky=tk.W, padx=(10, 3), pady=7)
        self.news.grid(row=0, column=1, sticky=tk.W, padx=3, pady=7)
        self.images.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)
        self.bored.grid(row=0, column=3, sticky=tk.W, padx=3, pady=7)
        self.back.grid(row=0, column=4, sticky=tk.W, padx=3, pady=7)
        self.forward.grid(row=0, column=5, sticky=tk.W, padx=3, pady=7)
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))

        # add a placeholder for the search field
        self.tooltip = "Enter <keyword> to search..."
        self.search.insert(0, self.tooltip)

        # add clicking interaction for the search field and for each button
        self.search.bind("<Button-1>", self.root.search_text)  # bind mouse click to search field's placeholder
        self.search_btn.bind("<Button-1>", self.root.click_search)

        self.search.bind("<Enter>", lambda event, arg=self.root.messenger.search_field: self.root.update_message(arg))
        self.search.bind("<Leave>", lambda event, arg=self.root.messenger.default: self.root.update_message(arg))

        self.home_btn.bind("<Button-1>", lambda event: self.root.switch_page(2))
        self.news.bind("<Button-1>", lambda event: self.root.switch_page(0))
        self.images.bind("<Button-1>", lambda event: self.root.switch_page(1))
        self.bored.bind("<Button-1>", self.root.random_search)

        # set of button names and description of their use
        context = {0: ("Home", "System: return to the Home page."),
                   1: ("News", "System: search <keyword> for the latest news articles."),
                   2: ("Images", "System: explore current images for <keyword>."),
                   3: ("Previous", "System: navigate to the previous search page."),
                   4: ("Next", "System: navigate to the next search page."),
                   5: ("Search", "Initiate a search query for <keyword>."),
                   6: ("I'm Feeling Bored", "No idea what to search for? Let me help!"),
                   }

        # add the button labels (i.e. their names) and their description
        self.buttons = [self.home_btn, self.news, self.images, self.back, self.forward, self.search_btn, self.bored]
        self.root.update_btns(self.buttons, context)

    def get_tooltip(self):
        return self.tooltip


class Home(tk.Frame):
    """
    The interface for the "Home" page - a frame that contains a canvas that will hold the app's logo
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self["borderwidth"] = 1
        self["relief"] = 'groove'

        self.redCanvas = tk.Canvas(root, width=655, height=500, bg="#F9F9F9", bd=1, highlightthickness=2,
                                   highlightbackground="green")

        # scrollbar is created, but is hidden behind the canvas - since there is nothing to scroll
        # however, having it here makes switching pages more easier
        self.scrollbar = tk.Scrollbar(root, command=self.redCanvas.yview, orient=tk.VERTICAL)

        self.bg = ImageTk.PhotoImage(Image.open("bg.png").resize((600, 88)))
        self.redCanvas.background = self.bg
        self.bg_image = self.redCanvas.create_image(660 / 2, 400 / 2, anchor=tk.CENTER, image=self.bg)

        self.redCanvas.grid(row=2, column=0, columnspan=102, sticky=tk.NW, padx=(10, 0), pady=7)


class Results(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self["borderwidth"] = 5
        self["relief"] = "groove"

        # main canvas (red) that will hold all News search results (blue),
        self.redCanvas = tk.Canvas(root, width=640, height=500, bg="#202020", bd=0, highlightthickness=0)

        # create another canvas (blue) that'll hold search entries
        self.blueCanvas = tk.Canvas(self.redCanvas, width=640, height=450, bg="#F9F9F9", bd=0, highlightthickness=0)
        self.redCanvas.create_window(0, 0, window=self.blueCanvas, anchor=tk.NW, width=640)

        # create scrollbar & assign it to 'red' canvas
        self.scrollbar = tk.Scrollbar(root, command=self.redCanvas.yview, orient=tk.VERTICAL)
        self.redCanvas.config(yscrollcommand=self.scrollbar.set)

        # position the 'red' frame and the scrollbar
        self.redCanvas.grid(row=2, column=0, columnspan=102, sticky=tk.NW, padx=(10, 0), pady=7)
        self.scrollbar.grid(row=2, column=95, columnspan=102, sticky=tk.NS, padx=(6, 0), pady=7)

        # listen for events that would change the size or drag (i.e scroll) the 'blue' canvas
        self.redCanvas.bind("<Configure>", self.update_scrollbar)
        self.redCanvas.bind_all("<MouseWheel>", self.scroll_canvas)

    def scroll_canvas(self, event):
        """

        """
        increment = 0

        if event.delta == 120:
            increment = -1
        elif event.delta == -120:
            increment = 1

        self.redCanvas.yview_scroll(increment, "units")

    def update_scrollbar(self, event):
        """Sets the scrolling region for the canvas"""
        self.redCanvas.configure(scrollregion=self.redCanvas.bbox("all"))


class NewsResults(Results):
    """
    Frame that would hold all the entries (canvas) for news articles.
    """
    def __init__(self, root):
        Results.__init__(self, root)
        self.root = root

        self.news, self.news_canvas, self.canvas_objs = [], [], []

        self.start, self.end = 0, 6

        # add search entries inside the 'blue' canvas
        for i in range(5):
            news = tk.Canvas(self.blueCanvas, height=200, width=615, bg="#F9FFF3", bd=1, highlightthickness=2,
                             highlightbackground="green")
            news.grid(row=i, column=0, sticky=tk.W, padx=(10, 15), pady=(10, 15))
            self.news_canvas.append(news)

        self.root.search_set.forward.bind("<Button-1>", lambda root: self.increase_page(5, True))
        self.root.search_set.back.bind("<Button-1>", lambda root: self.increase_page(-5, False))

    def increase_page(self, num, increase):
        """
        Increases the set of news articles to display when pressing the "Next" button,
        otherwise, decreases the set of news articles when pressing the "Previous" button.
        """

        # currently the max # of news articles that is pulled each time from News API is set to a limit of 15
        if self.end <= 15 and increase is True:
            self.start += num
            self.end += num
            self.set_news(self.news)

        # when "increase" is False, this indicates the user is pressing the "Previous" button
        elif self.start > 0 and increase is False:
            self.start += num
            self.end += num
            self.set_news(self.news)

    def set_news(self, news_list):
        """
        Discards any existing news articles and calls extract_content() to populate new results.
        """
        self.news = news_list

        if len(news_list) == 0:
            return None

        # everytime a new search is performed, any previous news articles shown in the search results
        # area will be discard to make room for the new results
        if len(self.canvas_objs) != 0:
            for canvas in self.news_canvas:
                for x in range(4):
                    canvas.delete(self.canvas_objs.pop(0))

        self.extract_content(news_list)

    def extract_content(self, news_list):
        """
        For the current article, extract its title, publish date, author, and abstract from JSON
        """
        categories = ["title", "publishedAt", "author", "description"]

        # the frame holds up to five news articles at once
        for x in range(5):
            content = []
            if (self.start + x) < len(news_list):
                for y in categories:
                    data = news_list[self.start + x][y]
                    if data is None:
                        data = "N/A"
                    elif y == "publishedAt":
                        # parse the default date string into a date object
                        data = parser.parse(data).date()
                    content.append(data)
            self.create_text(content, x, news_list)

    def create_text(self, content, entry_num, news_list):
        """
        With the article's extracted data, add the title, date, source, and abstract to the current entry (canvas).
        """
        font_color = self.root.toolbar.get_color()

        # add the article's title to the entry
        title = self.news_canvas[entry_num].create_text(5, 25, text=content[0], anchor='nw', width=600,
                                                        fill=font_color, font=("Arial", 10, "bold"))

        # add the date that the article was published to the entry
        date = self.news_canvas[entry_num].create_text(5, 60, text=content[1], anchor='nw', width=600,
                                                       fill=font_color, font=("Arial", 8, "normal"))

        # add the article source to the entry
        source = self.news_canvas[entry_num].create_text(5, 75, text="Source: " + content[2], anchor='nw', width=600,
                                                         fill=font_color, font=("Arial", 8, "normal"))

        # add the article's abstract to the entry
        abstract = self.news_canvas[entry_num].create_text(5, 105, text=content[3], anchor='nw', width=600,
                                                           fill=font_color)

        # add the handler to a list so its iterable later on
        self.canvas_objs.extend((title, date, source, abstract))

        self.news_canvas[entry_num].grid(row=entry_num)
        self.news_canvas[entry_num].bind("<Button-1>",
                                         lambda event, arg=news_list[entry_num]["url"]: self.root.open_link(arg))
        self.news_canvas[entry_num].bind("<Enter>",
                                         lambda event, arg=self.news_canvas[entry_num]: self.mouse_in(arg))

    def close_image(self, arg):
        """
        Destroys the argument widget
        """
        arg.destroy()

    def mouse_in(self, widget):
        """
        The argument widget's default cursor is set to a custom Mario cursor.
        """
        widget["cursor"] = "@mario.ani"


class ImageResults(Results):
    """
    This frame contain canvases where each holds an photo/image, ones from search results.
    """
    def __init__(self, root):
        Results.__init__(self, root)
        self.root = root

        self.images, self.images_canvas = [], []
        self.start, self.end = 0, 9

        # initiate canvases for image(s), where the frame displays up to nine results at once
        for x in range(3):
            for y in range(3):
                image = tk.Canvas(self.blueCanvas, height=180, width=180, bg="#F9FFF3", bd=1, highlightthickness=2,
                                  highlightbackground="green")
                image.grid(row=x, column=y, sticky=tk.W, padx=(15, 15), pady=(15, 15))
                self.images_canvas.append(image)

    def increase_page(self, num, increase):
        """

        """
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
        """
        Discard existing images in all the canvases and replace them with new images from 'img_set'.
        For each image, bind callback functions that allow the user to see larger resolution of the image,
        and also a custom mouse pointer when the image is hovered.
        """
        self.images = img_set

        # clear any existing image and add new image to canvas
        for x in range(9):
            self.images_canvas[x].delete("all")
            if (self.start + x) < len(img_set):
                raw_file = img_set[self.start + x]
                img = ImageTk.PhotoImage(img_set[self.start + x])
                self.images_canvas[x].create_image(0, 0, image=img)
                self.images_canvas[x].bind("<Button-1>", lambda event,
                                                                arg=(img, raw_file): self.enlarge_images(arg))
                self.images_canvas[x].bind("<Enter>",
                                           lambda event, arg=self.images_canvas[x]: self.mouse_in(arg))

    def enlarge_images(self, arg):
        """
        Creates a new toplevel window that contains the image, with the resolution depending on
        the app's setting (small, medium, or large).
        """
        image_window = tk.Toplevel(self)
        image_window.geometry(self.find_img_size(arg))
        image_window.resizable(False, False)
        image_window.iconbitmap("logo64.ico")

        image_label = tk.Label(image_window, image=arg[0])
        image_label.grid(row=0, column=0)

        # allow user to use left-mouse click to close the image, and also a Mario cursor when hovered
        image_label.bind("<Button-1>", lambda event, arg=image_window: self.close_image(arg))
        image_label.bind("<Enter>", lambda event, arg=image_label: self.mouse_in(arg))

    def find_img_size(self, img):
        """
        Takes an image 'img' and find its width and height.
        Return its width and height as a string, "{width}x{height}".
        """
        width = img[1].size[0]
        height = img[1].size[1]
        size = "{width}x{height}".format(width=width, height=height)
        return size

    def close_image(self, arg):
        """
        Destroys the argument widget
        """
        arg.destroy()

    def mouse_in(self, widget):
        """
        The argument widget's default cursor is set to a custom Mario cursor.
        """
        widget["cursor"] = "@mario.ani"


class Toolbar(tk.Menu):
    """
    The main toolbar, made up of four menus: File, View, Advanced, Help.
    """
    def __init__(self, root):
        super().__init__(root)
        self.menu = tk.Menu(self)
        self.root = root

        self.search_history = []

        # this is the list of countries that the user can choose to select headline news from
        # each country has along its ISO country code, which is used by the News API
        self.countries = [("All", "All"), ("Australia", "au"), ("Brazil", "br"), ("Canada", "ca"), ("China", "zh"),
                          ("Germany", "de"), ("United Kingdom", "gb"), ("Hong Kong", "hk"), ("Israel", "il"),
                          ("India", "in"), ("Italy", "it"), ("Japan", "jp"), ("South Korea", "kr"), ("Mexico", "mx"),
                          ("Malaysia", "ma"), ("Russia", "ru"), ("Saudi Arabia", "sa"), ("Singapore", "sg"),
                          ("Thailand", "th"), ("Taiwan", "tw"), ("United States", "us")
                          ]

        # File menu
        self.file = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="File", menu=self.file)

        self.setting = tk.Menu(self.menu, tearoff=0)
        self.setting.add_command(label="Clear History", command=self.show_confirm)
        self.file.add_cascade(label="Settings", menu=self.setting)

        self.file.add_separator()
        self.file.add_command(label="Exit", command=self.exit)

        # View menu
        self.view = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="View", menu=self.view)

        self.searches = tk.Menu(self.view, tearoff=0)
        self.color_mode = tk.Menu(self.view, tearoff=0)
        self.view.add_cascade(label="Theme", menu=self.color_mode)
        self.view.add_separator()
        self.view.add_cascade(label="Search History", menu=self.searches)

        # Set the default items for radio buttons
        self.themes_var = tk.StringVar()
        self.languages = tk.StringVar()
        self.image_var = tk.StringVar()
        self.themes_var.set(self.countries[0][0])
        self.languages.set(1)
        self.image_var.set("medium")
        self.color = tk.StringVar()
        self.color.set("black")

        self.color_mode.add_radiobutton(label="Light", value="black", variable=self.color,
                                        command=lambda: self.change_theme(0))
        self.color_mode.add_radiobutton(label="Dark", value="white", variable=self.color,
                                        command=lambda: self.change_theme(1))

        # Advanced menu
        self.advanced = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Advanced", menu=self.advanced)

        self.themes = tk.Menu(self.advanced, tearoff=0)

        self.advanced.add_cascade(label="News By Location", menu=self.themes)
        self.advanced.add_separator()

        for x in range(len(self.countries)):
            self.themes.add_radiobutton(label=self.countries[x][0], value=self.countries[x][1],
                                        variable=self.themes_var, command=lambda: self.set_en())

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

        # Help menu
        self.help = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Help", menu=self.help)
        self.help.add_command(label="Homepage",
                              command=lambda: self.root.open_link("https://github.com/yu-daniel/CS361"))
        self.help.add_command(label="Tutorial", command=self.show_tutorial)

        self.help.add_separator()
        self.help.add_command(label="About...", command=self.show_about)

    def show_tutorial(self):
        """
        Create and displays the app tutorial.
        """
        Tutorial(self.root)

    def get_countries(self):
        return self.countries

    def get_themes_var(self):
        return self.themes_var.get()

    def get_image_var(self):
        return self.image_var.get()

    def get_color(self):
        return self.color.get()

    def set_en(self):
        self.languages.set(1)

    def set_language(self, language):
        self.themes_var.set(self.countries[0][0])
        self.root.set_language(language)

    def add_search_history(self, keyword):
        """
        Add 'keyword' to the Search History
        """
        self.search_history.append(keyword)
        self.searches.add_command(label=keyword, command=lambda: self.from_history(keyword))

    def from_history(self, keyword):
        """
        When a 'keyword' from Search History menu is clicked, a search is performed again
        using this keyword.
        """
        self.root.image_api(keyword)
        self.root.news_api(keyword)

    def show_confirm(self):
        """
        When initiating Clear History, a confirmation window is displayed to the user,
        asking again to  confirm deleting all history.
        """
        confirm_screen = tk.Toplevel(self)
        root_x = self.root.winfo_x() + 250
        root_y = self.root.winfo_y() + 330

        confirm_screen.geometry("175x50+{x}+{y}".format(x=root_x, y=root_y))
        confirm_screen.resizable(False, False)
        confirm_screen.iconbitmap("logo64.ico")
        confirm_screen.transient(self.root)

        confirm_frame = tk.Frame(confirm_screen)
        confirm_frame.grid(row=0, column=0)

        confirm_msg = tk.Label(confirm_frame, text="Clear all search history?")
        confirm_msg.grid(row=0, column=0, columnspan=2)

        cancel_btn = ColorButtons(confirm_frame)
        cancel_btn.bind("<Button-1>", lambda event, screen=confirm_screen: self.cancel(screen))
        cancel_btn.grid(row=1, column=0, sticky=tk.SW, padx=(10, 0), pady=0)

        ok_btn = ColorButtons(confirm_frame)
        ok_btn.grid(row=1, column=1, sticky=tk.SE, padx=(0, 10), pady=0)
        ok_btn.bind("<Button-1>", lambda event, screen=confirm_screen: self.ok(screen))

        context = {0: ("Cancel", "Cancel operation."),
                   1: ("Confirm", "Confirm operation."),
                   }
        self.root.update_btns([cancel_btn, ok_btn], context)

    def ok(self, screen):
        """
        Delete all keywords (if any) in the Search History list.
        """
        history_total = self.searches.index("end")

        if history_total is not None:
            for num in range(history_total + 1):
                self.searches.delete(0)

        screen.destroy()

    def show_about(self):
        """
        Create a toplevel window that shows the software logo, version, and creator.
        """
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

        version = tk.Label(about_container, text="Version 1.3.0", fg="white", bg="#202020")
        version.grid(row=1, column=0)

        copyright = tk.Label(about_container, text="Copyright 2021 by Daniel Yu", fg="white", bg="#202020")
        copyright.grid(row=2, column=0)

        ok = ColorButtons(about_container)

        ok.grid(row=3, column=0, sticky=tk.SE, padx=(0, 10), pady=(10, 10))
        ok.bind("<Button-1>", lambda event, screen=about: self.cancel(screen))

        context = {0: ("Ok", "Information regarding software version and creator.")}
        self.root.update_btns([ok], context)

    def cancel(self, screen):
        screen.destroy()

    def exit(self):
        """
        Exists the app.
        """
        self.root.quit()

    def change_theme(self, theme):
        """
        Changes each individual component of the UI based on the 'theme' that is selected
        in the toolbar View -> Theme -> Light | Dark
        """
        gray = "#F0F0F0"
        white = "white"
        black = "black"
        medium_gray = "#606060"
        dark_gray = "#202020"
        light_green = "#F6FFEE"
        medium_green = "#CCFFCC"
        leprechaun = "#29CB66"
        yellow = "#FFFF99"

        bar_text, button_default, button_hover, root_UI = None, None, None, None
        canvas_bg, entry_txt, ctn_thickns, bar_thickns = None, None, None, None

        if theme == 0:
            bar_text = medium_gray
            button_default = light_green
            button_hover = medium_green
            root_UI = gray
            canvas_bg = white
            entry_txt = black
            ctn_thickns = 0
            bar_thickns = 1
        else:
            bar_text = leprechaun
            button_default = leprechaun
            button_hover = yellow
            root_UI = dark_gray
            canvas_bg = dark_gray
            entry_txt = black
            ctn_thickns = 1
            bar_thickns = 0

        # the parent (root) frame,
        self.root["bg"] = root_UI
        self.root.root["bg"] = root_UI

        # search field
        self.root.search_set["bg"] = root_UI
        self.root.search_set.search["fg"] = bar_text
        self.root.search_set.search["background"] = canvas_bg

        # text color for the status bar
        self.root.status_container.status_bar.itemconfig(self.root.status_container.status, fill=bar_text)

        # status bar's background and border
        self.root.status_container["bg"] = root_UI
        self.root.status_container["bd"] = 1
        self.root.status_container["highlightthickness"] = ctn_thickns
        self.root.status_container["highlightbackground"] = root_UI

        self.root.status_container.status_bar["bg"] = root_UI
        self.root.status_container.status_bar["bd"] = bar_thickns
        self.root.status_container.status_bar["highlightthickness"] = bar_thickns

        # search results' background
        self.root.home.redCanvas["background"] = canvas_bg
        self.root.news_results.blueCanvas["background"] = canvas_bg
        self.root.image_results.blueCanvas["background"] = canvas_bg

        # search results - news canvas background
        for canvas in self.root.news_results.news_canvas:
            canvas["background"] = canvas_bg

        # search results - images canvas background
        for canvas in self.root.image_results.images_canvas:
            canvas["background"] = canvas_bg

        # each news entry's text color
        for canvas in self.root.news_results.news_canvas:
            for item in self.root.news_results.canvas_objs:
                canvas.itemconfig(item, fill=black)

        # each button's default/hovered color
        for button in self.root.search_set.buttons:
            button["background"] = button_default
            button.set_color(entry_txt, button_default, button_hover)


class Messages:
    def __init__(self, root):
        self.root = root
        self.default = "Status: "
        self.search_field = "System: enter a <keyword> to begin the search."
        self.current = self.default

    def get_current(self):
        return self.current

    def set_current(self, widget):
        self.current = widget


class ColorButtons(tk.Button):
    """
    Modified Tkinter Button widget - changing default the button's default background color
    and also changing color when mouse pointer is hovered over the object.
    """
    def __init__(self, root, **kwargs):
        tk.Button.__init__(self, root, **kwargs)

        self.tip_msg, self.status_canvas, self.status_item, self.fg, self.default = None, None, None, None, True
        self.default_msg, self.bg_default, self.bg_hover = "Status: ", "#F6FFEE", "#CCFFCC"

        # default button color is a "light green" - when app is launched (in light mode)
        self["background"] = self.bg_default

        # change button color as the mouse enter/leaves the button
        self.bind("<Enter>", lambda event, arg=0: self.update_message(arg))
        self.bind("<Leave>", lambda event, arg=1: self.update_message(arg))

    def set_status(self, canvas, item):
        self.status_canvas = canvas
        self.status_item = item

    def set_message(self, msg):
        self.tip_msg = msg

    def update_message(self, arg):
        """
        Updates the status bar's "tip" that corresponds to the current button, and also
        change its default color to the hovered color.
        """
        msg = ""
        if arg == 0:
            msg = self.tip_msg
        elif arg == 1:
            msg = self.default_msg

        self.status_canvas.itemconfig(self.status_item, text=msg)

        if self.default:
            self["background"] = self.bg_hover
            self.default = False
        else:
            self["background"] = self.bg_default
            self.default = True
        time.sleep(0.01)

    def set_color(self, fg, bg_default, bg_new):
        self.fg = fg
        self.bg_default = bg_default
        self.bg_hover = bg_new


class Tutorial(tk.Toplevel):
    """
    Creates a toplevel window that is the Tutorial for the user.
    """
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.root = root

        # find parent window's position to create the toplevel at a specific position
        x = root.winfo_x() + 250
        y = root.winfo_y() + 230

        self.geometry("500x350+{x}+{y}".format(x=x, y=y))
        self.resizable(False, False)
        self.transient(root)

        self.main = tk.Frame(self, bg="#202020")
        self.main.grid(row=0, column=0)

        self.bg = tk.Canvas(self.main, width=500, height=350, bg="green", bd=0, highlightthickness=0)
        self.bg.grid(row=0, column=0, columnspan=3)

        self.cancel = ColorButtons(self.main)
        self.cancel.grid(row=0, column=2, sticky=tk.S)

        self.next = ColorButtons(self.main, )
        self.next.grid(row=0, column=1, sticky=tk.S)

        self.previous = ColorButtons(self.main)
        self.previous.grid(row=0, column=0, sticky=tk.S)

        self.count = 1
        front_img = "test1.jpg"

        self.img = ImageTk.PhotoImage(Image.open(front_img).resize((500, 350)))
        self.bg.background = self.img
        self.bg_image = self.bg.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.cancel.bind("<Button-1>", lambda event, root=self: self.close(root))
        self.next.bind("<Button-1>", lambda event, root=self, increase=True: self.change_tip(root, increase))
        self.previous.bind("<Button-1>", lambda event, root=self, increase=False: self.change_tip(root, increase))

        context = {0: ("Ok", "Exit tutorial."),
                   1: ("Next", "Next tip."),
                   2: ("Previous", "Previous tip."),
                   }
        self.root.update_btns([self.cancel, self.next, self.previous], context)

    def close(self, root):
        root.destroy()

    def change_tip(self, root, increase):
        if self.count < 6 and increase is True:
            self.count += 1
        elif self.count > 1 and increase is False:
            self.count -= 1

        # change the "tip" depending on the current count
        img2 = "test{num}.jpg".format(num=self.count)
        self.img = ImageTk.PhotoImage(Image.open(img2).resize((500, 350)))
        self.bg.itemconfig(self.bg_image, image=self.img)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scramble Engine")  # add title to the app
    root.iconbitmap("logo64.ico")
    root.resizable(False, False)  # don't allow resizing window
    root.geometry("680x650")
    app = Main(root)  # initiate the main interface
    root.mainloop()  # keep Tkinter running
