from tkinter import *
from tkinter import ttk

class CampFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Seattle Summer Camps Finder")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        # Search criteria
        ttk.Label(main_frame, text="ZIP Code:").grid(row=0, column=0, sticky=W)
        self.zip_code = ttk.Entry(main_frame, width=10)
        self.zip_code.grid(row=0, column=1, sticky=W)
        self.zip_code.insert(0, "98101")
        
        ttk.Label(main_frame, text="Child's Age:").grid(row=1, column=0, sticky=W)
        self.age = ttk.Entry(main_frame, width=5)
        self.age.grid(row=1, column=1, sticky=W)
        self.age.insert(0, "10")
        
        # Search button
        ttk.Button(main_frame, text="Search Camps", command=self.search_camps).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results area
        self.results_text = Text(main_frame, width=50, height=20)
        self.results_text.grid(row=3, column=0, columnspan=2, pady=10)
        
    def search_camps(self):
        # Clear previous results
        self.results_text.delete(1.0, END)
        
        # Demo camp data
        camps = [
            {
                "name": "STEM Discovery Camp",
                "location": "Pacific Science Center",
                "ages": "8-12",
                "dates": "July 10-14, 2025",
                "cost": "$475"
            },
            {
                "name": "Zoo Explorers",
                "location": "Woodland Park Zoo",
                "ages": "9-11",
                "dates": "July 17-21, 2025",
                "cost": "$425"
            },
            {
                "name": "Youth Kayaking",
                "location": "Moss Bay",
                "ages": "10-13",
                "dates": "July 8-12, 2025",
                "cost": "$495"
            }
        ]
        
        # Display results
        self.results_text.insert(END, "Found camps:\n\n")
        for camp in camps:
            self.results_text.insert(END, f"Name: {camp['name']}\n")
            self.results_text.insert(END, f"Location: {camp['location']}\n")
            self.results_text.insert(END, f"Ages: {camp['ages']}\n")
            self.results_text.insert(END, f"Dates: {camp['dates']}\n")
            self.results_text.insert(END, f"Cost: {camp['cost']}\n")
            self.results_text.insert(END, "\n" + "-"*40 + "\n\n")

if __name__ == "__main__":
    root = Tk()
    app = CampFinder(root)
    root.mainloop()
