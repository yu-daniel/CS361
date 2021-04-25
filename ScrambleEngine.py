import tkinter as tk

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()                 # using Tkinter's grid system over pack

        # initiate the main toolbar
        self.toolbar = Toolbar(self)
        root.config(menu=self.toolbar)

        # add News/Images/Videos button
        self.news = tk.Button(self, text="News")
        self.images = tk.Button(self, text="Images")
        self.videos = tk.Button(self, text="Videos")

        # add search field
        self.search = tk.Entry(self, width=100)

        # position of objects (buttons, search entry, labels)
        self.news.grid(row=0, column=0, sticky=tk.W, padx=2, pady=7)
        self.images.grid(row=0, column=1, sticky=tk.W, padx=2, pady=7)
        self.videos.grid(row=0, column=2, sticky=tk.W, padx=2, pady=7)
        self.search.grid(row=1, column=0, columnspan=100, sticky=tk.W, padx=10, pady=7)


class Toolbar(tk.Menu):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.menu = tk.Menu(self)

        # file menu
        self.file = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="File")

        # fiew menu
        self.view = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="View")

        # help menu
        self.help = tk.Menu(self.menu, tearoff=0)
        self.add_cascade(label="Help")



if __name__ == '__main__':
    root = tk.Tk()
    root.title("Scramble Engine")       # add title to the app
    app = Main(root)                    # initiate the main interface
    root.mainloop()                     # keep Tkinter running
