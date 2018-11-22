"""
  ======================================================================================================
  These functions create and control all the data for the elements of the web 
  and their relationships to each other.
  ======================================================================================================
"""

import json
import re

"""
The elementData object is the basic building block of the entire web.
"""
class elementData:
  def __init__(self, dict):
    self.element_dict = dict
    self.id = dict["id"]
    self.element_key = "e" + str(self.id)
    self.type = self.element_dict["type"]
    self.name = self.element_dict["name"]
    self.notes = self.element_dict["notes"]
    
    # Make sure the element_dict has a "parents" list and add one if it doesn't:
    try:
      self.parents = self.element_dict["parents"]
    except KeyError:
      self.element_dict["parents"] = []
      self.parents = self.element_dict["parents"]

    # Make sure the element_dict has a "children" list and add one if it doesn't:
    try:
      self.children = self.element_dict["children"]
    except KeyError:
      self.element_dict["children"] = []
      self.children = self.element_dict["children"]
	
    if self.type == 'NPC':
      try:
        self.rank = self.element_dict["rank"]
      except KeyError:
        self.element_dict["rank"] = 'None'
        self.rank = self.element_dict["rank"]
	  
    # Only NPCs, Factions, and Parties have stats:
    if (self.type == 'NPC' or self.type == 'Faction' or self.type == 'Party'):
      try:
        self.stats = self.element_dict["stats"]
      except KeyError:
        if self.type == 'NPC':
          self.element_dict["stats"] = {"Charisma": -1, "Intellect": -1, "Reputation": -1}
        else:
          self.element_dict["stats"] = {"Clout": -1}
        self.stats = self.element_dict["stats"]
	
    # Only Factions and Parties have causes:
    if (self.type == 'Faction' or self.type == 'Party'):
      self.cause = self.element_dict["cause"]

    # For Player and NPC elements, set up allies and enemies attributes:
    if (self.type == 'Player' or self.type == 'NPC'):
      # Make sure the element_dict has an "allies" list and add one if it doesn't:
      try:
        self.allies = self.element_dict["allies"]
      except KeyError:
        self.element_dict["allies"] = []
        self.allies = self.element_dict["allies"]

      # Make sure the element_dict has an "enemies" list and add one if it doesn't:
      try:
        self.enemies = self.element_dict["enemies"]
      except KeyError:
        self.element_dict["enemies"] = []
        self.enemies = self.element_dict["enemies"]

    # For Player elements, set up agenda, objectives, support, and promises attribute:
    if self.type == 'Player':
      try:
        self.agenda = self.element_dict["agenda"]
      except KeyError:
        self.element_dict["agenda"] = {"ambition": '', 
                                       "opposition": '', 
									   "scope": ''}
        self.agenda = self.element_dict["agenda"]
		
      try:
        self.objectives = self.element_dict["objectives"]
      except KeyError:
        self.element_dict["objectives"] = {}
        self.objectives = self.element_dict["objectives"]	

      try:
        self.support = self.element_dict["support"]
      except KeyError:
        self.element_dict["support"] = {}
        self.support = self.element_dict["support"]	
		
      try:
        self.promises = self.element_dict["promises"]
      except KeyError:
        self.element_dict["promises"] = {"prom_1": {"promise": '', "promised_to": ''},
                                         "prom_2": {"promise": '', "promised_to": ''},
                                         "prom_3": {"promise": '', "promised_to": ''},
                                         "prom_4": {"promise": '', "promised_to": ''},
                                         "prom_5": {"promise": '', "promised_to": ''}
                                         }
        self.promises = self.element_dict["promises"]
  
  # Resets all attributes according to the rules in __init__. This allows types to be changed:
  def resynchronize(self):
    self.__init__(self.element_dict)
    
"""
The webData object essentially acts a database of elementData objects.
"""
class webData:
  def __init__(self):
    self.file_path = 'web.json' # This could be user selected someday?
    self.web_data_list = []
    self.meta_data = None
    self.id_list = []
    self.elements = {}
    self.next_id = -1
    self.id_history = []
    self.type_colors = {}
    self.type_colors_kivy = {}
    # Add a try/catch here to account for corrupted save files?
    # Load the selected file:
    with open(self.file_path, 'r') as r:
      for i, line in enumerate(r):
        # The first line of the save file should contain meta data needed to set up the web UI.
        if i == 0:
          self.meta_data = json.loads(line)
          self.id_history = self.meta_data["id_history"]
        # The remaining lines should contain data for each element in the web.
        else:
          temp_dict = json.loads(line)
          self.web_data_list.append(temp_dict)
		  
    # Populate the id_list with each id from the loaded dictionaries, and create 
	# an elementData object for each id:
    for i in self.web_data_list:
      id = i["id"]
      self.id_list.append(id)
      self.elements["e" + str(id)] = elementData(i)
 
	  
    # Sets up the web's next_id upon initialization:
    for i in self.id_list:
      if i > self.next_id:
        self.next_id = i
    self.next_id += 1
	
    # Sets up the web's type_colors meta_data for use by kivy:
    self.type_colors = self.meta_data["type_colors"]
    for key in self.type_colors:
      self.type_colors_kivy[key] = []
      for i in self.type_colors[key]:
        self.type_colors_kivy[key].append(i / 255)
      self.type_colors_kivy[key].append(1)
	  
  # This method adds a new element to the web:
  def addElement(self, data_dict):
    data_dict["id"] = self.next_id
    new_element = elementData(data_dict)
    self.elements["e" + str(data_dict["id"])] = new_element
    self.web_data_list.append(data_dict)
    self.next_id += 1
    return data_dict["id"]
	
  # This method searches the names of elements and returns a dictionary with matches:
  def search(self, search_str, filter=None):
    results = {}
    if search_str == '' and (filter == 'allow:all' or filter == 'allow:bank'):
      pass
    elif search_str == '':
      return results
    
    for element in self.elements:
      if self.elements[element].type.lower() == 'bank':
        if filter == 'allow:bank':
          results[self.elements[element].name] = element
        else:
          continue
      if search_str.lower()[0:6:] == 'type: ':
        check = re.search(search_str.lower()[6::], self.elements[element].type.lower())
      elif search_str.lower()[0:6:] == 'rank: ':
        try:
          check = re.search(search_str.lower()[6::], self.elements[element].rank.lower())
        except AttributeError:
          continue
      else:
        check = re.search(search_str.lower(), self.elements[element].name.lower())
      filter_passed = False
      if filter == 'type:char':
        if (self.elements[element].type == 'NPC' or self.elements[element].type == 'Player'):
          filter_passed = True
      elif (filter == None or filter == '' or filter == 'allow:all'):
        filter_passed = True
      if (check and filter_passed):
        results[self.elements[element].name] = element
    return results
	
  # This method saves the web's list of meta data and dictionaries to the selected file.
  def save(self):
    with open(self.file_path, 'w') as w:
      w.write(json.dumps(self.meta_data) + '\r')
    with open(self.file_path, 'a') as a:
      for i in self.web_data_list:
        a.write(json.dumps(i) + '\r')
  

