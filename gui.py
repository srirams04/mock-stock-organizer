#Import of Modules
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from functools import partial
import ctypes
import weakref
import os
from colorsys import rgb_to_hls, hls_to_rgb
from requests import post

#Import of Created Files
import constant
import logic

class CustomButton(Button):
    def __init__(self, master, hover = False, hover_text = '', hover_bg = "#000000", hover_fg = "#FFFFFF", *args, **kwargs):
        super().__init__(master, *args, **kwargs, activebackground = constant.ACTIVEBGCLR, activeforeground = constant.ACTIVEFGCLR)

        if hover:
            self.bind("<Enter>", lambda e: self.onHoverShowButton())
            self.hover_text = hover_text
            self.hover_bg = hover_bg
            self.hover_fg = hover_fg
        else:
            self.bind("<Enter>", lambda e: self.onEnter())
    
    def onEnter(self):
        org_bg = self['bg']
        conv_org_bg = tuple(int(org_bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        
        new_bg = '#%02x%02x%02x' % darken_color(*conv_org_bg, 0.2)
        
        self.config(bg = new_bg)
        
        def onLeave(e):
            if new_bg == self['bg']:
                self.config(bg = org_bg)
            self.unbind("<Leave>")
            
        self.bind("<Leave>", onLeave)
    
    def onHoverShowButton(self):
        org_bg = self['bg']
        new_bg = self.hover_bg
        
        org_fg = self['fg']
        new_fg = self.hover_fg
        
        org_text = self['text']
        
        def onLeave(e):
            self.config(text = org_text, bg = org_bg, fg = org_fg)
            self.unbind("<Leave>")
            
        self.config(text = self.hover_text, bg = new_bg, fg = new_fg)
        self.bind("<Leave>", onLeave)
        
      
class TaggedEntry(Entry):
    
    def __init__(self, master, tags, onEntryUpdate, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.tags = list(tags)
        self.config(state = 'readonly')
        self.onEntryUpdate = onEntryUpdate
        if 'readonly' not in tags:
            self.bind("<Double-Button-1>", lambda e: self.onDoubleClick())
        if 'highlight' in tags:       
            self.bind("<ButtonPress-1>", lambda e: self.onButtonPress())
        
    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
        if tag == 'readonly':
            self.unbind("<Double-Button-1>")
    

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
        else:
            raise ValueError(f'Tag \'{tag}\' not found.')
        
        if tag == 'readonly':
            self.bind("<Double-Button-1>", lambda e: self.onDoubleClick())


    def get_tags(self):
        return self.tags


    def onDoubleClick(self):
        org_text = self.get()
        org_bg = self['bg']
        org_fg = self['fg']
        self.config(state = NORMAL, bg = "white", fg = "black")
        self.focus_set()
        
        
        
        def onReturn(e):
            self.config(state = 'readonly')
            
            self.onEntryUpdate(self.get(), org_text)
            
            if 'theme' in self.get_tags():
                self.config(bg = theme_bg, fg = theme_fg)
            else:
                self.config(bg = org_bg, fg = org_fg)
            
            self.unbind("<Return>")
            self.bind("<Double-Button-1>", lambda e: self.onDoubleClick())
        
        
        def onFocusOut_2(e):
            self.delete(0, END)
            self.insert(INSERT, org_text)
            self.config(state = 'readonly')
            
            if 'theme' in self.get_tags():
                self.config(bg = theme_bg, fg = theme_fg)
            else:
                self.config(bg = org_bg, fg = org_fg)
                
            self.unbind("<FocusOut>", funcid_focus_out)
            self.bind("<Double-Button-1>", lambda e: self.onDoubleClick())
            
        self.unbind("<Double-Button-1>")
        self.bind("<Return>", onReturn)
        funcid_focus_out = self.bind("<FocusOut>", onFocusOut_2, add = True)

    
    def onButtonPress(self):
        org_bg = self['readonlybackground']
        conv_org_bg = tuple(int(org_bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        
        new_bg = '#ABBEE5'
        
        self.config(readonlybackground = new_bg)
    
        def onFocusOut_1(e):
            if 'theme' in self.tags:
                self.config(readonlybackground = theme_bg)
            else:
                self.config(readonlybackground = org_bg)
            self.unbind("<FocusOut>", funcid_focus_out)
            self.bind("<ButtonPress-1>", lambda e: self.onButtonPress())
        
        self.unbind("<ButtonPress-1>")
        funcid_focus_out = self.bind("<FocusOut>", onFocusOut_1, add = True)
            
            
class EntryManager():
    
    def __init__(self) -> None:
        self.entries = weakref.WeakSet()

    def create_entry(self, master, tags, text,  func, default_row, default_column, *args, **kwargs) -> None:
        entry = TaggedEntry(master, tags, func, *args, **kwargs)
        entry.ROW = default_row
        entry.COLUMN = default_column
        entry.config(readonlybackground = entry['bg'])
        entry.config(state = NORMAL)
        entry.insert(INSERT, text)
        entry.config(state = 'readonly')
        self.entries.add(entry)
        return entry
    

    def delete_entry(self, tags, columnconfigure = True):
        entries = tuple(self.entries)
        for entry in entries:
            if set(tags) <= set(entry.tags):
                try:
                    if columnconfigure == True:
                        entry.master.grid_columnconfigure(entry.COLUMN, weight = 0)
                    self.entries.remove(entry)
                    entry.destroy()
                except:
                    pass
  
  
    def modify(self, tags, text):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.config(state = NORMAL)
                    entry.delete(0, END)
                    entry.insert(INSERT, text)
                    entry.config(state = 'readonly')
                except:
                    pass


    def clear(self, tags):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.config(state = NORMAL)
                    entry.delete(0, END)
                    entry.config(state = 'readonly')
                except:
                    pass


    def add_tag(self, tags, tag):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.add_tag(tag)
                except:
                    pass
    

    def remove_tag(self, tags, tag):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.remove_tag(tag)
                except:
                    pass


    def change_bg(self, tags, bg_clr, readonly_bg_clr = ''):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.config(bg = bg_clr)
                    if readonly_bg_clr == '':
                        continue
                    entry.config(readonlybackground = readonly_bg_clr)
                except:
                    pass
                    

    def change_fg(self, tags, fg_clr):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.config(fg = fg_clr)
                except:
                    pass
    

    def hide(self, tags, columnconfigure = True):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    if columnconfigure == True:
                        entry.master.grid_columnconfigure(entry.COLUMN, weight = 0)
                    entry.grid_forget()
                except:
                    pass
            
            
    def show(self, tags, columnconfigure = True):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    if columnconfigure == True:
                        entry.master.grid_columnconfigure(entry.COLUMN, weight = 1)  
                    entry.grid(row = entry.ROW, column = entry.COLUMN, sticky = NSEW, ipadx = 5, ipady = 5)
                except:
                    pass
       
       
    def get(self, tags): #Applicable only for those TaggedEntries which have a unique tag tuple and tags should contain the complete set of tags
        value = "N/A"
        for entry in self.entries:
            if set(tags) == set(entry.tags):
                value = entry.get()
                break
        return value.strip()
        
        
    def change_entry_update_function(self, tags, func):
        for entry in self.entries:
            if set(tags) <= set(entry.tags):
                try:
                    entry.onEntryUpdate = func
                except:
                    pass

    
class ScrolledFrame(Frame):
    def __init__(self, parent, max_height, *args, **kwargs):
        super().__init__(parent, *args, **kwargs) # create a frame (self)

        #Storing the value of max_height
        self.max_height = max_height
        
        #place canvas on self
        self.canvas = Canvas(self, *args, **kwargs)
        
        #place a frame on the canvas, this frame will hold the child widgets
        self.viewPort = Frame(self.canvas, *args, **kwargs)
        
        #place a vertical scrollbar on self
        self.vsb = Scrollbar(self, orient= VERTICAL)
        
        #Setting the command for vertical scrollbar
        self.vsb.config(command = self.canvas.yview)
        
        #pack the vertical scrollbar to right of self
        self.vsb.pack(side = RIGHT, fill = Y)
        
        #attach scrollbar action to scroll of canvas
        self.canvas.configure(yscrollcommand = self.vsb.set)
        
        #pack canvas to left of self and expand to fil
        self.canvas.pack(side = TOP, fill = 'both', expand = True)
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw")
        
        #bind an event whenever the size of the viewPort frame changes.
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        
        #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        
        #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize
        self.onFrameConfigure(None)

        self.viewPort.bind('<Enter>', self._bound_to_mousewheel)
        self.viewPort.bind('<Leave>', self._unbound_to_mousewheel)


    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)


    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def onFrameConfigure(self, event):
        viewPort_ht = self.viewPort.winfo_height()
        
        if viewPort_ht < self.max_height:
            self.canvas.config(height = viewPort_ht)
        else:
            self.canvas.config(height = self.max_height)
        
        #whenever the size of the frame changes, alter the scroll region respectively.
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
  
    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width

        #whenever the size of the canvas changes alter the window region respectively.
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)
    
    
    def config(self, **kwargs):
        self.viewPort.config(**kwargs)
        self.canvas.config(**kwargs)
        self.viewPort.update_idletasks()
        self.canvas.update_idletasks()
    
    
    def configure(self, **kwargs):
        self.viewPort.config(**kwargs)
        self.canvas.config(**kwargs)
        self.viewPort.update_idletasks()
        self.canvas.update_idletasks()
    
     
def adjust_color_lightness(r, g, b, factor):
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)
    
    
def lighten_color(r, g, b, factor=0.1):
    return adjust_color_lightness(r, g, b, 1 + factor)


def darken_color(r, g, b, factor=0.1):
    return adjust_color_lightness(r, g, b, 1 - factor) 


def switch_theme():
    global theme, theme_bg, theme_fg, manager_entry, tuple_theme_frames, tuple_theme_labels, label_message, active_messages
    
    if theme == "dark":
        theme = "light"
        theme_bg = constant.LIGHTBGCLR
        theme_fg = constant.LIGHTBGTEXTCLR

    elif theme == "light":
        theme = "dark"
        theme_bg = constant.DARKBGCLR
        theme_fg = constant.DARKBGTEXTCLR
    

    root.config(bg = theme_bg)    
    
    #Updating the theme of label_message
    label_message.config(bg = theme_bg)
    try:
        if theme == "light":
            if active_messages[-1][0] == 'error':
                label_message.config(fg = constant.ERRORDARKFGCLR)
            elif active_messages[-1][0] == 'update':
                label_message.config(fg = constant.UPDATEDARKFGCLR)
        elif theme == "dark":
            if active_messages[-1][0] == 'error':
                label_message.config(fg = constant.ERRORLIGHTFGCLR)
            elif active_messages[-1][0] == 'update':
                label_message.config(fg = constant.UPDATELIGHTFGCLR)
    except:
        pass
        
    for widget in tuple_theme_frames:
        try:
            widget.config(bg = theme_bg)
        except:
            pass

    for widget in tuple_theme_labels:
        try:
            widget.config(bg = theme_bg, fg = theme_fg)
        except:
            pass

    manager_entry.change_bg(('theme',), theme_bg, theme_bg)
    manager_entry.change_fg(('theme',), theme_fg)
        
    root.update_idletasks() 

    
def switch_tab(tab_name):
    global tab_frames, tab_buttons, active_tab
    
    #Taking off the previous tab_frame and also setting the tab button to the default colour
    try:
        tab_frames[active_tab].grid_forget()
        tab_buttons[active_tab].config(bg = constant.TERTIARYCLR)
    except NameError:
        pass
    
    #Placing the new tab frame and also highlighting the corresponding tab button
    tab_frames[tab_name].grid(row = 2, column = 0, padx = 10, pady = 5, sticky = 'new')
    tab_buttons[tab_name].config(bg = constant.HIGHLIGHTCLR)

    #Modifying active_tab
    active_tab = tab_name


def switch_action_frame(name):
    global active_action_frame, action_frames
    if name != active_action_frame:
        active_action_frame = name
        if name == "minor action":
            action_frames['tab action'].grid_forget()
            action_frames['major action'].grid_forget()
            action_frames['minor action'].grid(row = 3, column = 0, sticky = 'sew', padx = 10, pady = 5)
        elif name == "major action":
            action_frames['tab action'].grid_forget()
            action_frames['minor action'].grid_forget()
            action_frames['major action'].grid(row = 3, column = 0, sticky = 'sew', padx = 10, pady = 5)
        elif name == "tab action":
            action_frames['major action'].grid_forget()
            action_frames['minor action'].grid_forget()
            action_frames['tab action'].grid(row = 3, column = 0, sticky = 'sew', padx = 10, pady = 5)
        

def transact_shares():
    global globe, tab_frames, combo_company, combo_buying_company, combo_selling_company, combo_affected_company, entry_shares, entry_price,  manager_entry

    company_name = combo_company.get()
    selling_company_name = combo_selling_company.get()
    buying_company_name = combo_buying_company.get()
    
    if not company_name.strip():
        display_error("Select Stock Company")
        return
    
    if not selling_company_name.strip():
        display_error("Select Selling Company")
        return
    
    if not buying_company_name.strip():
        display_error("Select Buying Company")
        return

    try:
        raw_shares = entry_shares.get()
        shares = int(raw_shares)
        if not(shares > 0):
            raise ValueError
    except ValueError:
        display_error("Number of Shares must be a positive integer")
        
        action = f'inv-{mod(company_name)}: {mod(selling_company_name)} wants to sell {mod(raw_shares)} shares to {mod(buying_company_name)} (Number of Shares must be a positive integer)'
        update_log(action)
        return

    try:
        raw_price = entry_price.get()
        price = round(float(raw_price), 2)
        if not(price >= 0):
            raise ValueError
    except ValueError:
        error = 'Price must be a non-negative integer or float'
        display_error(error)
        
        action = f'inv-{mod(company_name)}: {mod(selling_company_name)} wants to sell {shares} shares to {mod(buying_company_name)} at ${mod(raw_price)} ({mod(error)})'
        update_log(action)
        return

    
    if selling_company_name == buying_company_name:
        display_error("Buying and Selling Companies must be different")
        
        action = f'inv-{mod(company_name)}: {mod(selling_company_name)} wants to sell {shares} shares to {mod(buying_company_name)} at ${price} (Buying and Selling Companies must be different)'
        update_log(action)
        combo_buying_company.set('')
        return

    try:
        globe.transact_shares(company_name, selling_company_name, buying_company_name, shares, price)  
    except Exception as error:
        display_error(error)
        
        action = f'inv-{mod(company_name)}: {mod(selling_company_name)} wants to sell {shares} shares to {mod(buying_company_name)} at ${price} ({mod(error)})'
        update_log(action)
        return 

    
    update_indirect_changes()
    
    #Updating log file and log tab
    action = f'ts-{mod(company_name)}-{mod(selling_company_name)}-{mod(buying_company_name)}-{shares}-{price}'
    update_log(action)
    
    combo_company.set('')
    combo_selling_company.set('')
    combo_buying_company.set('')
    entry_shares.delete(0, END)
    entry_price.delete(0, END)


def update_pr_crisis():
    global globe, combo_affected_company, combo_pr_crisis

    company_name = combo_affected_company.get()

    if not company_name.strip():
        display_error("Select Affected Company")
        return

    try:
        pr_crisis = int(combo_pr_crisis.get())
        if not (pr_crisis in tuple(range(0,11))):
            raise ValueError
    except ValueError:
        display_error("Select PR Crisis Index")
        return

    try:
        globe.release_pr_crisis(company_name, pr_crisis)
    except Exception as error:
        display_error(error)
        action = f"inv-{mod(company_name)} hit by grade {pr_crisis} PR CRISIS ({mod(error)})"
        update_log(action)
        return
    
    update_indirect_changes()
    
    #Updating log file and log tab
    action = f"prc-{mod(company_name)}-{pr_crisis}"
    update_log(action)
    
    combo_affected_company.set('')
    combo_pr_crisis.set('')


def update_pr_response():
    global globe, frame_stock_table, frame_investors_table, combo_recovered_company, combo_pr_response, label_message

    company_name = combo_recovered_company.get()
    
    if not company_name.strip():
        display_error("Select Recovered Company")
        return

    try:
        pr_response = int(combo_pr_response.get())
        if not(pr_response in tuple(range(0,11))):
            raise ValueError
    except ValueError:
        display_error("Select PR Response Index")
        return
    
    try:
        globe.release_pr_response(company_name, pr_response)
    except Exception as error:
        display_error(error)
        action = f"inv-{mod(company_name)} released grade {pr_response} PR RESPONSE ({mod(error)})"
        update_log(action)
        return

    update_indirect_changes()
    
    #Updating log file and log tab
    action = f"prr-{mod(company_name)}-{pr_response}"
    update_log(action)
    
    combo_recovered_company.set('')
    combo_pr_response.set('')


def update_entry(company_name, field, text, org_text):
    global globe, manager_entry
    
    existing_companies = tuple(i.lower() for i in globe.companies.keys())
    if field.lower() == "name" and text.lower() in existing_companies:
        display_error("Company name taken! Think of a new one.")
        manager_entry.modify((company_name, "name"), org_text)
        
        action = f"inv-Rename {mod(company_name)} to {mod(text)} (Company name taken! Think of a new one.)"
        update_log(action)
            
        return
    
    
    if not text or "," in text:
        if field.lower() == "name":
            error = "Company name must be a non-empty string [commas not allowed]"
            display_error(error)
            manager_entry.modify((company_name, "name"), org_text)
            
            action = f"inv-Rename {mod(company_name)} to {mod(text)} ({mod(error)})"
            update_log(action)
            return
        elif field.lower() == "owners":
            display_error("Owners must be a non empty string [commas not allowed]")
            manager_entry.modify((company_name, "owners"), org_text)

            action = f"inv-{mod(company_name)}: change Owners FROM {mod(org_text)} to {mod(text)} (Owners must be a non empty string [commas not allowed])"
            update_log(action)
            return
        elif field.lower() == "location":
            display_error("Location must be a non empty string [commas not allowed]")
            manager_entry.modify((company_name, "location"), org_text)
            
            action = f"inv-{mod(company_name)}: change Location FROM {mod(org_text)} to {mod(text)} (Location must be a non empty string [commas not allowed])"
            update_log(action)
            return
        
        
    if field.lower() == "capital":
        try:
            capital = float(text)
            if not(capital >= 0):
                raise ValueError
        except ValueError:
            error = "Capital must be a non-negative float or integer"
            display_error(error)
            manager_entry.modify((company_name, "capital"), org_text)

            action = f"inv-{mod(company_name)}: change Capital FROM {mod(org_text)} to {mod(text)} ({mod(error)})"
            update_log(action)
            return
   

    if field.lower() == "stock price":
        try:
            stock_price = float(text)
            if not(stock_price >= 0):
                raise ValueError
        except ValueError:
            error = "Stock price must be a non-negative float or integer"
            display_error(error)
            manager_entry.modify((company_name, "stock price"), org_text)
            
            action = f"inv-{mod(company_name)}: change Stock Price FROM {mod(org_text)} to {mod(text)} ({mod(error)})"
            update_log(action)
            return
       
       
    if field.lower() == "name":
        new_company_name = text
        
        possible_fields = globe.stock_file_fields
        for possible_field in possible_fields:
            func = partial(update_entry, new_company_name, possible_field)
            manager_entry.change_entry_update_function((company_name, possible_field), func)
        
        manager_entry.add_tag((company_name, ), new_company_name)
        manager_entry.remove_tag((new_company_name,), company_name)
        
        for i in tuple(globe.companies.keys()):
            if i != company_name:
                manager_entry.add_tag((f'{company_name} --> {i}',), f'{new_company_name} --> {i}')
                manager_entry.remove_tag((f'{new_company_name} --> {i}',), f'{company_name} --> {i}')
                
                manager_entry.add_tag((f'{i} --> {company_name}',), f'{i} --> {new_company_name}')
                manager_entry.remove_tag((f'{i} --> {new_company_name}',), f'{i} --> {company_name}')
        manager_entry.add_tag((f'{company_name} --> {company_name}',), f'{new_company_name} --> {new_company_name}')
        manager_entry.remove_tag((f'{new_company_name} --> {new_company_name}',), f'{company_name} --> {company_name}')
        
        globe.rename(company_name, new_company_name)
        manager_entry.modify((new_company_name, field), text)
        
        #Updating log file and tab
        action = f"chgname-{mod(company_name)}-{mod(new_company_name)}"
        update_log(action)
        
        #Updating all the combo_companies
        update_combo_companies()
        
        return
               
    
    elif field.lower() == "capital":
        capital = text
        globe.set_capital(company_name, round(float(capital), 2))
        
        #Updating log file and tab
        action = f"chgcapital-{mod(company_name)}-{org_text}-{capital}"
        update_log(action)
    
    elif field.lower() == "stock price":
        stock = round(float(text), 2)
        globe.set_stock(company_name, stock)
        
        #Updating log file and tab
        action = f"chgstock-{mod(company_name)}-{org_text}-{stock}"
        update_log(action)
        
        
    elif field.lower() == "owners":
        owners = text
        globe.set_owners(company_name, owners)
        
        #Updating log file and tab
        action = f"chgowners-{mod(company_name)}-{mod(org_text)}-{mod(owners)}"
        update_log(action)
        
        
    elif field.lower() == "location":
        location = text
        globe.set_location(company_name, location)
        
        #Updating log file and tab
        action = f"chglocation-{mod(company_name)}-{mod(org_text)}-{mod(location)}"
        update_log(action)
        
        
    manager_entry.modify((company_name, field), text)   


def update_log(fen_action):
    global log_file_name, tab_frames, audit_log_row_count
    
    #Updating the action to the log file
    file = open(log_file_name, 'a')
    text = '/' + fen_action
    file.write(text)
    file.close()
    

    
    #Adding the action to the audit_log_tab
    frame = tab_frames['audit log']
    label_color_code = Label(frame.viewPort, text = '     ', font = ('Consolas', 17), bd = 1, relief = "ridge")
    label_color_code.grid(row = audit_log_row_count, column = 0, sticky = NSEW, ipadx = 5, ipady = 5)
    
    entry_readonly_action = Entry(frame.viewPort, bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR, font = ('Consolas', 17), bd = 1, relief = "ridge")
    entry_readonly_action.grid(row = audit_log_row_count, column = 1, sticky = NSEW, ipadx = 5, ipady = 5)
    
    action = decode_fen_string(fen_action)
    entry_readonly_action.insert(INSERT, ' ' * 3 + action)
    entry_readonly_action.config(state = 'readonly')
    
    action_name = fen_action.strip('/\t\r\n ').split('-', 1)[0]
    log_color_code(action_name, label_color_code)
    
    button_revert = CustomButton(frame.viewPort, hover = True, hover_text = 'REVERT', hover_bg = constant.REVERTBGCLR, hover_fg = "white", text = '      ', bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR, font = ('Consolas', 17, 'bold'), command = partial(revert, audit_log_row_count), bd = 0, highlightthickness = 0)
    button_revert.grid(row = audit_log_row_count, column = 2, sticky = EW, ipadx = 5, ipady = 5)
        
    audit_log_row_count += 1
    
    
    #Displaying the update at the bottom of the screen as well
    if action_name != 'inv':
        display_update(action)
    
    if action_name == 'ts':
        post_msg_on_discord(action)
    
    post_log_on_discord()

    
def decode_fen_string(fen_string):
    x = fen_string.strip('/\t\r\n ').split('-')
    
    x = [unmod(i) for i in x]
    
    if x[0] == 'inv':
        action = unmod(x[1])
    elif x[0] == 'cc':
        company_name = x[1]
        action = f"Created a company named {company_name}"
    elif x[0] == 'dc':
        company_name = x[1]
        action = f"Deleted {company_name}"
    elif x[0] == 'ts':
        stock_company_name = x[1]
        selling_company_name = x[2]
        buying_company_name = x[3]
        shares = x[4]
        price = x[5]
        action = f"{stock_company_name}: {selling_company_name} sold {shares} shares to {buying_company_name} at ${price}"
    elif x[0] == 'prc':
        company_name = x[1]
        pr_crisis = x[2]
        action = f"{company_name} hit by grade {pr_crisis} PR crisis"
    elif x[0] == 'prr':
        company_name = x[1]
        pr_response = x[2]
        action = f"{company_name} released grade {pr_response} PR response"
    elif x[0] == 'chgname':
        old_company_name = x[1]
        new_company_name = x[2]
        action = f"{old_company_name} renamed to {new_company_name}"
    elif x[0] == 'chgowners':
        company_name = x[1]
        org_text = x[2]
        owners = x[3]
        action = f"{company_name}: Owners changed from {org_text} to {owners}"
    elif x[0] == 'chgcapital':
        company_name = x[1]
        org_text = x[2]
        capital = x[3]
        action = f"{company_name}: Capital changed from {org_text} to {capital}"
    elif x[0] == 'chgstock':
        company_name = x[1]
        org_text = x[2]
        stock_price = x[3]
        action = f"{company_name}: Stock Price changed from {org_text} to {stock_price}"
    elif x[0] == 'chglocation':
        company_name = x[1]
        org_text = x[2]
        location = x[3]
        action = f"{company_name}: Location changed from {org_text} to {location}"
    else:
        raise ValueError(f'Invalid Operation: {x[0]}')
    
    return action
    
    
def log_color_code(action_name, label):
    if action_name == 'ts':
        label.config(bg = constant.TRANSACTSHARESCLR, fg = constant.TRANSACTSHARESCLR)

    elif action_name == 'prc':
        label.config(bg = constant.PRCRISISCLR, fg = constant.PRCRISISCLR)
        
    elif action_name == 'prr':
        label.config(bg = constant.PRRESPONSECLR, fg = constant.PRRESPONSECLR)
 
    elif action_name == "inv":
        label.config(bg = constant.INVALIDOPRCLR, fg = constant.INVALIDOPRCLR)
    
    elif action_name == "cc":
        label.config(bg = constant.CREATECOMPANYCLR, fg = constant.CREATECOMPANYCLR)
    
    elif action_name == "dc":
        label.config(bg = constant.DELETECOMPANYCLR, fg = constant.DELETECOMPANYCLR)
    
    else:
        label.config(bg = constant.MODIFYVALUECLR, fg = constant.MODIFYVALUECLR)
       
      
def update_indirect_changes():
    global globe, tuple_previous_tags
    
    for tags in tuple_previous_tags:
        manager_entry.change_bg(tags, constant.LIGHTBGCLR, constant.LIGHTBGCLR)

    tuple_tags = globe.latest_indirect_changes
    
    for tags in tuple_tags:
        company_name = tags[0]
        if 'capital' in tags:
            manager_entry.modify(tags, globe.get_capital(company_name))
        elif 'stock price' in tags:
            manager_entry.modify(tags, globe.get_stock(company_name))
        elif 'latest stock change' in tags:
            manager_entry.modify(tags, globe.get_latest_stock_change(company_name))
        elif 'pr crisis' in tags:
            manager_entry.modify(tags, globe.get_pr_crisis(company_name))
        elif 'pr response' in tags:
            manager_entry.modify(tags, globe.get_pr_response(company_name))
        elif 'stock drop (pr)' in tags: 
            manager_entry.modify(tags, globe.get_stock_drop_pr_crisis(company_name))
        elif 'shares fraction' in tags:
            #In this elif condition alone company_name which has been calculated above is actually not the company name
            share_flow = tags[0]
            company_name, investor_name = share_flow.strip().split(' --> ')
            value = f'{globe.get_investor_shares(company_name, investor_name)} / {globe.get_shares(company_name)}'

                
            manager_entry.modify(tags, value)
        manager_entry.change_bg(tags, constant.MODIFIEDCLR, constant.MODIFIEDCLR)
    
    tuple_previous_tags = tuple_tags


def create_investors_tab():
    global globe, frame_investors_table, list_label_fields
    
    #Creating a frame to contain the table
    frame_investors_table = ScrolledFrame(root, bg = theme_bg, bd = 0, highlightthickness = 0, max_height = 387)

    #Gridding frame_investors_table
    frame_investors_table.viewPort.grid_columnconfigure(tuple(range(0, len(globe.companies) + 1)), weight = 1)

    #Filling the contents of frame_investors_table
    existing_companies = list(globe.companies.keys()) #returns the names of all the companies in globe
    investors_data = [None]
    investors_data[0] = [''] + existing_companies
    
    for stock_company_name in existing_companies:
        record = [stock_company_name]
        for investor_name in existing_companies:
            x = globe.get_investor_shares(stock_company_name, investor_name)
            record.append(x)
        investors_data.append(record)
        
        
    row = 0
    for col in range(len(investors_data[0])):
        company_name = investors_data[0][col]
        entry_x = manager_entry.create_entry(frame_investors_table.viewPort, ('investors tab', 'name', company_name, 'readonly', 'theme'), company_name, lambda e: None, default_row = row, default_column = col, font  = ('Comic Sans', 17), bd = 1, relief = "ridge", bg = theme_bg, fg = theme_fg, justify = CENTER)
        entry_x.grid(row = row, column = col, sticky = NSEW, ipadx = 5, ipady = 5)

    row = 1
    for record in investors_data[1:]:
        col = 0
        
        total_shares = 0
        for i in record[1:]:
            total_shares += int(float(i))
    
        for value in record:
            if col == 0:
                company_name = value
                entry_x = manager_entry.create_entry(frame_investors_table.viewPort, ('investors tab', 'name', company_name, 'readonly', 'theme'), company_name, lambda e: None, default_row = row, default_column = col, font = ('Comic Sans', 17, 'bold'),  bd = 1, relief = "ridge", justify = CENTER, bg = theme_bg, fg = theme_fg)
            else:
                stock_company_name = record[0]
                shares_company_name = investors_data[0][col]
                entry_x = manager_entry.create_entry(frame_investors_table.viewPort, ('investors tab', 'shares fraction', f'{stock_company_name} --> {shares_company_name}', 'readonly', 'highlight'), f'{int(float(value))} / {total_shares}', lambda e: None, default_row = row, default_column = col, bd = 1, relief = "ridge", justify = CENTER, font  = ('Comic Sans', 17), bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR)
            entry_x.grid(row = row, column = col, sticky = NSEW, ipadx = 5, ipady = 5)
            col+=1
        row += 1
    return frame_investors_table


def create_audit_log_tab():
    global audit_log_row_count, log_file_name, world_name
    
    #Creating a frame for the audit log tab
    frame_audit_log = ScrolledFrame(root, bd = 0, highlightthickness = 0, bg = theme_bg, max_height = 387)
    
    #Gridding frame_audit_log.viewPort
    frame_audit_log.viewPort.grid_columnconfigure(1, weight = 1)
    
    #Initialising the value of the row count
    audit_log_row_count = 0
    
    #Getting the file contents
    folder_name = f'World {world_name}'
    log_file_name = f'./{folder_name}/log.txt'
    

    try:
        file = open(log_file_name, 'r')
    except:
        file = open(log_file_name, 'w')
    
    fen_actions = file.read().strip('/\t\r\n ').split('/')
    if fen_actions == ['']:
        fen_actions = []
    file.close()
    
    for fen_action in fen_actions: #It is called fen action because every action is in the form of a fen string
        action = decode_fen_string(fen_action)
            
        action_name = fen_action.strip('/\t\r\n ').split('-', 1)[0]

        label_color_code = Label(frame_audit_log.viewPort, text = '     ', font = ('Consolas', 17), bd = 1, relief = "ridge")
        label_color_code.grid(row = audit_log_row_count, column = 0, sticky = NSEW, ipadx = 5, ipady = 5)
        
        entry_readonly_action = Entry(frame_audit_log.viewPort, bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR, font = ('Consolas', 17), bd = 1, relief = "ridge")
        entry_readonly_action.grid(row = audit_log_row_count, column = 1, sticky = NSEW, ipadx = 5, ipady = 5)
        
        entry_readonly_action.insert(INSERT, ' ' * 3 + action)
        entry_readonly_action.config(state = 'readonly')
        
        log_color_code(action_name, label_color_code)
        
        button_revert = CustomButton(frame_audit_log.viewPort, hover = True, hover_text = 'REVERT', hover_bg = constant.REVERTBGCLR, hover_fg = "white", text = '      ', bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR, font = ('Consolas', 17, 'bold'), command = partial(revert, audit_log_row_count), bd = 0, highlightthickness = 0)
        button_revert.grid(row = audit_log_row_count, column = 2, sticky = EW, ipadx = 5, ipady = 5)
        
        audit_log_row_count += 1

    return frame_audit_log
    
    
def create_world(_world_name):
    global world_name
    
    #Initialising the name of the world
    world_name = _world_name
    
    #Initialising all the folder and files required
    folder_name = f'World {world_name}'
    
    os.mkdir(folder_name)
    
    for file_name in ('Companies.csv', 'Investors.csv', 'config.txt', 'log.txt'):
        file = open(folder_name + '/' + file_name, 'w')
        if file_name == 'Companies.csv':
            text = "name,owners,location,capital,stock price,shares,pr crisis,pr response,stock drop (pr),latest stock change\n"
            file.write(text)
        elif file_name == 'Investors.csv':
            file.write(",\n")
        elif file_name == "config.txt":
            text = "Title : double click to edit; hit enter to save"
            file.write(text)
        file.close()
        
    open_world(_world_name)
    
    
def open_world(_world_name):
    global globe, world_name, frame_home, frame_buttons, tab_buttons, tab_frames, tab_fields, action_frames, active_tab, active_action_frame, tuple_theme_frames, tuple_previous_tags, tuple_combo_companies
    
    
    #Creating a function when the close button is clicked
    def on_root_close():
        dump_config_file()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", partial(on_root_close))
    
    #Initialising the name of the world
    world_name = _world_name
    
    #Updating the title of the root to the world name
    root.title(f'World {world_name}')
    
    #Deleting frame_home first
    frame_home.destroy()

    #Resetting the weight of root
    root.grid_rowconfigure(1, weight = 0)

    #Changing the default font of combobox drop downs.
    font_combo_listbox = font.Font(family="Comic Sans", size = 17, weight = "normal")
    root.option_add("*TCombobox*Listbox*Font", font_combo_listbox)


    #Getting world ready to handle all the transactions and also initalising the companies data in it
    folder_name = f'World {world_name}'
    globe = logic.World(f"./{folder_name}/Companies.csv", f"./{folder_name}/Investors.csv")
           
    
    #Creating a dictionary of the form - tab name : tab buttons
    tab_buttons = {}
    
    #Creating a dictionary of the form - tab name : tab frame
    tab_frames = {}
    
    #Creating a dictionary of the form - tab name : tab fields
    tab_fields = {}
    
    #Initialising tuple_previous_tags
    tuple_previous_tags = ()
    
    #Reading the title, tab, tab columns details
    try:
        file = open(f'./{folder_name}/config.txt', 'r')
    except:
        file = open(f'./{folder_name}/config.txt', 'w')
    
    try:
        config_data = file.readlines()
    except:
        config_data = []
        
    try:
        world_title = config_data[0].strip()
    except:
        world_title = "Title : double click to edit; hit enter to save"
        
    try:
        tab_names = tuple(i.strip() for i in config_data[1].strip().split(','))
        _ = config_data[2].strip().split(',')
    except:
        tab_names = []
    
    file.close()

    #Changing the title at the top of root to world_title
    manager_entry.modify(('title',), world_title)
    
    #Creating a frame to hold all the tab buttons
    frame_buttons = Frame(root, bd = 0, highlightthickness = 0, bg = theme_bg)
    frame_buttons.grid(row = 1, column = 0, sticky = 'new', padx = 5, pady = 5)
    tuple_theme_frames += (frame_buttons,)

    #Gridding frame_buttons
    frame_buttons.grid_columnconfigure(tuple(range(len(tab_names) + 2)), weight = 1) #2 is added because Investors and Audit Log would be present always (default)...so these tabs are not even added to config.txt

    #--------------------------Creating all the tab buttons----------------------------
    
    #First comes the audit log tab
    col = 0
    button_x = CustomButton(frame_buttons, text = 'AUDIT LOG', font = ("Comic Sans", 17, 'bold'), bg = constant.TERTIARYCLR, fg = "white", command = partial(switch_tab, 'audit log'))
    button_x.grid(row = 0, column = col, sticky = NSEW, ipadx = 5, ipady = 5)
    tab_buttons['audit log'] = button_x
    
    col += 1
    #Then comes the investors tab
    button_x = CustomButton(frame_buttons, text = 'INVESTORS', font = ("Comic Sans", 17, 'bold'), bg = constant.TERTIARYCLR, fg = "white", command = partial(switch_tab, 'investors'))
    button_x.grid(row = 0, column = col, sticky = NSEW, ipadx = 5, ipady = 5)
    tab_buttons['investors'] = button_x
    
    col += 1
    for tab_name in tab_names:
        button_x = CustomButton(frame_buttons, text = tab_name.upper(), font = ("Comic Sans", 17, 'bold'), bg = constant.TERTIARYCLR, fg = "white", command = partial(switch_tab, tab_name))
        button_x.grid(row = 0, column = col, sticky = NSEW, ipadx = 5, ipady = 5)
        tab_buttons[tab_name] = button_x
        col += 1



    #-----------------------Creating all the tab frames-------------------------------
    
    #Creating the audit log tab frame first
    frame_x = create_audit_log_tab()
    tab_frames['audit log'] = frame_x
    
    #Creating the investors tab frame
    frame_x = create_investors_tab()
    tab_frames['investors'] = frame_x 
    
    count = 2
    for tab_name in tab_names:
        fields = tuple(config_data[count].strip().split(','))
        tab_fields[tab_name] = fields
        frame_x = create_tab(tab_name, fields)
        tab_frames[tab_name] = frame_x
        count+=1
       
    
    for frame in tab_frames:
        tuple_theme_frames += (frame, )
        
    #Tab displayed will be the investors tab
    switch_tab('investors')
    
    action_frames = {}
    action_frames['minor action'] = create_minor_action_frame()
    action_frames['major action'] = create_major_action_frame()
    action_frames['tab action'] = create_tab_action_frame()
    action_frames['minor action'].grid(row = 3, column = 0, sticky = 'sew', padx = 10, pady = 5)
    active_action_frame = 'minor action'
    
    tuple_combo_companies = (combo_affected_company, combo_buying_company, combo_company, combo_delete_company, combo_recovered_company, combo_selling_company)
    

def update_combo_companies():
    global globe, tuple_combo_companies
    
    #Updating all the comboboxes which the company names as their values
    companies = tuple(globe.companies.keys())

    for combo in tuple_combo_companies:
        combo['values'] = companies 
        if combo.get() not in companies:
            combo.set('')
    
      
def create_company():
    global entry_company_name, entry_owners, entry_location, entry_capital, entry_stock_price, entry_init_shares, tab_frames
    
    company_name = entry_company_name.get()
    owners = entry_owners.get()
    location = entry_location.get()
    
    if not company_name or "," in company_name:
        error = "Company name must be a non-empty string [commas not allowed]"
        display_error(error)
        
        action = f"inv-Create company named {mod(company_name)} ({mod(error)})"
        update_log(action)
        return
    
    if not owners or "," in owners:
        display_error("Owners must be a non empty string [commas not allowed]")

        action = f"inv-Create company named {mod(company_name)} with Owners as {mod(owners)} (Owners must be a non empty string [commas not allowed])"
        update_log(action)
        return
    
    if not location or "," in location:
        display_error("Location must be a non empty string [commas not allowed]")
        
        action = f"inv-Create company named {mod(company_name)} with Location {mod(location)} (Location must be a non empty string [commas not allowed])"
        update_log(action)
        return
    
    try:
        raw_capital = entry_capital.get()
        capital = float(raw_capital)
        if not(capital >= 0):
            raise ValueError
    except ValueError:
        error = "Capital must be a non-negative float or integer"
        display_error(error)
        action = f"inv-Create company named {mod(company_name)} with Capital of {mod(raw_capital)} ({mod(error)})"
        update_log(action)
        return
    
    try:
        raw_stock_price = entry_stock_price.get()
        stock_price = float(raw_stock_price)
        if not(stock_price >= 0):
            raise ValueError
    except ValueError:
        error = "Stock price must be a non-negative float or integer"
        display_error(error)

        action = f"inv-Create company named {mod(company_name)} with Stock Price of {mod(raw_stock_price)} ({mod(error)})"
        update_log(action)
        return
    
    try:
        raw_shares = entry_init_shares.get()
        shares = int(raw_shares)
        if not(shares > 0):
            raise ValueError
    except ValueError:
        display_error("Shares must be a positive integer")
        
        action = f"inv-Create company named {mod(company_name)} having {mod(raw_shares)} shares (Shares must be a positive integer)"
        update_log(action)
        return
    
    try:
        globe.open_company(company_name, owners, location, capital, stock_price, shares)
    except logic.InvalidCompanyError as error:
        display_error(error)

        action = f"inv-Create company named {mod(company_name)} ({mod(error)})"
        update_log(action)
        return
        
    company = globe.companies[company_name]
    
    #Getting all possible fields from globe
    possible_fields = globe.stock_file_fields
    
    record = (company.name, company.owners, company.location, company.capital, company.stock, company.shares, company.pr_crisis, company.pr_response, company.stock_drop_pr_crisis, company.latest_stock_change)
    
    reqd_tab_frames = tab_frames.copy()
    reqd_tab_frames.pop('investors')
    reqd_tab_frames.pop('audit log')
    
    for tab_name, frame in reqd_tab_frames.items():
        row = 1 + len(globe.companies)
        col = 0
        for value in record:
            company_name = record[0]
            field = possible_fields[col]
  
            entry_x = manager_entry.create_entry(frame.viewPort, (tab_name, company_name, field), value, partial(update_entry, company_name, field), default_row = row, default_column = col, font = ('Comic Sans', 17), bd = 1, relief = "ridge", bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR)
            
            if field in ('shares', 'pr crisis', 'pr response', 'stock drop (pr)', 'latest stock change'):
                entry_x.add_tag('readonly')
            
            col+=1
        for desired_field in tab_fields[tab_name]:
            manager_entry.show((tab_name, company_name, desired_field))
    
    #Updating the log file and the table
    action = f"cc-{mod(company_name)}-{mod(owners)}-{mod(location)}-{capital}-{stock_price}-{shares}"
    update_log(action)
    
    #Resetting the values of the entry boxes
    entry_company_name.delete(0, END)
    entry_owners.delete(0, END)
    entry_location.delete(0, END)
    entry_capital.delete(0, END)
    entry_stock_price.delete(0, END)
    entry_init_shares.delete(0, END)
    
    update_combo_companies()
    
    #Updating the investors tab
    tab_frames['investors'].destroy()
    tab_frames['investors'] = create_investors_tab()
    if active_tab == "investors":
        tab_frames['investors'].grid(row = 2, column = 0, padx = 10, pady = 5, sticky = 'new')
       
        
def delete_company():
    global combo_delete_company, globe
    company_name = combo_delete_company.get()
    if not company_name:
        display_error("Select Company")
        return
    for name, company in globe.companies.items():
        if name != company_name and company_name in tuple(company.get_investors().keys()):
            display_error("Invalid closure due to unsold shares in other companies")
            
            action = f"inv-Delete {mod(company_name)} (Invalid closure due to unsold shares in other companies)"
            update_log(action)
            return
            
    globe.close_company(company_name)
    manager_entry.delete_entry((company_name,), False)
    
    #Updating the log file and the table
    action = f"dc-{mod(company_name)}"
    update_log(action)
    
    #Resetting the value of the combobox
    combo_delete_company.set('')
    
    update_combo_companies()
    
    #Updating the investors tab
    tab_frames['investors'].destroy()
    tab_frames['investors'] = create_investors_tab()
    if active_tab == "investors":
        tab_frames['investors'].grid(row = 2, column = 0, padx = 10, pady = 5, sticky = 'new')
    

def create_tab(tab_name, desired_fields):
    global globe
    
    #Creating a frame for the tab
    frame = ScrolledFrame(root, bg = theme_bg, bd = 0, highlightthickness = 0, max_height = 387)


    #Getting all possible fields from globe
    possible_fields = globe.stock_file_fields

    #Creating and placing all the field headings like name, location, owners, etc
    col = 0
    for field in possible_fields:
        entry_x = manager_entry.create_entry(frame.viewPort, (tab_name, field, 'theme', 'readonly'), field.upper(), lambda e: None, default_row = 0, default_column = col, font  = ('Comic Sans', 17, 'bold'), bd = 1, relief = "ridge", bg = theme_bg, fg = theme_fg)
        col += 1
    
    #Getting the records for all the companies from globe
    stock_data = []
    for company in globe.companies.values():
        name = company.get_name()
        owners = company.get_owners()
        location = company.get_location()
        capital = company.get_capital()
        stock = company.get_stock()
        shares = company.get_shares()
        pr_crisis = company.get_pr_crisis()
        pr_response = company.get_pr_response()
        pr_stock_drop = company.get_stock_drop_pr_crisis()
        latest_stock_change = company.get_latest_stock_change()
        
        stock_data.append((name, owners, location, capital, stock, shares, pr_crisis, pr_response, pr_stock_drop, latest_stock_change))

    row = 1
    for record in stock_data:
        col = 0
        for value in record:
            company_name = record[0]
            field = possible_fields[col]
            
            entry_x = manager_entry.create_entry(frame.viewPort, (tab_name, company_name, field, 'highlight'), value, partial(update_entry, company_name, field), default_row = row, default_column = col, font = ('Comic Sans', 17), width = frame.winfo_width() // 9, bd = 1, relief = "ridge", bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR)
            
            if field in ('shares', 'pr crisis', 'pr response', 'stock drop (pr)', 'latest stock change'):
                entry_x.add_tag('readonly')
            
            col+=1
        row += 1
    
    #Making the desired fields visible
    for field in desired_fields:
        manager_entry.show((tab_name, field,))

    return frame
 
    
def create_tab_action_frame():
    global tuple_theme_frames, tuple_theme_labels, entry_create_tab, combo_delete_tab, combo_tab_name
    
    def init_new_tab():
        global entry_create_tab, tuple_theme_frames, tab_buttons, tab_frames, tab_fields, frame_buttons
        
        tab_name = entry_create_tab.get().lower()
        
        if not tab_name or "," in tab_name:
            display_error("Tab name must be a non-empty string [commas not allowed]")
            return
        elif tab_name in tuple(tab_buttons.keys()):
            display_error("Tab name taken. Think of a new one!")
            return
        
        #Creating a tab button and adding it to tab_buttons
        col = len(tab_buttons)
        frame_buttons.grid_columnconfigure(col, weight = 1)
        
        button_x = CustomButton(frame_buttons, text = tab_name.upper(), font = ("Comic Sans", 17, 'bold'), bg = constant.TERTIARYCLR, fg = "white", command = partial(switch_tab, tab_name))
        button_x.grid(row = 0, column = col, sticky = NSEW, ipadx = 5, ipady = 5)
        
        tab_buttons[tab_name] = button_x
        
        #Creating the tab frame
        frame = create_tab(tab_name, ())
        
        #Adding it to all the required storage variables
        tab_frames[tab_name] = frame
        tab_fields[tab_name] = () 
        tuple_theme_frames += (frame,)
        tab_fields[tab_name] = ()
        
        
        #Modifying the values of tab_name combobox and delete tab combobox
        combo_tab_name['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
        combo_delete_tab['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
        
        #Setting the value of the combobox and entry to ''
        entry_create_tab.delete(0, END)
        
        
    def delete_tab():
        global combo_delete_tab, combo_tab_name, tuple_theme_frames, tab_buttons, tab_frames, tab_fields, frame_buttons, active_tab
        
        tab_name = combo_delete_tab.get().lower()
        if not tab_name:
            display_error("Select Tab")
            return
            
        col = tuple(tab_buttons.keys()).index(tab_name)
        frame_buttons.grid_columnconfigure(col, weight = 0)
        
        #If tab name chosen at the bottom is the tab deleted, then 
        if combo_tab_name.get().lower() == tab_name:
            combo_tab_name.set('')
            hide_checklabels()
        
        #If the tab displayed at the top is the deleted tab, go to investors tab default
        if active_tab == tab_name:
            switch_tab('investors')
            
        tab_buttons[tab_name].destroy()
        
        del tab_buttons[tab_name]
        del tab_frames[tab_name]
        del tab_fields[tab_name]
        
        #Modifying the values of tab_name combobox and delete tab combobox
        combo_tab_name['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
        combo_delete_tab['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
        
        #Setting the values of the combobox to ''
        combo_delete_tab.set('')
       
    
    def clear_create_tab():
        global entry_create_tab
        entry_create_tab.delete(0, END)
    
    
    def clear_delete_tab():
        global combo_delete_tab
        combo_delete_tab.set('')
        
        
    #Creating the tab action frame
    frame_tab_action = Frame(root, bg = theme_bg, bd = 0, highlightthickness = 0)
    
    #Gridding frame_tab_action
    frame_tab_action.grid_columnconfigure((1,2), weight = 1)
    
    #Creating a "<" label on the left to move to the minor action frame
    label_minor_action = Label(frame_tab_action, text = "<", bg = theme_bg, fg = theme_fg, font = ('Consolas', 50, 'bold'))
    label_minor_action.grid(row = 0, column = 0, rowspan = 2, sticky = NSEW, padx = 10, pady = 5)
    label_minor_action.bind("<Button-1>", lambda e: partial(switch_action_frame, 'minor action')())
    
    #--------------------------------Creating a frame to create a tab----------------------------
    frame_create_tab = Frame(frame_tab_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    
    #Gridding frame_create_tab
    frame_create_tab.grid_columnconfigure((0,1), weight = 1)
    
    label_create_tab = Label(frame_create_tab, text = "CREATE TAB", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_create_tab.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    label_tab_name = Label(frame_create_tab, text = "Tab Name", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_tab_name.grid(row = 1, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    
    entry_create_tab = Entry(frame_create_tab, font = ('Comic Sans', 17))
    entry_create_tab.grid(row = 1, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    
    button_clear_create_tab = CustomButton(frame_create_tab, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_create_tab)
    button_clear_create_tab.grid(row = 2, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)
    
    button_create_tab = CustomButton(frame_create_tab, text = "CREATE", bg = constant.SECONDARYCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = init_new_tab)
    button_create_tab.grid(row = 2, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)
        
    #------------------------------------Creating a frame to delete a tab--------------------------
    frame_delete_tab = Frame(frame_tab_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    
    #Gridding frame_delete_tab
    frame_delete_tab.grid_columnconfigure((0,1), weight = 1)
    
    label_delete_tab = Label(frame_delete_tab, text = "DELETE TAB", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_delete_tab.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    combo_delete_tab = ttk.Combobox(frame_delete_tab, font = ('Comic Sans', 17), state = 'readonly')
    combo_delete_tab['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
    combo_delete_tab.grid(row = 1, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    button_clear_delete_tab = CustomButton(frame_delete_tab, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_delete_tab)
    button_clear_delete_tab.grid(row = 2, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)
    
    button_delete_tab = CustomButton(frame_delete_tab, text = "DELETE", bg = constant.DANGERCLR, fg = "white", font = ('Comic Sans', 17, 'bold'),  command = delete_tab)
    button_delete_tab.grid(row = 2, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)
    
    #------------------------------------Creating a frame to edit fields in a tab----------------------------------------------
    
    #Creating onTabSelect to execute the display_checklabels function after getting the tab_name
    def onTabSelect():
        global combo_tab_name
        tab_name = combo_tab_name.get().lower()
        if not tab_name:
            display_error("Select Tab")
            return
        
        display_checklabels(tab_name)
    
    
    #Creating a function to process any change made in the fields
    def toggle(tab_name, field, widget, event):
        global tab_fields
        if widget['text'][0] == "✓":
            text = f'  {field.upper()}'
            widget.config(text = text)
            lst = list(tab_fields[tab_name])
            lst.remove(field)
            tab_fields[tab_name] = tuple(lst)
            manager_entry.hide((tab_name,field))
        else:
            text = f'✓ {field.upper()}'
            widget.config(text = text)
            tab_fields[tab_name] += (field,)
            manager_entry.show((tab_name,field))
       
       
    #Creating a function which will take the tab name as parameter and display all the checkbutton-like-labels
    def display_checklabels(tab_name):
        global tuple_checklabels, globe
        try:
            for widget in tuple_checklabels:
                widget.destroy()
        except:
            pass
        tuple_checklabels = ()
        possible_fields = tuple(globe.stock_file_fields)
        desired_fields = tuple(tab_fields[tab_name])
        row = 0
        frame_field_choices.viewPort.grid_columnconfigure(0, weight = 1)
        for field in possible_fields:
            if field in desired_fields:
                text = f'✓ {field.upper()}'
            else:
                text = f'  {field.upper()}'
            
            x = Label(frame_field_choices.viewPort, text = text, font = ('Comic Sans', 17), bg = constant.LIGHTBGCLR, fg = constant.LIGHTBGTEXTCLR, bd = 1, relief = "ridge")
            x.grid(row = row, column = 0, sticky = NSEW, padx = 50, pady = 1, ipadx = 5, ipady = 5)
            x.bind("<Button-1>", partial(toggle, tab_name, field, x))
            tuple_checklabels += (x,)
            row += 1
                
            
    def hide_checklabels():
        global tuple_checklabels, globe
        try:
            for widget in tuple_checklabels:
                widget.destroy()
        except:
            pass
            
            
    frame_edit_tab_fields = Frame(frame_tab_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    
    #Gridding frame_edit_tab_fields
    frame_edit_tab_fields.grid_columnconfigure(0, weight = 1)
    
    label_edit_tab_fields = Label(frame_edit_tab_fields, text = "EDIT TAB COLUMNS", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_edit_tab_fields.grid(row = 0, column = 0, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    #Creating a combobox to get the tab name
    combo_tab_name = ttk.Combobox(frame_edit_tab_fields, font = ('Comic Sans', 17), state = 'readonly', justify = CENTER)
    
    combo_tab_name['values'] = tuple((tab.upper() for tab in tuple(tab_fields.keys())))
    combo_tab_name.grid(row = 1, column = 0, sticky = NSEW, padx = 10, pady = 5, ipadx = 5, ipady = 5)
    combo_tab_name.bind("<<ComboboxSelected>>", lambda e: onTabSelect())
    
    frame_field_choices = ScrolledFrame(frame_edit_tab_fields, bg = theme_bg, bd = 0, highlightthickness = 0, max_height = 280)
    frame_field_choices.grid(row = 2, column = 0, sticky = NSEW, padx = 5, pady = 5)
        
    #---------------Placing frame_create_tab, frame_delete_tab and frame_edit_tab_fields
    frame_create_tab.grid(row = 0, column = 1, sticky = 'new', padx = 50, pady = 5)
    frame_delete_tab.grid(row = 1, column = 1, sticky = 'new', padx = 50, pady = 5)
    frame_edit_tab_fields.grid(row = 0, column = 2, rowspan = 2, sticky = 'new', padx = 50, pady = 5)
    
    #----------Adding the theme based frames and labels to tuple_theme_frames and tuple_theme_labels
    tuple_theme_frames += (frame_tab_action, frame_create_tab, frame_delete_tab, frame_edit_tab_fields, frame_field_choices.viewPort)
    tuple_theme_labels += (label_create_tab, label_delete_tab, label_tab_name, label_minor_action, label_edit_tab_fields)
    
    #Managing focus
    frame_tab_action.bind("<Button-1>", lambda e: frame_tab_action.focus_set())
    frame_create_tab.bind("<Button-1>", lambda e: frame_create_tab.focus_set())
    frame_delete_tab.bind("<Button-1>", lambda e: frame_delete_tab.focus_set())
    frame_edit_tab_fields.bind("<Button-1>", lambda e: frame_edit_tab_fields.focus_set())
    
    label_create_tab.bind("<Button-1>", lambda e: label_create_tab.focus_set())
    label_delete_tab.bind("<Button-1>", lambda e: label_delete_tab.focus_set())
    label_edit_tab_fields.bind("<Button-1>", lambda e: label_edit_tab_fields.focus_set())
    label_tab_name.bind("<Button-1>", lambda e: label_tab_name.focus_set())
    
    
    return frame_tab_action
  
  
def create_major_action_frame():
    global entry_company_name, entry_owners, entry_location, entry_capital, entry_stock_price, entry_init_shares, combo_delete_company, tuple_theme_frames, tuple_theme_labels
    
    def clear_create_company():
        global entry_company_name, entry_owners, entry_location, entry_stock_price, entry_capital, entry_init_shares
        entry_company_name.delete(0, END)
        entry_owners.delete(0, END)
        entry_location.delete(0, END)
        entry_stock_price.delete(0, END)
        entry_capital.delete(0, END)
        entry_init_shares.delete(0, END)
        
        
    def clear_delete_company():
        global combo_delete_company
        combo_delete_company.set('')
        
        
    #Creating the major action frame
    frame_major_action = Frame(root, bg = theme_bg, bd = 0, highlightthickness = 0)

    #Gridding frame_major_action
    frame_major_action.grid_columnconfigure((0,1), weight = 1)

    #Adding the ">" button on the right to go to the minor action frame
    label_minor_action = Label(frame_major_action, text = ">", bg = theme_bg, fg = theme_fg, font = ('Consolas', 50, 'bold'))
    label_minor_action.grid(row = 0, column = 2, sticky = NSEW, padx = 10, pady = 5)
    label_minor_action.bind("<Button-1>", lambda e: partial(switch_action_frame, 'minor action')())

    #Creating a frame to create companies
    frame_create_company = Frame(frame_major_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_create_company.grid(row = 0, column = 0, sticky = 'new', padx = 50, pady = 5)
    
    #Gridding frame_create_company
    frame_create_company.grid_columnconfigure((0,1), weight = 1)
    
    #Creating the label to tell them what is the task is
    label_create_company =Label(frame_create_company, text = "CREATE COMPANY", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_create_company.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)

    
    #Creating the labels required for transacting share
    label_company_name = Label(frame_create_company, text = "Company Name", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_owners = Label(frame_create_company, text = "Owners", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_location = Label(frame_create_company, text = "Location", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_capital = Label(frame_create_company, text = "Capital", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_stock_price = Label(frame_create_company, text = "Stock Price", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_init_shares = Label(frame_create_company, text = "Shares", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')

    #Creating entries required for transacting share
    entry_company_name = Entry(frame_create_company, font = ('Comic Sans', 17))
    entry_owners= Entry(frame_create_company, font = ('Comic Sans', 17))
    entry_location = Entry(frame_create_company, font = ('Comic Sans', 17))
    entry_capital = Entry(frame_create_company, font = ('Comic Sans', 17))
    entry_stock_price = Entry(frame_create_company, font = ('Comic Sans', 17))
    entry_init_shares = Entry(frame_create_company, font = ('Comic Sans', 17))


    #Placing all the labels above
    label_company_name.grid(row = 1, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_owners.grid(row = 2, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_location.grid(row = 3, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_capital.grid(row = 4, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_stock_price.grid(row = 5, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_init_shares.grid(row = 6, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    
    #Placing all the entries above
    entry_company_name.grid(row = 1, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_owners.grid(row = 2, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_location.grid(row = 3, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_capital.grid(row = 4, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_stock_price.grid(row = 5, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_init_shares.grid(row = 6, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the reset button
    button_clear_create_company = CustomButton(frame_create_company, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_create_company)
    button_clear_create_company.grid(row = 7, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)

    #Creating the create button
    button_create_company = CustomButton(frame_create_company, text = "CREATE", bg = constant.SECONDARYCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = create_company)
    button_create_company.grid(row = 7, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)

    #Creating a frame to delete companies
    frame_delete_company = Frame(frame_major_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_delete_company.grid(row = 0, column = 1, sticky = 'new', padx = 50, pady = 5)
    
    #Gridding frame_delete_company
    frame_delete_company.grid_columnconfigure((0,1), weight = 1)
    
    #Adding all the contents of frame_delete_company
    label_delete_company = Label(frame_delete_company, text = "DELETE COMPANY", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_delete_company.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)

    combo_delete_company = ttk.Combobox(frame_delete_company, font = ('Comic Sans', 17), state = 'readonly')
    combo_delete_company['values'] = tuple(globe.companies.keys())
    combo_delete_company.grid(row = 1, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the delete button
    button_clear_delete_company = CustomButton(frame_delete_company, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_delete_company)
    button_clear_delete_company.grid(row = 2, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the delete button
    button_delete_company = CustomButton(frame_delete_company, text = "DELETE", bg = constant.DANGERCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = delete_company)
    button_delete_company.grid(row = 2, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)

    #Adding all the theme based frames to tuple_theme_frames
    tuple_theme_frames += (frame_create_company, frame_delete_company, frame_major_action)

    #Adding all the theme based labels to tuple_theme_labels
    tuple_theme_labels += (label_minor_action, label_create_company, label_delete_company, label_company_name, label_capital, label_location, label_owners, label_init_shares, label_stock_price)

    #Managing focus
    frame_major_action.bind("<Button-1>", lambda e: frame_major_action.focus_set())
    frame_create_company.bind("<Button-1>", lambda e: frame_create_company.focus_set())
    frame_delete_company.bind("<Button-1>", lambda e: frame_delete_company.focus_set())

    label_create_company.bind("<Button-1>", lambda e: label_create_company.focus_set())
    label_company_name.bind("<Button-1>", lambda e: label_company_name.focus_set())
    label_owners.bind("<Button-1>", lambda e: label_owners.focus_set())
    label_location.bind("<Button-1>", lambda e: label_location.focus_set())
    label_capital.bind("<Button-1>", lambda e: label_capital.focus_set())
    label_stock_price.bind("<Button-1>", lambda e: label_stock_price.focus_set())
    label_init_shares.bind("<Button-1>", lambda e: label_init_shares.focus_set())
    
    label_delete_company.bind("<Button-1>", lambda e: label_delete_company.focus_set())
    
    return frame_major_action


def create_minor_action_frame():
    global tuple_theme_frames, tuple_theme_labels, combo_company, combo_buying_company, combo_selling_company, combo_affected_company, combo_recovered_company, combo_pr_crisis, combo_pr_response, entry_shares, entry_price 
    
    def clear_transact_shares():
        global combo_company, combo_selling_company, combo_buying_company, entry_shares, entry_price
        combo_company.set('')
        combo_selling_company.set('')
        combo_buying_company.set('')
        entry_shares.delete(0, END)
        entry_price.delete(0, END)
     
     
    def clear_pr_crisis():
        global combo_affected_company, combo_pr_crisis
        combo_affected_company.set('')
        combo_pr_crisis.set('')
        
    
    def clear_pr_response():
        global combo_recovered_company, combo_pr_response
        combo_recovered_company.set('')
        combo_pr_response.set('')
        
        
    #Creating the minor action frame
    frame_minor_action = Frame(root, bg = theme_bg, bd = 0, highlightthickness = 0)

    #Gridding frame_minor_action
    frame_minor_action.grid_columnconfigure((1,2,3), weight = 1)
    

    #Adding the "<" button on the left to go to the major action frame
    label_major_action = Label(frame_minor_action, text = "<", bg = theme_bg, fg = theme_fg, font = ('Consolas', 50, 'bold'))
    label_major_action.grid(row = 0, column = 0, sticky = NSEW, padx = 10, pady = 5)
    label_major_action.bind("<Button-1>", lambda e: partial(switch_action_frame, 'major action')())
    
    #Adding the ">" button on the right to go to the tab action frame
    label_tab_action = Label(frame_minor_action, text = ">", bg = theme_bg, fg = theme_fg, font = ('Consolas', 50, 'bold'))
    label_tab_action.grid(row = 0, column = 4, sticky = NSEW, padx = 10, pady = 5)
    label_tab_action.bind("<Button-1>", lambda e: partial(switch_action_frame, 'tab action')())
    
    #Creating a transact share frame and gridding it
    frame_transact_shares = Frame(frame_minor_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_transact_shares.grid(row = 0, column = 1, sticky = NSEW, padx = 5, pady = 5)
    
    #Gridding frame_transact_shares
    frame_transact_shares.grid_columnconfigure((0,1), weight = 1)

    #Creating the label to tell them what is the task is
    label_transact_shares = Label(frame_transact_shares, text = "TRANSACT SHARES", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_transact_shares.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)

    #Creating the labels required for transacting share
    label_company = Label(frame_transact_shares, text = "Stock Company", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_selling_company = Label(frame_transact_shares, text = "Selling Company", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_buying_company = Label(frame_transact_shares, text = "Buying Company", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_shares = Label(frame_transact_shares, text = "No of Shares", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_price = Label(frame_transact_shares, text = "Price", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')

    #Creating entries required for transacting share
    combo_company = ttk.Combobox(frame_transact_shares, font = ('Comic Sans', 17), state = 'readonly')
    combo_selling_company = ttk.Combobox(frame_transact_shares, font = ('Comic Sans', 17), state = 'readonly')
    combo_buying_company = ttk.Combobox(frame_transact_shares, font = ('Comic Sans', 17), state = 'readonly')
    entry_shares = Entry(frame_transact_shares, font = ('Comic Sans', 17))
    entry_price = Entry(frame_transact_shares, font = ('Comic Sans', 17))

    #Setting the values for the combobox
    combo_company['values'] = tuple(globe.companies.keys())
    combo_selling_company['values'] = tuple(globe.companies.keys())
    combo_buying_company['values'] = tuple(globe.companies.keys())

    #Placing all the labels above
    label_company.grid(row = 1, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_selling_company.grid(row = 2, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_buying_company.grid(row = 3, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_shares.grid(row = 4, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    label_price.grid(row = 5, column = 0, sticky = NSEW, padx = (10, 0), pady = 1, ipadx = 5, ipady = 5)
    
    #Placing all the entries above
    combo_company.grid(row = 1, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    combo_selling_company.grid(row = 2, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    combo_buying_company.grid(row = 3, column = 1, sticky = NSEW,padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_shares.grid(row = 4, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    entry_price.grid(row = 5, column = 1, sticky = NSEW, padx = (0, 10), pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the reset button
    button_clear_transact_shares = CustomButton(frame_transact_shares, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_transact_shares)
    button_clear_transact_shares.grid(row = 6, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)

    #Creating the update button
    button_transact_shares = CustomButton(frame_transact_shares, text = "UPDATE", bg = constant.PRIMARYCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = transact_shares)
    button_transact_shares.grid(row = 6, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)

    
    #Creating the pr crisis frame
    frame_pr_crisis = Frame(frame_minor_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_pr_crisis.grid(row = 0, column = 2, sticky = 'new', padx = 5, pady = 5)
    
    #Gridding frame_pr_crisis
    frame_pr_crisis.grid_columnconfigure((0,1), weight = 1)
    
    #Creating the label to tell them what is the task is
    label_pr_crisis =Label(frame_pr_crisis, text = "PR CRISIS", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_pr_crisis.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)

    #Creating the entries to receive the pr crisis of the affected company
    combo_affected_company = ttk.Combobox(frame_pr_crisis, font = ('Comic Sans', 17), state = 'readonly')
    combo_pr_crisis = ttk.Combobox(frame_pr_crisis, font = ('Comic Sans', 17), state = 'readonly')

    #Setting the values for the comboboxes
    combo_affected_company['values'] = tuple(globe.companies.keys())
    combo_pr_crisis['values'] = tuple(range(0, 11))

    #Placing the entries
    combo_affected_company.grid(row = 1, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    combo_pr_crisis.grid(row = 2, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the reset button
    button_clear_pr_crisis = CustomButton(frame_pr_crisis, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_pr_crisis)
    button_clear_pr_crisis.grid(row = 3, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)
    
    #Creating and placing the update button for pr crisis
    button_pr_crisis = CustomButton(frame_pr_crisis, text = "UPDATE", bg = constant.PRIMARYCLR, fg = "white", font = ('Comic Sans', 17, 'bold'),  command = update_pr_crisis)
    button_pr_crisis.grid(row = 3, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)


    #Creating the pr response frame
    frame_pr_response = Frame(frame_minor_action, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_pr_response.grid(row = 0, column = 3, sticky = 'new', padx = 5, pady = 5)
    
    #Gridding frame_pr_response
    frame_pr_response.grid_columnconfigure((0,1), weight = 1)
    
    #Creating the label to tell them what is the task is
    label_pr_response =Label(frame_pr_response, text = "PR RESPONSE", font = ('Comic Sans', 17, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_pr_response.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)

    #Creating the entries for receiving the pr response values
    combo_recovered_company = ttk.Combobox(frame_pr_response, font = ('Comic Sans', 17), state = 'readonly')
    combo_pr_response = ttk.Combobox(frame_pr_response, font = ('Comic Sans', 17), state = 'readonly')

    #Setting the values for the comboboxes
    combo_recovered_company['values'] = tuple(globe.companies.keys())
    combo_pr_response['values'] = tuple(range(0, 11))

    #Placing the above entries
    combo_recovered_company.grid(row = 1, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    combo_pr_response.grid(row = 2, column = 0, columnspan = 2, sticky = NSEW, padx = 10, pady = 1, ipadx = 5, ipady = 5)
    
    #Creating the reset button
    button_clear_pr_response = CustomButton(frame_pr_response, text = "CLEAR", bg = constant.CLEARCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = clear_pr_response)
    button_clear_pr_response.grid(row = 3, column = 0, sticky = NSEW, padx = (10,0), pady = 1, ipadx = 5, ipady = 5)
    
    #Creating and placing the update button for pr response
    button_pr_response = CustomButton(frame_pr_response, text = "UPDATE", bg = constant.PRIMARYCLR, fg = "white", font = ('Comic Sans', 17, 'bold'), command = update_pr_response)
    button_pr_response.grid(row = 3, column = 1, sticky = NSEW, padx = (0,10), pady = 1, ipadx = 5, ipady = 5)

    
    #Adding all the theme based frames to tuple_theme_frames
    tuple_theme_frames += (frame_minor_action, frame_transact_shares, frame_pr_crisis, frame_pr_response)

    #Adding all the theme based labels to tuple_theme_labels
    tuple_theme_labels += (label_major_action, label_company, label_selling_company, label_buying_company, label_shares, label_price, label_transact_shares, label_pr_crisis, label_pr_response, label_tab_action)

    #Managing focus
    frame_minor_action.bind("<Button-1>", lambda e: frame_minor_action.focus_set())
    frame_transact_shares.bind("<Button-1>", lambda e: frame_transact_shares.focus_set())
    frame_pr_crisis.bind("<Button-1>", lambda e: frame_pr_crisis.focus_set())
    frame_pr_response.bind("<Button-1>", lambda e: frame_pr_response.focus_set())
    

    label_transact_shares.bind("<Button-1>", lambda e: label_transact_shares.focus_set())
    label_company.bind("<Button-1>", lambda e: label_company.focus_set())
    label_selling_company.bind("<Button-1>", lambda e: label_selling_company.focus_set())
    label_buying_company.bind("<Button-1>", lambda e: label_buying_company.focus_set())
    label_shares.bind("<Button-1>", lambda e: label_shares.focus_set())
    label_price.bind("<Button-1>", lambda e: label_price.focus_set())

    label_pr_crisis.bind("<Button-1>", lambda e: label_pr_crisis.focus_set())
    label_pr_response.bind("<Button-1>", lambda e: label_pr_response.focus_set())

    return frame_minor_action
 
    
def dump_config_file():
    global tab_fields, manager_entry, world_name
    try:
        world_title = manager_entry.get(('title', 'theme'))
        tab_names  = ','.join(tuple(tab_fields.keys()))
        
        lst_tab_fields = []
        for tup in tab_fields.values():
            x = ','.join(tup) + "\n"
            lst_tab_fields.append(x)
        
        #Removing the \n at the end of the last line
        lst_tab_fields[-1] = lst_tab_fields[-1].strip()
    except Exception as error:
        print(error)
        
    folder = f'World {world_name}'
    x = f'./{folder}/config.txt'
    
    file = open(x, "w")
    file.write(f'{world_title}\n')
    file.write(f'{tab_names}\n')
    file.writelines(lst_tab_fields)
    file.close()
    

def display_error(error):
    global label_message, active_messages, theme
    
    if theme == 'light':
        label_message.config(fg = constant.ERRORDARKFGCLR)
    else:
        label_message.config(fg = constant.ERRORLIGHTFGCLR)
        
    label_message.config(text = error)
  
    active_messages.append(('error', error))

    root.after(5000, clear_message)


def display_update(update):
    global label_message, active_messages, theme

    if theme == 'light':
        label_message.config(fg = constant.UPDATEDARKFGCLR)
    else:
        label_message.config(fg = constant.UPDATELIGHTFGCLR)
 
    label_message.config(text = update)
    
    active_messages.append(('update', update))
    
    root.after(10000, clear_message)
    

def mod(x): 
    return str(x).replace("/","{slash}").replace("-", "{hyphen}")


def unmod(x):
    return str(x).replace("{slash}", "/").replace("{hyphen}", "-")
    
    
def configure_world(fen_actions):
    global globe
    
    #Resetting globe
    globe.reset()

    for fen_action in fen_actions:
        x = fen_action.split('-')
        if x[0] == 'inv':
            continue
        elif x[0] == 'cc': #create company
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            owners = x[2].replace('{hyphen}', '-').replace('{slash}', '/')
            location = x[3].replace('{hyphen}', '-').replace('{slash}', '/')
            capital = float(x[4])
            stock_price = float(x[5])
            shares = int(x[6])
            
            globe.open_company(name, owners, location, capital, stock_price, shares)
        elif x[0] == 'dc': #delete company
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            globe.close_company(name)
        elif x[0] == 'ts': #transact shares
            stock_company_name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            selling_company_name = x[2].replace('{hyphen}', '-').replace('{slash}', '/')
            buying_company_name = x[3].replace('{hyphen}', '-').replace('{slash}', '/')
            
            shares = int(x[4])
            price = float(x[5])
            globe.transact_shares(stock_company_name, selling_company_name, buying_company_name, shares, price)
        elif x[0] == 'prc': #pr crisis
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            pr_crisis = int(x[2])
            globe.release_pr_crisis(name, pr_crisis)
        elif x[0] == 'prr': #pr response
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            pr_response = int(x[2])
            globe.release_pr_response(name, pr_response)
        elif x[0] == 'chgname': #change name
            old_name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            new_name = x[2].replace('{hyphen}', '-').replace('{slash}', '/')
            globe.rename(old_name, new_name)
        elif x[0] == 'chgowners': #change owners
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            owners = x[3].replace('{hyphen}', '-').replace('{slash}', '/')
            globe.set_owners(name, owners)
        elif x[0] == 'chglocation': #change location
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            location = x[3].replace('{hyphen}', '-').replace('{slash}', '/')
            globe.set_location(name, location)
        elif x[0] == 'chgcapital': #change capital
            name = x[1].replace('{hyphen}', '-').replace('{slash}', '/')
            capital = float(x[3])
            globe.set_capital(name, capital)
        elif x[0] == 'chgstock': #change stock price
            name = x[1]
            stock_price = float(x[3])
            globe.set_stock(name, stock_price)
        else:
            raise ValueError(f'Invalid Operation: {x[0]}')
            

def refresh():
    global globe, tab_frames, tab_fields, tuple_theme_frames, active_tab
    
    tuple_theme_frames = list(tuple_theme_frames)
    for frame in tab_frames.values():
        try:
            tuple_theme_frames.remove(frame)
        except Exception:
            pass
            
    tuple_theme_frames = tuple(tuple_theme_frames)
    
    #Destroying the old one and Creating the audit log tab frame
    tab_frames['audit log'].destroy()
    tab_frames['audit log'] = create_audit_log_tab()
    
    #Destroying the old one and Creating the investors tab frame
    tab_frames['investors'].destroy()
    tab_frames['investors'] = create_investors_tab()
    
    count = 2
    for tab_name in tab_fields:
        tab_frames[tab_name].destroy()
        fields = tab_fields[tab_name]
        tab_frames[tab_name] = create_tab(tab_name, fields)
        count+=1
       
    
    for frame in tab_frames:
        tuple_theme_frames += (frame,)
    
    #Switching to the active tab
    switch_tab(active_tab)
    
    #Updating all the company combo boxes
    update_combo_companies()
    
    #Scrolling the audit log tab to the bottom
    tab_frames['audit log'].canvas.update_idletasks()
    tab_frames['audit log'].canvas.yview_moveto('1.0')
    tab_frames['audit log'].canvas.update_idletasks()


def revert(num): #num - whole number
    global log_file_name
    
    response = messagebox.askokcancel('Revert back', 'Are you sure?')
    if response != 1:
        return
        
    file = open(log_file_name, 'r')
    fen_actions = file.read().strip('/\t\r\n ').split('/')
    file.close()
    
    updated_fen_actions = fen_actions[:num+1]
    
    file = open(log_file_name, 'w')
    file.write('/'.join(updated_fen_actions))
    file.close()
    
    post_log_on_discord()
    
    configure_world(updated_fen_actions)
    refresh()
    
    
def clear_message():
    global label_message, active_messages
    active_messages.pop(0)
    if not active_messages: #Checks if active_messages is empty. If not empty, label_message is not cleared.
        label_message.config(text = '')
            

def post_log_on_discord():
    global log_file_name, log_webhook
    
    if log_webhook.strip() != '':        
        file = open(log_file_name, 'r')
        x = file.read()
        file.close()
        try:
            post(log_webhook, data = {"content": f"```{x}```"})
        except Exception as error:
            print(error)
    
    
def post_msg_on_discord(message):
    global msg_webhook

    if msg_webhook.strip() != '':
        try:
            post(msg_webhook, data = {"content": message, 'tts': False})
        except Exception as error:
            print(error)
            
 
def main():
    global theme, theme_bg, theme_fg, root, frame_top, frame_home, label_message, manager_entry, combo_open_world, entry_create_world, tuple_theme_frames, tuple_theme_labels, available_worlds, entry_msg_webhook, entry_log_webhook, active_messages
    
    #Default theme is Light theme
    theme = "dark"
    theme_bg = constant.DARKBGCLR
    theme_fg = constant.DARKBGTEXTCLR

    #Creating the root window
    root = Tk()
    root.title('Stock and Key')
    
    #Setting the bg colour of root to theme_bg
    root.config(bg = theme_bg)   
    
    #Gridding root
    root.grid_columnconfigure(0, weight = 1)
    root.grid_rowconfigure((2,3,4), weight = 1)
    
    #Setting the min size of root
    root.minsize(1590, 990)
    
    #Adjusting the resolution
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

    #Creating the entry manager
    manager_entry = EntryManager()

    #Changing the default font of combobox drop downs. This font size looks good only on the home page. It will be changed later for the other pages.
    font_combo_listbox = font.Font(family="Comic Sans", size = 23, weight = "normal")
    root.option_add("*TCombobox*Listbox*Font", font_combo_listbox)

    #Changing the default font of the menu pop ups
    font_menu = font.Font(family="Comic Sans", size=15, weight = "normal")
    root.option_add("*Menu*Font", font_menu)

    #Initialising tuple_theme_frames and tuple_theme_labels
    tuple_theme_frames = ()
    tuple_theme_labels = ()
   
    #Creating and placing a frame for the title and switch_theme button
    frame_top = Frame(root, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_top.grid(row = 0, column = 0, sticky = 'new', padx = 5, pady = 10)
    tuple_theme_frames += (frame_top,)

    #Gridding frame_top
    frame_top.grid_columnconfigure(0, weight = 1)

    #Title of the application
    def func(*args, **kwargs):
        pass
        
    tagentry_title = manager_entry.create_entry(frame_top, ('title', 'theme'), 'Innowaves: Stock and Key', func, default_row = 0, default_column = 0, font = ('Comic Sans', 25, 'bold', 'underline'), bd = 0, justify = CENTER, bg = theme_bg, fg = theme_fg)
    tagentry_title.grid(row = 0, column = 0, columnspan = 2, sticky = 'new', ipadx = 5, ipady = 5, padx = 5)

    #Creating and Placing the switch_theme button
    button_switch_theme = CustomButton(frame_top, text = "TOGGLE THEME", font = ("Comic Sans", 17, 'bold'), bg = constant.SECONDARYCLR, fg = "white", command = switch_theme)
    button_switch_theme.grid(row = 0, column = 1, sticky = E, ipadx = 5, ipady = 5, padx = 5)

    #Having a label message at the bottom to display messages to the user
    label_message = Label(root, font = ('Comic Sans', 17, 'bold'), bg = theme_bg, highlightthickness = 0)
    label_message.grid(row = 4, column = 0, sticky = 'sew', padx = 5, pady = 5, ipadx = 5, ipady = 5)
    
    #Initialising active_messages
    active_messages = []
  
    #Getting the world code from the user or enabling them to create a new world
    root.grid_rowconfigure(1, weight = 1)

    #Creating frame_home to contain the contents for accepting the world code or creating a new world    
    frame_home = Frame(root, bd = 0, highlightthickness = 0, bg = theme_bg)
    frame_home.grid(row = 1, column = 0, sticky = NSEW, padx = 5, pady = 30)
    tuple_theme_frames += (frame_home, )

    #Gridding frame_home
    frame_home.grid_columnconfigure((0,1), weight = 1)

    #Creating the label to explain what is a world
    label_world_explanation = Label(frame_home, text = constant.WORLDEXPLANATION, font = ('Comic Sans', 24, 'bold'), bg = theme_bg, fg = theme_fg, bd = 5, relief = 'ridge')
    label_world_explanation.grid(row = 0, column = 0, columnspan = 2, ipadx = 40, ipady = 40, padx = 5, pady = 20)
    tuple_theme_labels += (label_world_explanation, )
    
    #Creating the frame, label and entry to get the discord web hook from the user to send messages in the required channel and log in the desired channel
    frame_webhook = Frame(frame_home, bg = theme_bg, bd = 0, highlightthickness = 0)
    frame_webhook.grid(row = 2, column = 0, columnspan = 2, sticky = NSEW, padx = 20, pady = 20)
    
    label_msg_webhook = Label(frame_webhook, text = "Discord Webhook for transactions (Optional)", font = ('Comic Sans', 20, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_msg_webhook.pack(fill = X, ipadx = 5, ipady = 5, padx = 40)
    
    entry_msg_webhook = Entry(frame_webhook, font = ('Comic Sans', 20, 'underline'), fg = constant.LINKCLR)
    entry_msg_webhook.pack(fill = X, ipadx = 5, ipady = 5, padx = 40, pady = (0,25))
    
    label_log_webhook = Label(frame_webhook, text = "Discord Webhook for log updates (Optional)", font = ('Comic Sans', 20, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = 'ridge')
    label_log_webhook.pack(fill = X, ipadx = 5, ipady = 5, padx = 40, pady = (25,0))
    
    entry_log_webhook = Entry(frame_webhook, font = ('Comic Sans', 20, 'underline'), fg = constant.LINKCLR)
    entry_log_webhook.pack(fill = X, ipadx = 5, ipady = 5, padx = 40)
    
    #Updating tuple_theme_frames and tuple_theme_labels
    tuple_theme_frames += (frame_webhook, )
    tuple_theme_labels += (label_msg_webhook, label_log_webhook)
    
    #Creating frame_open_world and frame_create_world
    frame_open_world = Frame(frame_home, bg = theme_bg, highlightthickness = 0, bd = 0)
    frame_create_world = Frame(frame_home, bg = theme_bg, highlightthickness = 0, bd = 0)
    tuple_theme_frames += (frame_open_world, frame_create_world)

    #Gridding frame_open_world and frame_create_world
    frame_open_world.grid_columnconfigure((0,1), weight = 1)
    frame_create_world.grid_columnconfigure((0,1), weight = 1)

    #Placing frame_open_world and frame_create_world
    frame_open_world.grid(row = 1, column = 0 , padx = 10, pady = 50)
    frame_create_world.grid(row = 1, column = 1 , padx = 10, pady = 50)

    def onCreateWorldClick():
        global entry_create_world, entry_msg_webhook, entry_log_webhook, msg_webhook, log_webhook
        _world_name = entry_create_world.get().strip()
        msg_webhook = entry_msg_webhook.get().strip()
        log_webhook = entry_log_webhook.get().strip()
        if not _world_name or ',' in _world_name:
            display_error("Enter World Name [commas not allowed]")
            return
        elif _world_name.lower() in tuple(i.lower() for i in available_worlds):
            display_error("World name taken. Think of a new one!")
            return
        
        create_world(_world_name)
       

    def onOpenWorldClick():
        global combo_open_world, entry_msg_webhook, entry_log_webhook, msg_webhook, log_webhook
        _world_name = combo_open_world.get()
        msg_webhook = entry_msg_webhook.get().strip()
        log_webhook = entry_log_webhook.get().strip()
        
        if _world_name:
            open_world(_world_name)
        else:
            display_error("Select World")


    #Adding the contents to frame_create_world
    label_create_world = Label(frame_create_world, text = "CREATE WORLD", font = ('Comic Sans', 23, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_create_world.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    label_world_name = Label(frame_create_world, text = "World Name", font = ('Comic Sans', 23, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge" )
    label_world_name.grid(row = 1, column = 0, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    tuple_theme_labels += (label_create_world, label_world_name)

    entry_create_world = Entry(frame_create_world, font = ('Comic Sans', 23))
    entry_create_world.grid(row = 1, column = 1, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    button_create_world = CustomButton(frame_create_world, text = "SUBMIT", bg = constant.PRIMARYCLR, fg = "white", font = ('Comic Sans', 23, 'bold'), command = onCreateWorldClick)
    button_create_world.grid(row = 2, column = 0, columnspan = 2, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    
    #Adding the contents to frame_open_world
    label_open_world = Label(frame_open_world, text = "OPEN WORLD", font = ('Comic Sans', 23, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge")
    label_open_world.grid(row = 0, column = 0, columnspan = 2, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    label_world_name = Label(frame_open_world, text = "World Name", font = ('Comic Sans', 23, 'bold'), bg = theme_bg, fg = theme_fg, bd = 1, relief = "ridge" )
    label_world_name.grid(row = 1, column = 0, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    tuple_theme_labels += (label_open_world, label_world_name)

    folders = []
    for (dirpath, dirnames, filenames) in os.walk('.'):
        folders.extend(dirnames)
        break

    available_worlds = []
    for folder in folders:
        if folder == "__pycache__":
            continue
        available_worlds.append(folder.lstrip('wWorld').strip())


    combo_open_world = ttk.Combobox(frame_open_world, font = ('Comic Sans', 23), state = 'readonly')
    combo_open_world['values'] = available_worlds
    combo_open_world.grid(row = 1, column = 1, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    button_open_world = CustomButton(frame_open_world, text = "SUBMIT", bg = constant.PRIMARYCLR, fg = "white", font = ('Comic Sans', 23, 'bold'), command = onOpenWorldClick)
    button_open_world.grid(row = 2, column = 0, columnspan = 2, sticky = NSEW, pady = 1, ipadx = 5, ipady = 5)

    #Managing focus
    frame_home.bind("<Button-1>", lambda e: frame_home.focus_set())
    frame_create_world.bind("<Button-1>", lambda e: frame_create_world.focus_set())
    frame_open_world.bind("<Button-1>", lambda e: frame_open_world.focus_set())
    frame_top.bind("<Button-1>", lambda e: frame_top.focus_set())
    frame_webhook.bind("<Button-1>", lambda e: frame_webhook.focus_set())
    label_world_explanation.bind("<Button-1>", lambda e: label_world_explanation.focus_set())
    label_message.bind("<Button-1>", lambda e: label_message.focus_set())
    
   
    #Keeping the root window open
    root.mainloop()
