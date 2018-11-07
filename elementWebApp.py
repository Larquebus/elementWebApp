from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.properties import (ObjectProperty, StringProperty, NumericProperty, 
                            ListProperty, DictProperty, BooleanProperty)
from kivy.core.window import Window
from kivy.graphics import BorderImage
from kivy.clock import Clock

from elementWebData import *

# The core of the application. When initialized it taps into the web data file:
class AppFrame(Widget):
  web_data = ObjectProperty(webData())
  selected_element = ObjectProperty(None)
  focus_element = ObjectProperty(None)
  element_display = ObjectProperty(None)
  static_search_bar = ObjectProperty(None)
  element_details = ObjectProperty(None)
  app_float = ObjectProperty(None)
  search_res_display = ObjectProperty(None)
  
  # Updates values in the detail for the currently selected element, saves back to web:
  def updateElementDetails(self, value_to_update, new_value):
    selected_key = self.selected_element.element_key
    self.selected_element.element_dict[value_to_update] = new_value
    self.web_data.elements[selected_key].element_dict[value_to_update] = new_value
    self.web_data.elements[selected_key].resynchronize()
    self.web_data.save()

  # Updates links to the focus element and reciprocates those links, saves back to web:
  def updateElementLinks(self, link_type_to_update, id_to_link):
    element_to_update = self.focus_element
	
    # First check all link lists in the element_to_update's element_dict and look
	# for the id_to_link:
    lists_to_check = {}
    lists_to_check['parents'] = element_to_update.parents
    lists_to_check['children'] = element_to_update.children
    if (element_to_update.type == 'NPC' or element_to_update.type == 'Player'):
      lists_to_check['allies'] = element_to_update.allies
      lists_to_check['enemies'] = element_to_update.enemies
	  
    # If the id_to_link is already linked to the focus, unLink it. This solves 
	# creation of duplicate links AND makes it easy to move links from one type to 
	# another in one stroke:
    for key in lists_to_check:
      try:
        lists_to_check[key].index(id_to_link)
      except ValueError:
        continue
      else:
        self.unLink(key, id_to_link)
	
    # First update the primary element:
    try:
      element_to_update.element_dict[link_type_to_update].append(id_to_link)
    except KeyError:
      element_to_update.element_dict[link_type_to_update] = []
      element_to_update.element_dict[link_type_to_update].append(id_to_link)

    reciprocate_val_to_update = ''

    # For parent and child links we need to update the opposite value for the reciprocate:
    if link_type_to_update == 'parents':
      reciprocate_val_to_update = 'children'
    elif link_type_to_update == 'children':
      reciprocate_val_to_update = 'parents'
    else: 
      reciprocate_val_to_update = link_type_to_update

    # Next reciprocate the link between the primary and secondary element:
    reciprocate_element = self.web_data.elements['e' + str(id_to_link)]
    element_to_update_id = element_to_update.id
    try:
      reciprocate_element.element_dict[reciprocate_val_to_update].append(element_to_update_id)
    except KeyError:
      reciprocate_element.element_dict[reciprocate_val_to_update] = []
      reciprocate_element.element_dict[reciprocate_val_to_update].append(element_to_update_id)
    self.web_data.elements[reciprocate_element.element_key].resynchronize()

    self.web_data.elements[element_to_update.element_key].resynchronize()
    self.web_data.save()  
	
  # Removes a specified link type to a specified element from the focus element:
  def unLink(self, link_type_to_remove, id_to_remove):
    try:
      self.focus_element.element_dict[link_type_to_remove].remove(id_to_remove)
    except ValueError:
      print('Value is not linked to focus element.')
    else:
      self.focus_element.resynchronize()
	  
    reciprocate_type_to_remove = ''

    # For parent and child links we need to remove the id from the opposite value 
	# for the reciprocate:
    if link_type_to_remove == 'parents':
      reciprocate_val_to_remove = 'children'
    elif link_type_to_remove == 'children':
      reciprocate_val_to_remove = 'parents'
    else: 
      reciprocate_val_to_remove = link_type_to_remove
	  
	# Next remove the link  between the focus and the reciprocate:
    reciprocate_element = self.web_data.elements['e' + str(id_to_remove)]
    try:
      reciprocate_element.element_dict[reciprocate_val_to_remove].remove(self.focus_element.id)
    except ValueError:
      print('Value is not linked to focus element.')
    else:
      reciprocate_element.resynchronize()
    
    self.element_display.display_window.activateDisplay('web')
	
