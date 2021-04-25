import tkinter as tk


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()  # using Tkinter's grid system over pack

        # initiate the main toolbar
        self.toolbar = Toolbar(self)
        root.config(menu=self.toolbar)

        # add results area
        # self.box = Box(self)
        self.box = tk.Frame(self, bg="#3463ad", width=660, height=500)



        # add buttons to the UI
        self.news = tk.Button(self, text="News")
        self.images = tk.Button(self, text="Images")
        self.videos = tk.Button(self, text="Videos")
        self.search_btn = tk.Button(self, text="Search")
        self.bored = tk.Button(self, text="I'm Feeling Bored")

        # add search field
        self.search = tk.Entry(self, width=100)
        self.search.insert(0, "Enter <keyword> to search...")
        self.search.bind("<Button-1>", self.search_text)
        self.search_btn.bind("<Button-1>", self.click_search)

        # position of objects (buttons, search entry, labels)
        self.news.grid(row=0, column=0, sticky=tk.W, padx=(10, 3), pady=7)
        self.images.grid(row=0, column=1, sticky=tk.W, padx=3, pady=7)
        self.videos.grid(row=0, column=2, sticky=tk.W, padx=3, pady=7)
        self.bored.grid(row=0, column=3, sticky=tk.W, padx=3, pady=7)

        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=(10, 10), pady=7)
        self.search_btn.grid(row=1, column=101, sticky=tk.W, padx=(0, 10))

        self.box.grid(row=2, column=0, columnspan=102, sticky=tk.W, padx=(10, 0), pady=7)









    def delete_text(self, event):
        self.search.delete(0, tk.END)

    def add_text(self, event):
        print('hi')
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
            self.search.insert(0, "Enter <keyword> to search...")
            root.focus()


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
        super().__init__(root, bg="#3463ad")


        self.grid()  # using Tkinter's grid system over pack

        self.addLabel = tk.Label(self, text="Ticker: ")
        self.addLabel.grid(row=0, column=0, sticky=tk.W, padx=10, pady=7)

        self.addEntry = tk.Entry(self, width=15, fg="#3463ad")
        self.addEntry.grid(row=1, column=0, sticky=tk.W, padx=50, pady=7)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Scramble Engine")  # add title to the app
    root.resizable(False, False)  # don't allow resizing window
    root.geometry("680x620")
    app = Main(root)  # initiate the main interface
    root.mainloop()  # keep Tkinter running