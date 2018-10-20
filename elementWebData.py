"""
  ======================================================================================================
  These functions create and control all the data for the elements of the web 
  and their relationships to each other.
  ======================================================================================================
"""

import json

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
	
#    if (self.type == 'player' or self.type == 'npc'):
#     self.allies = dict["ally_ids"]
#      self.enemies = dict["enemy_ids"]
	
  def resynchronize(self):
    self.type = self.element_dict["type"]
    self.name = self.element_dict["name"]
    self.notes = self.element_dict["notes"]    

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
    # Add a try/catch here to account for corrupted save files?
    # Load the selected file:
    with open(self.file_path, 'r') as r:
      for i, line in enumerate(r):
        # The first line of the save file should contain meta data needed to set up the web UI.
        if i == 0:
          self.meta_data = json.loads(line)
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
	  
  # This method adds a new element to the web:
  def addElement(self, data_dict):
    data_dict["id"] = self.next_id
    new_element = elementData(data_dict)
    self.elements["e" + str(data_dict["id"])] = new_element
    self.web_data_list.append(data_dict)
    self.next_id += 1
	
  # This method saves the web's list of meta data and dictionaries to the selected file.
  def save(self):
    with open(self.file_path, 'w') as w:
      w.write(json.dumps(self.meta_data) + '\r')
    with open(self.file_path, 'a') as a:
      for i in self.web_data_list:
        a.write(json.dumps(i) + '\r')
  