class SearchBar(TextInput):
  filter = StringProperty(None)
  selected_result = NumericProperty(None)
  parent_display_type = StringProperty()
  results_orientation = StringProperty(None)
  results_view_link = ObjectProperty(None)
  results_tray_link = ObjectProperty(None)
  parent_linker_type = ObjectProperty(None)
  
  def dynamicSearch(self, search_str, filter):
    app = App.get_running_app()
    search_results = app.root.web_data.search(search_str, filter)
    if len(search_results) > 0:
      self.results_tray_link.clear_widgets()
      if self.parent_display_type == 'web':
        self.results_view_link.num_results = len(search_results) + 1
        add_new_element_btn = SearchResultBtn(root_link=app.root, 
                                              text='Add new element...', 
                                              mode='new',
                                              parent_linker_type = self.parent_linker_type,
                                              parent_display_type = self.parent_display_type
                                              )
        self.results_tray_link.add_widget(add_new_element_btn)
		
    for element in search_results:
      data = app.root.web_data.elements[search_results[element]]
      result = SearchResultBtn(element_data=data,
                               root_link=app.root,
                               text=element,
                               parent_linker_type=self.parent_linker_type,
                               parent_display_type=self.parent_display_type							   
                               )
      result.parent_linker_type=self.parent_linker_type
      self.results_tray_link.add_widget(result)
  
  def on_focus(self, *args):
    app = App.get_running_app()
    if self.focus == True:
      if self.results_orientation == 'above':
        pos_for_results = [self.pos[0], self.pos[1] + self.height]
      else:
        pos_for_results = self.pos[0], self.pos[1] - 125
      if self.parent_linker_type == None:
        app.root.app_float = FloatLayout(size=app.root.size)
        app.root.add_widget(app.root.app_float)
      app.root.search_res_display = SearchResults(search_bar_width=self.width, 
                                                  search_bar_pos=pos_for_results)
      
      app.root.app_float.add_widget(app.root.search_res_display)	 
      self.results_view_link = app.root.search_res_display	  
      self.results_tray_link = app.root.search_res_display.results_tray
	  
class SearchResults(ScrollView):
  num_results = NumericProperty(0)
  results_anchor = ObjectProperty(None)
  results_tray = ObjectProperty(None)
  search_bar_pos = ListProperty(None)
  search_bar_width = NumericProperty(None)
  
  def on_num_results(self, *args):
    self.results_anchor.size = self.width, self.num_results * 25	  

