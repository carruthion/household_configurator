#!/usr/bin/python3  

from tkinter import *
from tkinter import ttk
from tkinter import filedialog 
from tkinter import messagebox
import csv
import random
import json
import os

#--------------------------------------------------------------
# Settings:
#--------------------------------------------------------------
hh_types = [
    "00: Single, Vollzeit",
    "01: Single, Arbeitslos",
    "02: Single, Teilzeit",
    "03: Paar, 2x Vollzeit",
    "04: Paar, 1x Vollzeit, 1x Teilzeit",
    "05: Paar, 1x Vollzeit, 1x Arbeitslos",
    "06: Familie, 2x Vollzeit, 1-4 Kinder",
    "07: Familie, 1x Vollzeit, 1x Teilzeit, 1-4 Kinder",
    "08: Familie, 1x Vollzeit, 1x Arbeitslos, 1-4 Kinder",
    "09: Alleinerziehend, Vollzeit, 1-4 Kinder",
    "10: Alleinerziehend, Teilzeit, 1-4 Kinder",
    "11: Alleinerziehend, Arbeitslos, 1-4 Kinder",
    "12: Renter Paar",
    "13: Rentner Single"
]

ev_types = []
ev_ids = []

# Load ev types
def load_ev_types():
    ev_file = "ev-data.json"
    if not os.path.exists(ev_file):
        import urllib.request
        url = "https://github.com/chargeprice/open-ev-data/blob/3134cae485555ac288d01ba9b13573047bf92937/data/ev-data.json?raw=true"
        try:
            urllib.request.urlretrieve(url, ev_file)
        except Exception as e:
            messagebox.showerror("Fehler", f"EV-Daten konnten nicht geladen werden:\n{e}")
            return
    with open(ev_file, "r") as f:
        ev_data = json.load(f)
        for ev in ev_data["data"]:
            ev_types.append(str(ev["brand"] + " " + ev["model"] + " " + ev["variant"]))
            ev_ids.append(ev["id"])

load_ev_types()

heat_types = [
    "00: Konventionell",
    "01: Kombiniert",
    "02: Wärmepumpe"
]

#--------------------------------------------------------------
# KI-Grid Config:
#--------------------------------------------------------------
global_hh_config_list = []
global_h_id_list = [0]

def get_next_id():
    global global_h_id_list
    max_id = max(global_h_id_list) + 1
    global_h_id_list.append(max_id)
    return max_id

class hh_config:
    def __init__(self, config_line=None):
        self.h_type = 0                     # Single, retired, family, ...
        self.h_id = 0                       # individual ID, integer
        self.consumption_yearly = 0         # Wh

        self.pv_area = 0                    # square meter, 0: Has no pv
        self.pv_efficiency = 20             # % (Wirkungsgrad)
        self.pv_azimuth = 180               # degrees, 90: east, 180: south, 270: west
        self.pv_elevation = 35              # degrees, 0 is horizontal to earth surface

        self.ev_type = 0                    # 0: No ev; 1: Ev model 1; ...
        self.length_commute = 0             # way to work in km

        self.battery_storage = 0            # Wh
        self.battery_charge_power = 0       # W
        self.battery_discharge_power = 0    # W

        self.heating_type = 0               # 0: Conventional; 1: Combined Heat Power; 2: Heat pump

        if config_line:
            self.set_config_by_line(config_line)
        
        if self.h_id in global_h_id_list:
            print("ID was already used, generating new one...")
            self.h_id = get_next_id()
        else:
            global_h_id_list.append(self.h_id)
    
    def set_config_by_line(self, line):
        conf_list = line.split(",")
        i = 0
        try:
            self.h_type = int(conf_list[i]); i += 1
            self.h_id = int(conf_list[i]); i += 1
            self.consumption_yearly = int(conf_list[i]); i += 1

            self.pv_area = int(conf_list[i]); i += 1
            self.pv_efficiency = int(conf_list[i]); i += 1
            self.pv_azimuth = int(conf_list[i]); i += 1
            self.pv_elevation = int(conf_list[i]); i += 1
            
            self.ev_type = str(conf_list[i]); i += 1
            self.length_commute = int(conf_list[i]); i += 1

            self.battery_storage = int(conf_list[i]); i += 1
            self.battery_charge_power = int(conf_list[i]); i += 1
            self.battery_discharge_power = int(conf_list[i]); i += 1

            self.heating_type = int(conf_list[i]); i += 1

        except:
            print("Wrong household config format")
            exit()
    
    def to_string(self):
        return (f"{self.h_type},{self.h_id},{self.consumption_yearly},"
                f"{self.pv_area},{self.pv_efficiency},{self.pv_azimuth},"
                f"{self.pv_elevation},{self.ev_type},{self.length_commute},"
                f"{self.battery_storage},{self.battery_charge_power},"
                f"{self.battery_discharge_power},{self.heating_type}")

def load_household_config(config_file_name):
    household_config_list = []    
    try:
        file = open(config_file_name, 'r')
        lines = file.readlines()
        file.close()
    except:
        return []
    for line in lines[1:]:
        household_config_list.append(hh_config(line))
    return household_config_list

