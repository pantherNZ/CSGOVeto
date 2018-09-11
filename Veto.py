import tkinter as tk
from tkinter import W, E, N, ttk, filedialog
from PIL import Image, ImageTk
import os, glob

"""Class which derives from tkinter, manages the different frames & switching between them"""
class VetoApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Veto Tool")
        self.resizable(0, 0)

        self._frame = None
        self.switch_frame(VetoStartPage, ["hello"])
        self['bg'] = 'black'

    def switch_frame(self, frame_class, data=[]):
        # Destroys current frame and replaces it with a new one.
        new_frame = frame_class(self, data)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

    def run(self):
        self.mainloop()


"""Base frame class"""
class BaseFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

    def set_window(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.master.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.master.minsize(width, height)
        self.master.maxsize(width, height)


"""Start page"""
class VetoStartPage(BaseFrame):
    def __init__(self, master, _):
        tk.Frame.__init__(self, master, bd = 20)
        self.set_window(230, 210)
        spacing = 5
        border = (20, 0)
        self['bg'] = 'black'

        self.info_text = tk.Label(self, text = "Veto Settings:", font = ("Helvetica", 16), bg = 'black', fg = 'white')
        self.info_text.grid(padx = border[0], pady = (border[1], spacing), sticky = W)

        self.team1_text = tk.StringVar()
        self.team1_entry = tk.Entry(self, textvariable = self.team1_text)
        self.team2_text = tk.StringVar()
        self.team2_entry = tk.Entry(self, textvariable = self.team2_text)
        self.team1_text.set("Team A")
        self.team2_text.set("Team B")

        self.team1_entry.grid(row = 1, column = 0, padx = border[0], pady = spacing, sticky = W + E)
        self.team2_entry.grid(row = 2, column = 0, padx = border[0], pady = spacing, sticky = W + E)

        self.gametype_text = tk.StringVar()
        self.gametype_text.set('BO3')
        self.gametype_combo = tk.ttk.Combobox(self, textvariable = self.gametype_text, values = ('BO1', 'BO2', 'BO3', 'BO5'), width = 5)
        self.gametype_combo.grid(row = 3, column = 0, padx = border[0], pady = spacing, sticky = W)

        # Veto data for the various game types (team #, action type, action number)
        veto_data = {
            'BO1': ['1BAN1', '1BAN2', '2BAN1', '2BAN2', '2BAN3', '1BAN3'],
            'BO2': ['1BAN1', '2BAN1', '1PICK1', '2PICK1', 'FINISH'],
            'BO3': ['1BAN1', '2BAN1', '1PICK1', '2PICK1', '1BAN2', '2BAN2'],
            'BO5': ['1BAN1', '2BAN1', '1PICK1', '2PICK1', '1PICK2', '2PICK2'],
        }

        self.beginveto_button = tk.Button(self, text = "Start", command = lambda: master.switch_frame(VetoMainPage, [self.team1_text.get(), self.team2_text.get(), veto_data[self.gametype_combo.get()]]))
        self.beginveto_button.grid(row = 5, column = 0, padx = border[0], pady = (spacing, 0), sticky = W + E)


"""Main program page"""
class VetoMainPage(BaseFrame):
    def __init__(self, master, data):
        tk.Frame.__init__(self, master, bd = 20)
        self.set_window(1100, 700)
        self.selected = -1
        self.state_index = 0
        self.data = data
        self.state = self.data[2][self.state_index]
        self.ordinals = [('first', '1st'), ('second', '2nd'), ('third', '3rd'), ('fourth', '4th'), ('fifth', '5th')]
        self.maps_picked = 0
        self['bg'] = 'black'

        self.info_text = tk.Label(self, text = data[0] + "'s first Veto", font = ("Helvetica", 28), fg = 'white', bg = 'black')
        self.info_text.grid(row = 0, column = 0, columnspan = 5, pady=(0, 20), sticky = W)

        files = glob.glob('maps/*.png')
        self.map_data = []
        map_column, self.map_row = 0, 1

        for file in files:
            img = Image.open(file)
            img.thumbnail((256, 256), Image.ANTIALIAS)
            map_image = ImageTk.PhotoImage(img)
            image_holder = tk.Button(self, compound = tk.TOP, text = os.path.basename(file).split('.')[0], image = map_image, font = ("Helvetica", 16), fg = "white", bg = 'black')
            self.map_data.append((True, image_holder, map_image))
            image_holder['command'] = lambda index = len(self.map_data) - 1: self.button_press(index)
            image_holder.grid(row = self.map_row, column = map_column, columnspan = 2, rowspan = 2, pady = (0, 20 if self.map_row >= 2 else 0))

            map_column += 2
            if map_column >= 8:
                map_column = 0
                self.map_row += 2

        self.confirm_btn = tk.Button(self, text = 'Confirm', font = ("Helvetica", 12), command = self.confirm)
        self.confirm_btn.grid(row = self.map_row, column = map_column, pady = (30, 0), ipadx = 40, columnspan = 2)

        self.map_row += 1

        self.restart_btn = tk.Button(self, text = 'Restart', font = ("Helvetica", 12), command = lambda: master.switch_frame(VetoStartPage))
        self.restart_btn.grid(row = self.map_row, column = map_column, pady = (0, 30), ipadx = 40, columnspan = 2, sticky = N)

        self.export_btn = None
        self.timeline = []

        img = Image.open('csgo_logo.png')
        img.thumbnail((750, 750), Image.ANTIALIAS)
        self.csgo_logo = ImageTk.PhotoImage(img)
        self.logo = tk.Label(self, image = self.csgo_logo, bg = 'black')
        self.logo.grid(row = self.map_row + 1, column = map_column - 1, rowspan = 100, columnspan = 100, sticky = N, ipady = 35)

    def add_to_timeline(self, text, colour):
        self.map_row += 1
        new_label = tk.Label(self, text = text, font = ("Helvetica", 14), fg = colour, bg = 'black')
        new_label.grid(row = self.map_row, column = 0, columnspan = 4, sticky = W)
        self.timeline.append(text)

    def add_export_button(self):
        self.export_btn = tk.Button(self, text = 'Export', font = ("Helvetica", 12), command = lambda: self.file_save())
        self.export_btn.grid(row = 0, column = 6, pady = (10, 30), ipadx = 40, columnspan = 2, rowspan = 2, sticky = N)

    def button_press(self, button_index):
        if self.selected != -1:
            self.map_data[self.selected][1]['fg'] = 'white'
            self.map_data[self.selected][1]['bg'] = 'black'

        if self.map_data[button_index][0] and self.state_index < len(self.data[2]):
            self.selected = button_index
            self.map_data[self.selected][1]['fg'] = 'purple'
            self.map_data[self.selected][1]['bg'] = 'white'

    def confirm(self):
        if self.selected != -1:
            self.map_data[self.selected] = (False, self.map_data[self.selected][1], self.map_data[self.selected][2])
            image_holder = self.map_data[self.selected][1]
            image_holder['bg'] = 'black'

            if self.state.find('BAN') != -1:
                image_holder['fg'] = 'red'
                image_holder['font'] = ("Helvetica", 16, "overstrike")
            else:
                image_holder['fg'] = 'green'
                image_holder['font'] = ("Helvetica", 16, "bold")
                image_holder['text'] = self.ordinals[self.maps_picked][1] + ' map: ' + image_holder['text']
                self.maps_picked += 1

            self.selected = -1
            self.state_index += 1

            previous_team = self.data[int(self.state[0]) - 1]
            self.add_to_timeline(previous_team + (" veto'd " if self.state.find('BAN') != -1 else " picked ") + image_holder['text'], image_holder['fg'])

            if self.state_index >= len(self.data[2]):
                self.info_text['text'] = 'Veto Complete'

                for x in self.map_data:
                    if x[0]:
                        x[1]['text'] = ('Map: ' if self.maps_picked == 0 else self.ordinals[self.maps_picked][1] + ' map: ') + x[1]['text']
                        x[1]['fg'] = 'green'
                        self.add_to_timeline(x[1]['text'], 'green')
                        break

                self.add_export_button()
                return

            self.state = self.data[2][self.state_index]

            if self.state == 'FINISH':
                self.info_text['text'] = 'Veto Complete'
                for x in range(len(self.map_data)):
                    self.map_data[x] = (False, self.map_data[x][1], self.map_data[x][2])

                self.add_export_button()
                return

            current_team = self.data[int(self.state[0]) - 1]
            action_number = self.ordinals[int(self.state[-1]) - 1][0]
            action_name = ("Veto" if self.state.find('BAN') != -1 else "Pick")
            self.info_text['text'] = current_team + "'s " + action_number + " " + action_name

    def file_save(self):
        file = filedialog.asksaveasfile(title = "Save As..", mode='w', defaultextension=".txt", filetypes = (("Text File", "*.txt"), ("All files", "*.*")))
        if file is None:
            return

        for x in self.timeline:
            file.write(x + '\n')

        file.close()


if __name__ == '__main__':
    VetoApp().run()