"""	
  def on_touch_down(self, touch):
    app = App.get_running_app()
    if (touch.pos[0] >= self.search_pos[0] 
        and touch.pos[0] <= self.search_pos[0] + self.search_size[0]
	    and touch.pos[1] >= self.search_pos[1] 
        and touch.pos[1] <= self.search_pos[0] + self.search_size[1]):
      return False
    else:
      app.root.remove_widget(self)
      return True
"""
class SearchResultBtn(Button):
  mode = StringProperty()
  element_data = ObjectProperty(None)
  type_color = ListProperty(None)
  root_link = ObjectProperty(None)
  parent_display_type = StringProperty()
  parent_linker_type = StringProperty(None)
  
  def __init__(self, **kwargs):
    super(Button, self).__init__(**kwargs)
    if self.mode == 'new':
      self.type_color = [1, 1, 1, 1]
    else:
      self.type_color = self.root_link.web_data.type_colors_kivy[self.element_data.type]
	
  def selectSearchResult(self):
    # If the selected search result is a "Add new element..." search "result":
    if self.mode == 'new':
      # For searches called by linker buttons in the element web, create a NewElement
	  # prompt to replace the search bar: 
      if self.parent_linker_type != None:
        new_element = NewElement(pos=(self.root_link.search_res_display.pos[0],
                                      self.root_link.search_res_display.pos[1] + 124
                                      )
                                 )
        new_element.parent_display_type = self.parent_display_type
		# Tells the NewElement object to link the resulting new element to the focus:
        new_element.link_to_focus = True 
        new_element.parent_linker_type = self.parent_linker_type
        new_element.nameNewElement()
      # For searches called by the static search bar, 
      self.root_link.app_float.clear_widgets()
      self.root_link.app_float.add_widget(new_element)
      
    else:
      # If the selected search result was an element, behavior depends on what called the 
	  #search:
	  # For searches called by the static search bar, simply make the selected element 
	  # the focus and reset the static search bar's text:
      if (self.parent_linker_type == None and self.parent_display_type == 'web'):
        self.root_link.focus_element = self.element_data
        self.root_link.element_display.display_window.activateDisplay('web')
        self.root_link.static_search_bar.text = ''
      # For searches called by a linker button, link the selected element to the focus:
      else:
        self.root_link.updateElementLinks(link_type_to_update=self.parent_linker_type, 
                                          id_to_link=self.element_data.id
                                          )
      self.root_link.remove_widget(self.root_link.app_float)	
      self.root_link.element_display.display_window.activateDisplay('web')
	
"""
These widgets make up the left hand window of the application, which contains all widgets for the 
Element Web itself.
"""
# Holds the various ways of displaying Elements and the ElementDisplayBar:
class ElementDisplay(BoxLayout):
  display_window = ObjectProperty(None)
  
# A bar of display formats for Elements in the Web. Sits at the top of ElementDisplay:
class ElementDisplayBar(BoxLayout):
  detail_display_label = ObjectProperty(None)    
  
# A window of display formats resulting from ElementDisplayBar selections:
class ElementDisplayWindow(Widget):
  flat_web_scroll = ObjectProperty(None)
  web_layout = ObjectProperty(None)
  
  def activateDisplay(self, display_type):
    app = App.get_running_app()
    self.clear_widgets()
    if display_type == 'flat':
      app.root.static_search_bar.parent_display_type = 'flat'
      self.flat_web_scroll = ElementFlatScroll(size=self.size, pos=self.pos, do_scroll_x=False)
      flat_web = ElementFlat(root_link=app.root, 
                             size=self.flat_web_scroll.size,
                             pos=self.flat_web_scroll.pos
                             )
      flat_web.getFlatElements()
      self.flat_web_scroll.add_widget(flat_web)
      self.add_widget(self.flat_web_scroll)	
    elif display_type == 'web':
      app.root.static_search_bar.parent_display_type = 'web'	  
      current_focus = app.root.focus_element
      self.web_layout = ElementWeb(size=self.size, 
                                   pos=self.pos, 
                                   focus=current_focus,
                                   root_link=app.root)
      self.add_widget(self.web_layout)
      self.web_layout.getElementWeb()
  
# Tab that displays all Elements in the Web on one screen:
class ElementFlatScroll(ScrollView):
  flat_web = ObjectProperty(None)
  
class ElementFlat(StackLayout):
  root_link = ObjectProperty(None)
  
  # Loops through all Elements in the Web and adds them to the ScrollView:
  def getFlatElements(self):
    self.clear_widgets()
    counter = 0
    for e_id in self.root_link.web_data.elements:
      data = self.root_link.web_data.elements[e_id]
      new_element = Element(element_data=data,
                            details_link=self.root_link.element_details,
                            root_link=self.root_link					
                            )
      self.add_widget(new_element)
      counter += 1
    print("Added %i elements to flat element display." % counter)
    add_element_button = NewElement(parent_display_type='flat')
    self.add_widget(add_element_button)		
  