def hh_list_to_string(hh_list):
    out = ("h_type,h_id,consumption_yearly,pv_area,pv_efficiency,pv_azimuth,"
           "pv_elevation,ev_type,length_commute,battery_storage,battery_charge_power,"
           "battery_discharge_power,heating_type\n")
    for hh in hh_list:
        out += hh.to_string() + "\n"
    return out

#--------------------------------------------------------------
# GUI:
#--------------------------------------------------------------
act_row = 0

save_file_name = "./households.csv"

def set_text(e, text):
    e.delete(0, END)
    e.insert(0, text)

def make_frame_row(on_frame, label_name, unit_name, description, default_text=""):
    global act_row
    my_label = Label(on_frame, text=label_name)
    my_label.grid(column=0, row=act_row, sticky="w")
    my_entry = Entry(on_frame, width=10)
    set_text(my_entry, default_text)
    my_entry.grid(column=1, row=act_row, sticky="e")
    my_unit_label = Label(on_frame, text=unit_name)
    my_unit_label.grid(column=2, row=act_row, sticky="w")
    my_text_label = Label(on_frame, text=description)
    my_text_label.grid(column=3, row=act_row, sticky="w", padx=(3,0))
    act_row += 1
    return my_entry

def make_section(on_root, section_name):
    global act_row
    s = ttk.Separator(on_root, orient=HORIZONTAL)
    s.grid(column=0, row=act_row, sticky="ew", columnspan=4, pady=(3, 10))
    act_row += 1
    my_label = Label(on_root, text=section_name, font="TkHeadingFont")
    my_label.grid(column=0, row=act_row, pady=(0, 3), sticky="w")
    act_row += 1

def load_config_file():
    global global_hh_config_list, save_file_name
    global_hh_config_list += load_household_config(save_file_name)
    update_num_hh()

def save_config_file():
    global global_hh_config_list, save_file_name
    save_str = hh_list_to_string(global_hh_config_list)
    try:
        file = open(save_file_entry.get(), 'w')
        file.write(save_str)
        file.close()
    except:
        messagebox.showerror("Fehler", "Konnte nicht gespeichert werden.")    

# Main window
root = Tk()
root.title("KI-Grid Haushaltskonfigurator")

# Header
header_frame = Frame(root)
header_frame.grid(column=0, row=act_row, sticky="w", padx=10, pady=(10, 3))
act_row += 1

header_label = Label(header_frame, text="KI-Grid Haushaltskonfigurator", font="TkCaptionFont")
header_label.grid(column=0, row=0)

# General settings frame
hh_settings_frame = Frame(root)
hh_settings_frame.grid(column=0, row=act_row, sticky="w", padx=10, pady=(10, 10))
act_row += 1

make_section(hh_settings_frame, "Allgemeine Einstellungen")

hh_type_label = Label(hh_settings_frame, text="Haushaltstyp: ")
hh_type_label.grid(column=0, row=act_row, sticky="w")
hh_type_combobox = ttk.Combobox(hh_settings_frame, width=40, values=hh_types)
hh_type_combobox.current(0)
hh_type_combobox.grid(column=1, row=act_row, columnspan=3)
act_row += 1

hh_heat_label = Label(hh_settings_frame, text="Heizung: ")
hh_heat_label.grid(column=0, row=act_row, sticky="w")
hh_heat_combobox = ttk.Combobox(hh_settings_frame, width=14, values=heat_types)
hh_heat_combobox.current(0)
hh_heat_combobox.grid(column=1, row=act_row, sticky="e")
act_row += 1

hh_consumption_yearly_entry = make_frame_row(hh_settings_frame, "Jahresverbrauch:", "kWh", "Optional", "0")

# PV settings
make_section(hh_settings_frame, "PV Einstellungen")

hh_pv_area_entry = make_frame_row(hh_settings_frame, "PV-Fläche:", "m²", "0 = Keine PV-Anlage", "0")
hh_pv_efficiency_entry = make_frame_row(hh_settings_frame, "PV-Wirkungsgrad:", "%", "", "20")
hh_pv_azimuth_entry = make_frame_row(hh_settings_frame, "PV-Azimuth:", "°", "90° = Ost, 180° = Süd", "180")
hh_pv_elevation_entry = make_frame_row(hh_settings_frame, "PV-Elevationswinkel:", "°", "0° = Horizontal", "35")

# EV settings
make_section(hh_settings_frame, "EFZ Einstellungen")
hh_ev_type_label = Label(hh_settings_frame, text="EFZ Typ:")
hh_ev_type_label.grid(column=0, row=act_row, sticky="w")
hh_ev_type_combobox = ttk.Combobox(hh_settings_frame, width=40, values=ev_types)
hh_ev_type_combobox.current(0)
hh_ev_type_combobox.grid(column=1, row=act_row, sticky="e")
act_row += 1
hh_ev_length_commute = make_frame_row(hh_settings_frame, "Arbeitsweg", "km", "Optional", "0")