# Tab that displays a focus Element and its related Elements from the Web:
class ElementWeb(BoxLayout):
  root_link = ObjectProperty(None)  
  focus = ObjectProperty(None)
  disable_relationships = BooleanProperty(True)
  
  parent_layout = ObjectProperty(None)
  
  relation_layout = ObjectProperty(None)
  # Sub layouts of relation_layout:
  enemies_layout = ObjectProperty(None)
  focus_layout = ObjectProperty(None)
  focus_el_anchor = ObjectProperty(None)
  allies_layout = ObjectProperty(None)
  
  child_layout_width_hint = NumericProperty(0)
  child_layout_height = NumericProperty(0)
  child_layout = ObjectProperty(None)
  # Used to set up the sub layouts of the child_layout. Child types is used to 
  # keep the layouts in the same order every time:
  child_types = ListProperty(['Agent', 'Asset', 'Blackmail', 'Title', 'Party', 'Agnostic'])
  focus_children_types = DictProperty(None)
  # Sub layouts of the child_layout:
  agent_layout = ObjectProperty(None)
  asset_layout = ObjectProperty(None)
  blackmail_layout = ObjectProperty(None)
  title_layout = ObjectProperty(None)
  party_layout = ObjectProperty(None)
  agnostic_layout = ObjectProperty(None)
  
  def createLinkLayout(self, layout_type):
    links_to_loop = []
    check_link_el_type = False
    if layout_type == 'parents':
      links_to_loop = self.focus.parents
      target_layout = self.parent_layout
    elif layout_type == 'enemies':
      links_to_loop = self.focus.enemies
      target_layout = self.enemies_layout
    elif layout_type == 'allies':
      links_to_loop = self.focus.allies
      target_layout = self.allies_layout
    else:
      links_to_loop = self.focus.children
      check_link_el_type = True
      if layout_type == 'Agent':
        target_layout = self.agent_layout	
      elif layout_type == 'Asset':
        target_layout = self.asset_layout
      elif layout_type == 'Blackmail':
        target_layout = self.blackmail_layout
      elif layout_type == 'Title':
        target_layout = self.title_layout
      elif layout_type == 'Party':
        target_layout = self.party_layout		
      else:
        target_layout = self.agnostic_layout	  

    layout_height = 0
    layout_width = 0
		
    for id in links_to_loop:
      data = self.root_link.web_data.elements['e' + str(id)]
      # For child layout building, each child in links_to_loop must have its type
      # verified to make sure it matches type_layout and can thus be safely added to
	  # the target_layout:
      if check_link_el_type and layout_type == 'Agnostic':
        if (data.type == 'Agent'
            or data.type == 'Asset'
            or data.type == 'Blackmail'
            or data.type == 'Title'
            or data.type == 'Party'):		
          continue
        else:
          pass
      elif check_link_el_type:
        if data.type == layout_type:
          pass
        else:
          continue	  
        
      element_to_hold = Element(element_data=data,
                                root_link=self.root_link,
                                details_link=self.root_link.element_details
                                )
      element_to_hold.texture_update() # Forces kivy to generate the texture sizes so we can use 
                                       # it to set sizes for layouts and such.
      holder = LinkHolder(root_link=self.root_link,
                          element_id = data.id,
                          unlinker_type=layout_type,
                          holder_height=element_to_hold.texture_size[1]
                          )						  
      holder.link_anchor.add_widget(element_to_hold)
      
      target_layout.add_widget(holder)
	  
      layout_height += element_to_hold.texture_size[1]
      if layout_width < element_to_hold.texture_size[0]:
        layout_width = element_to_hold.texture_size[0]
    target_layout.height = layout_height
    layout_width = (layout_width + 20) * 1.1
    target_layout.width = layout_width
    return layout_width, layout_height
	  
  def getElementWeb(self):
    self.parent_layout.clear_widgets()
    self.enemies_layout.clear_widgets()
    self.focus_el_anchor.clear_widgets()
    self.allies_layout.clear_widgets()

    self.child_layout.clear_widgets()

    focus_element = Element(element_data=self.focus,
                            root_link=self.root_link,
                            details_link=self.root_link.element_details
                            )
    self.focus_el_anchor.add_widget(focus_element)
	
	# Add parents to web:
    self.createLinkLayout('parents')

    # Add enemies and allies to web:
    if (self.focus.type == 'NPC' or self.focus.type == 'Player'):
      self.disable_relationships = False

      # Add enemies:
      self.createLinkLayout('enemies')
		
      # Add allies:
      self.createLinkLayout('allies')
	  
    # Add children to the web:
    # Check each child's type and set up the necessary layouts that will need to be populated:
    for id in self.focus.children:
      child_el = self.root_link.web_data.elements['e' + str(id)]
      if child_el.type == 'Agent':	  
        self.agent_layout = LinkedElTray()
        self.focus_children_types['Agent'] = self.agent_layout
      elif child_el.type == 'Asset':	  
        self.asset_layout = LinkedElTray()
        self.focus_children_types['Asset'] = self.asset_layout
      elif child_el.type == 'Blackmail':	  
        self.blackmail_layout = LinkedElTray()
        self.focus_children_types['Blackmail'] = self.blackmail_layout
      elif child_el.type == 'Title':	  
        self.title_layout = LinkedElTray()
        self.focus_children_types['Title'] = self.title_layout
      elif child_el.type == 'Party':	  
        self.party_layout = LinkedElTray()
        self.focus_children_types['Party'] = self.party_layout		
      else:		  
        self.agnostic_layout = LinkedElTray()
        self.focus_children_types['Agnostic'] = self.agnostic_layout

	# Set the child_layout_width_hint based on how many layouts are needed:
    self.child_layout_width_hint = len(self.focus_children_types) * .2	
    # This is just insurance, it should be impossible for child_layout_width_hint to 
    # exceed 1:	
    if self.child_layout_width_hint > 1:
      self.child_layout_width_hint = 1 
	  
    # Loop over the child_types property (which keeps the layouts in the same order each time)
	# and populate the layouts:
    for type in self.child_types:
      # Try skips types that are not needed:
      try:
        self.child_layout.add_widget(self.focus_children_types[type])
      except KeyError:
        continue
      else:
        _, one_time_height = self.createLinkLayout(type)
        if self.child_layout_height < one_time_height:
          self.child_layout_height = one_time_height
		
# Used to block out the sub-regions of the ElementWeb window:
class WebRegion(AnchorLayout):
  pass
  
# Used to store linked elements in a neat stack:
class LinkedElTray(BoxLayout):
  pass
  
# Used to hold the unlink button and anchor layout that holds linked elements:
class LinkHolder(BoxLayout):
  root_link = ObjectProperty(None)
  element_id = NumericProperty(None)
  link_anchor = ObjectProperty(None)
  unlinker_type = StringProperty()
  holder_height = NumericProperty(None)
  
# All visible widgets in the ElementWeb and ElementFlat are Elements of various types.
class Element(Button):
  element_key = StringProperty()
  element_data = ObjectProperty(None)
  element_name = StringProperty()
  type_color = ListProperty()
  
  # Various objects designed to hold links to other widgets in the app that all Elements
  # need to be able to alter:
  root_link = ObjectProperty(None) # Used to access web meta_data.
  details_link = ObjectProperty(None) # Used to set up the next three links.
  notes_container_link = ObjectProperty(None) # Used to supply selected element notes.
  display_label_link = ObjectProperty(None) # Used to supply what element is selected.
  type_content_link = ObjectProperty(None) # Used to supply type-specifc content.  
  
  def __init__(self, **kwargs):
    super(Button, self).__init__(**kwargs)
    self.element_name = self.element_data.name
    self.type_color = self.root_link.web_data.type_colors_kivy[self.element_data.type]

    # Set up links:
    self.notes_container_link = self.details_link.notes_container
    self.display_label_link = self.details_link.detail_display_bar.detail_display_label
    self.type_content_link = self.details_link.type_content
  
  def selectElement(self):
    self.root_link.selected_element = self.element_data
    print('Selected ' + self.element_data.name)
    self.notes_container_link.activateElementNotes()
    self.display_label_link.text = 'Currently selected: ' + self.element_name
    self.type_content_link.addTypeContent(self.element_data.type)
	
  def on_touch_down(self, touch):
    if touch.is_double_tap and self.collide_point(touch.pos[0], touch.pos[1]):
      self.root_link.focus_element = self.element_data
      self.root_link.element_display.display_window.activateDisplay('web')
    elif self.collide_point(touch.pos[0], touch.pos[1]):
      self.root_link.selected_element = self.element_data
      self.selectElement()
	  