# Battery storage settings
make_section(hh_settings_frame, "Batteriespeicher Einstellungen")
hh_bat_cap_entry = make_frame_row(hh_settings_frame, "Kapazität:", "Wh", "0 = Kein Batteriespeicher", "0")
hh_bat_chg_entry = make_frame_row(hh_settings_frame, "Ladeleistung:", "W", "", "3700")
hh_bat_disc_entry = make_frame_row(hh_settings_frame, "Endladeleistung:", "W", "", "3700")

# Profile generation settings frame
hh_export_frame = Frame(root)
hh_export_frame.grid(column=0, row=act_row, sticky="w", padx=10, pady=(10, 10))
act_row += 1

make_section(hh_export_frame, "Speichern / Laden")
save_number_entry = make_frame_row(hh_export_frame, "Anzahl Kopien:", "", "", "1")

save_file_label = Label(hh_export_frame, text="Konfigurationsdatei:")
save_file_label.grid(column=0, row=act_row, sticky="w")
save_file_entry = Entry(hh_export_frame, width=40)
set_text(save_file_entry, "./households.csv")
save_file_entry.grid(column=1, row=act_row)
def select_file():
    global save_file_name
    save_file_name = filedialog.asksaveasfilename(initialdir="./", title="Konfiguration wählen", filetypes=(("csv files","*.csv"),("all files","*.*")))
    set_text(save_file_entry, save_file_name)
    try:
        f = open(save_file_name, "r")
        f.close()
        load_config_file()
        update_num_hh()
    except:
        pass
save_file_load_button = Button(hh_export_frame, text="Datei wählen", command=select_file)
save_file_load_button.grid(column=2, row=act_row, sticky="w")
act_row += 1

def gui_settings_to_hh():
    temp_hh = hh_config()
    try:
        temp_hh.h_type = int(hh_type_combobox.get()[0:2])
        temp_hh.consumption_yearly = int(hh_consumption_yearly_entry.get())      
        temp_hh.pv_area = int(hh_pv_area_entry.get())                   
        temp_hh.pv_efficiency = int(hh_pv_efficiency_entry.get())          
        temp_hh.pv_azimuth = int(hh_pv_azimuth_entry.get())
        temp_hh.pv_elevation = int(hh_pv_elevation_entry.get())
        temp_hh.ev_type = ev_ids[ev_types.index(hh_ev_type_combobox.get())]
        temp_hh.length_commute = int(hh_ev_length_commute.get())
        temp_hh.battery_storage = int(hh_bat_cap_entry.get())
        temp_hh.battery_charge_power = int(hh_bat_chg_entry.get())
        temp_hh.battery_discharge_power = int(hh_bat_disc_entry.get())
        temp_hh.heating_type = int(hh_heat_combobox.get()[0:2])
        return temp_hh
    except:
        messagebox.showerror("Fehler", "Ungültige Eingabe")
        return None

def clear_profiles():
    global global_hh_config_list
    global_hh_config_list = []
    update_num_hh()

Label(hh_export_frame, text="Anzahl vorhandener Profile:").grid(column=0, row=act_row, sticky="w")
num_profiles_label = Label(hh_export_frame, text=str(len(global_hh_config_list)))
num_profiles_label.grid(column=1, row=act_row, sticky="e")
Button(hh_export_frame, text="Löschen", command=clear_profiles).grid(column=2, row=act_row, sticky="w")
act_row += 1

def update_config_display():
    # Clear the Text widget and insert the updated configuration content
    config_text.delete("1.0", END)
    config_text.insert(END, hh_list_to_string(global_hh_config_list))

def update_num_hh():
    num_profiles_label["text"] = str(len(global_hh_config_list))
    update_config_display()

def button_load_click():
    load_config_file()
    update_num_hh()

def button_generate_click():
    temp_hh = gui_settings_to_hh()
    try:
        num_hh = int(save_number_entry.get())
        if temp_hh:
            for i in range(num_hh):
                global_hh_config_list.append(temp_hh)
        update_num_hh()
    except:
        messagebox.showerror("Fehler", "Anzahl Kopien muss eine Zahl sein.")

def button_save_click():
    save_config_file()

generate_button = Button(hh_export_frame, text="Profile erstellen", command=button_generate_click)
generate_button.grid(column=0, row=act_row)
shuffle_button = Button(hh_export_frame, text="Shuffle", command=lambda: random.shuffle(global_hh_config_list))
shuffle_button.grid(column=1, row=act_row)
save_button = Button(hh_export_frame, text="Datei speichern", command=button_save_click)
save_button.grid(column=2, row=act_row)

#--------------------------------------------------------------
# Display configuration content
#--------------------------------------------------------------
# Create a frame with a scrollable Text widget to show the entire config file
display_frame = Frame(root)
display_frame.grid(column=0, row=act_row+1, sticky="w", padx=10, pady=(10,10))
config_scrollbar = Scrollbar(display_frame)
config_scrollbar.pack(side=RIGHT, fill=Y)
config_text = Text(display_frame, width=80, height=10, yscrollcommand=config_scrollbar.set)
config_text.pack(side=LEFT, fill=BOTH)
config_scrollbar.config(command=config_text.yview)

#--------------------------------------------------------------
# Run:
#--------------------------------------------------------------
if __name__ == "__main__":
    root.mainloop()