class NewElement(BoxLayout):
  name_request = ObjectProperty(None)
  type_request = ObjectProperty(None)
  new_element_obj = ObjectProperty(None)
  parent_display_type = StringProperty()
  link_to_focus = BooleanProperty(False)
  parent_linker_type = StringProperty(None)
  
  def addNewElementToWeb(self, text, type):
    app = App.get_running_app()
	
    # Assemble new element data based on where the NewElement button sits in the tree:
    new_element_dict = {"name": text, "notes": "", "type": type}
    if new_element_dict["type"] == 'NPC':
      new_element_dict["rank"] = 'None'
      new_element_dict["stats"] = {"Charisma": -1, "Intellect": -1, "Reputation": -1}
    elif (new_element_dict["type"] == 'Faction' or new_element_dict["type"] == 'Party'):
      new_element_dict["stats"] = {"Clout": 0}
      new_element_dict["cause"] = ""
    new_element_id = app.root.web_data.addElement(new_element_dict)
    app.root.web_data.save()
    # If the NewElement object was created from a linker's search, we need to link it to the focus:
    if self.link_to_focus:
      app.root.updateElementLinks(link_type_to_update=self.parent_linker_type, 
                                  id_to_link=new_element_id
                                  )
      app.root.remove_widget(app.root.app_float)	
    app.root.element_display.display_window.activateDisplay(self.parent_display_type)
    if self.parent_display_type =='flat':
      self.clear_widgets()
	
    # Add the new element object to the parent
	
  def nameNewElement(self):
    app = App.get_running_app()
    self.clear_widgets()
    # For new elements in the flat element display, add a text input and type select dropdown:
    # Add the text input:
    self.name_request = NewElementInput(size_hint_y=1.1)
    self.add_widget(self.name_request)
    
	# Add the dropdown:
    dropdown = DropDown()
      
    # Populate dropdown with types from the web's meta_data:
    for type in app.root.web_data.meta_data["available_types"]:
      btn = Button(text=type, size_hint_y=None, height=25, background_normal='', color=[0, 0, 0, 1])
      color_array = app.root.web_data.type_colors_kivy[type] 
      btn.background_color=color_array		
      btn.bind(on_release=lambda btn: dropdown.select(btn.text))
      dropdown.add_widget(btn)
		
    # Add the button that triggers the dropdown:
    self.dropdown_btn = Button(text='select type', height=25)
    self.dropdown_btn.bind(on_release=dropdown.open)
    dropdown.bind(on_select=lambda instance, x: setattr(self.dropdown_btn, 'text', x))
	  
    self.add_widget(self.dropdown_btn)
	  
class NewElementInput(TextInput):
  pass
  
class LinkElement(BoxLayout):
  search_input = ObjectProperty(None)
  linker_type = StringProperty(None)
  search_orientation = StringProperty('right')
  
  def linkNewElement(self):
    app = App.get_running_app()
    search_x = -1
    search_y = self.y + 1
    if self.search_orientation == 'left':
      search_x = self.x - 250
    else:
      search_x = self.x + 50

    link_search_bar = SearchBar(pos=(search_x, search_y), size=[250, 30], size_hint=(None,None))
    
    if (self.linker_type == 'allies' or self.linker_type == 'enemies'):
      link_search_bar.filter = 'type:char'

    link_search_bar.parent_display_type='web'
    link_search_bar.parent_linker_type=self.linker_type
	
    app.root.app_float = FloatLayout(size=app.root.size)
    app.root.add_widget(app.root.app_float)	
    app.root.app_float.add_widget(link_search_bar)
  
class LinkElementInput(TextInput):
  pass

  
"""
These widgets make up the right hand window of the application, which shows notes and other details 
about elements selected in the Element Web window.
"""
class ElementDetails(BoxLayout):
  root_link = ObjectProperty(None)
  detail_display_bar = ObjectProperty(None)
  notes_container = ObjectProperty(None)
  type_content = ObjectProperty(None)
  
class ElementNotesFrame(Widget):
  element_notes = ObjectProperty(None)
  
  def activateElementNotes(self):
    app = App.get_running_app()
    self.clear_widgets()
    self.element_notes = ElementNotes(size=self.size, pos=self.pos)
    self.element_notes.root_link = app.root
    self.add_widget(self.element_notes)
    self.setNotesText()
	
  def setNotesText(self):
    self.element_notes.text = self.parent.root_link.selected_element.notes
	
class ElementNotes(TextInput):
  root_link = ObjectProperty(None)
  
class StatBubble(Widget):
  stat = StringProperty()
	  
class RankDropdown(DropDown):
  def onSelect(self, btn_to_change, selected_rank):
    app = App.get_running_app()
    setattr(btn_to_change, 'text', selected_rank)
    app.root.updateElementDetails('rank', selected_rank)
	
class CauseInput(TextInput):
  root_link = ObjectProperty(None)
  
class TypeSpecificContent(BoxLayout):
  
  def addTypeContent(self, type):
    app = App.get_running_app()
    self.clear_widgets()
	
	# Add stat display for appropriate types:
    if (type == 'NPC' or type == 'Faction' or type == 'Party'):
      stat_display = GridLayout(cols=8, size=self.size, pos=self.pos, size_hint_y=.6)

	  # Set up the stats to loop over (if needed) when creating the stat grid based on the 
	  # element's type:
      if (type == 'Faction' or type == 'Party'):
        # Create a widget to hold the bubble and label:
        stat_holder = BoxLayout(orientation='vertical', size_hint=(None, None))
		
        # Grab "Clout" from the stats dict and create a bubble for it:
        stat_bubble = StatBubble(stat='d' + str(app.root.selected_element.stats["Clout"]))
        stat_holder.add_widget(stat_bubble)
        
		# Add a Clout label:
        stat_label = Label(text='Clout', color=[0, 0, 0, 1])
        stat_holder.add_widget(stat_label)
		
        stat_display.add_widget(stat_holder)
      elif type == 'NPC':
        alpha_stats = ["Charisma", "Intellect", "Reputation"]
		
        # Check to see if the NPC has a rank yet:
        if app.root.selected_element.rank == 'None':
          stats_to_loop = [0, 0, 0]
        else:
          stats_to_loop = app.root.web_data.meta_data["npc_ranks"][app.root.selected_element.rank]
        
        rank_stats = stats_to_loop[3:]
		
		# First loop over the first 3 items in stats_to_loop to put them in alpha order:
        for i in alpha_stats:
          # Create a widget to hold the bubble and label:
          stat_holder = BoxLayout(orientation='vertical', size_hint=(None, None))
		  
		  # Get the high/medium/low (0/1/2) index of the current stat and create a bubble for it:
          stat_position = app.root.selected_element.stats[i]
          stat_value = -1
          if stat_position == -1:
            stat_value = 0
          else:
            stat_value = stats_to_loop[stat_position]
          stat_bubble = StatBubble(stat='d' + str(stat_value))
		  
		  # Add the appropriate stat label:
          stat_label = Label(text=i, color=[0, 0, 0, 1], size_hint_y=0.1)
		  
		  # Add the bubble and then the label to the BoxLayout holder widget:
          stat_holder.add_widget(stat_bubble)
          stat_holder.add_widget(stat_label)
		  
          stat_display.add_widget(stat_holder)
        
		# Now loop over the remaining items in stats_to_loop (rank_stats):
        for i in rank_stats:
          # Create a widget to hold the bubble and a dummy label:
          stat_holder = BoxLayout(orientation='vertical', size_hint=(None, None))
		  
		  # Add the stat bubble:
          stat_bubble = StatBubble(stat='d' + str(i))
          stat_holder.add_widget(stat_bubble)
		  
		  # Add a dummy label:
          stat_label = Label(text="Rank", color=[1, 1, 1, 1], size_hint_y=0.1)
          stat_holder.add_widget(stat_label)
          
          stat_display.add_widget(stat_holder)

      # Add the finalized stat_display
      self.add_widget(stat_display)

	# Add other type specific displays:
    if (type == 'Faction' or type == 'Party'):
      # Add a label to indicate what is being displayed:
      cause_label = Label(text="Cause:", size_hint_y=0.1, color=[0, 0, 0, 1])
      self.add_widget(cause_label)
	  
      # Add a CauseInput to store the Faction/Party's Cause:
      cause_input = CauseInput(text=app.root.selected_element.cause, size=self.size, pos=self.pos)
      cause_input.root_link = app.root
      self.add_widget(cause_input)
	  
    elif type == 'NPC':
      # Add a label to indicate what is being displayed:
      rank_label = Label(text="NPC's rank:", size_hint_y=0.1, color=[0, 0, 0, 1])
      self.add_widget(rank_label)

      # Get the NPC's current rank:
      sel_npc_rank = app.root.selected_element.rank
      	  
      # Add a drop down for the NPC's rank:
      dropdown = RankDropdown()
	  
      # Populate dropdown with ranks from the web's meta_data:
      for rank in app.root.web_data.meta_data["npc_ranks"]:
        btn = Button(text=rank, size_hint_y=None, height=25)
        btn.bind(on_release=lambda btn: dropdown.select(btn.text))
        dropdown.add_widget(btn)
		
      # Add the button that triggers the dropdown:
      if sel_npc_rank == 'None':
        displayed_rank = 'Click to select rank'
      else:
        displayed_rank = sel_npc_rank

      self.dropdown_btn = Button(text=displayed_rank, size_hint_y=0.1)
      self.dropdown_btn.bind(on_release=dropdown.open)
      dropdown.bind(on_select=lambda instance, x: dropdown.onSelect(self.dropdown_btn, x))
	  
      self.add_widget(self.dropdown_btn)
	  
      # Add the archetype label to indicate what is being displayed:
      arch_label = Label(text="NPC's archetype:", size_hint_y=0.07, color=[0, 0, 0, 1])
      self.add_widget(arch_label)
	  
      # Add the archetype textinput:
      arch_input = TextInput(size=self.size, pos=self.pos, size_hint_y=1.5)
      self.add_widget(arch_input)	  
  
"""
Build the app:
"""
class elementWebApp(App):
  def build(self):
    app = AppFrame()
    app.focus_element = app.web_data.elements["e" + str(app.web_data.meta_data["last_id"])]
    #app.element_display.display_window.activateDisplay('web')
    Window.maximize()
#    app.focus_name = app_data.web_data.elements["e" + str(app_data.web_data.meta_data["last_id"])].name
    print(app.web_data.meta_data)
#    print(app_data.focus_name)
	
    return app


if __name__ == '__main__':
  elementWebApp().run()