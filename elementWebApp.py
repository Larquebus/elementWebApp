from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
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
from functools import partial
import operator
import time

# The core of the application. When initialized it taps into the web data file:
class AppFrame(Widget):
  web_data = ObjectProperty(webData())
  selected_element = ObjectProperty(None)
  focus_element = ObjectProperty(None)
  display_window = ObjectProperty(None)
  static_search_bar = ObjectProperty(None)
  element_details = ObjectProperty(None)
  app_overlay = ObjectProperty(None)
  search_res_display = ObjectProperty(None)
  recent_layout = ObjectProperty(None)
	
  # Updates values in the detail for the currently selected element, saves back to web:
  def updateElementDetails(self, value_to_update, new_value):
    selected_key = self.selected_element.element_key
    web_update_string = "self.web_data.elements['" + selected_key + "'].element_dict"
    el_update_string = "self.selected_element.element_dict"
    for depth_key in value_to_update:
      web_update_string = web_update_string + "['" + depth_key + "']"
      el_update_string = el_update_string + "['" + depth_key + "']"
    web_update_string = web_update_string + " = new_value"
    el_update_string = el_update_string + " = new_value"
    exec(web_update_string)
    exec(el_update_string)
	# I genuinely don't know if these next two lines are necessary because the program 
	# seems to save changes made to elements/web_data that it shouldn't be saving???
	# Frankly, I'm terrified.
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

    # Next reciprocate the link between element_to_update and the reciprocate_element:
    reciprocate_element = self.web_data.elements['e' + str(id_to_link)]
    element_to_update_id = element_to_update.id
    try:
      reciprocate_element.element_dict[reciprocate_val_to_update].append(element_to_update_id)
    except KeyError:
      reciprocate_element.element_dict[reciprocate_val_to_update] = []
      reciprocate_element.element_dict[reciprocate_val_to_update].append(element_to_update_id)
    self.web_data.elements[reciprocate_element.element_key].resynchronize()

	# I genuinely don't know if these next two lines are necessary because the program 
	# seems to save changes made to elements/web_data that it shouldn't be saving???
	# Frankly, I'm terrified.
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
    
    self.activateWebDisplay()
	
  def loadRecentElements(self, *args):
    self.recent_layout.clear_widgets()
    recent_elements = self.web_data.id_history
    history_len = len(recent_elements)
    width_needed = 0
    for id in recent_elements:
      element_key = "e" + str(id)
      element = Element(element_data=self.web_data.elements[element_key],
                        root_link=self,
                        details_link=self.element_details
                        )
      element.texture_update()
      width_needed += element.texture_size[0]
      self.recent_layout.add_widget(element)
    self.recent_layout.width = width_needed

  def activateFlatDisplay(self, *args):
    self.display_window.clear_widgets() 
    self.static_search_bar.parent_display_type = 'flat'
    flat_web_scroll = ElementFlatScroll(size=self.display_window.size, 
                                        pos=self.display_window.pos, 
                                        do_scroll_x=False
                                        )
    self.display_window.flat_web = ElementFlat(root_link=self, 
                                               elements=self.web_data.elements,
                                               size=self.display_window.size,
                                               pos=self.display_window.pos
                                               )
    self.display_window.flat_web.getFlatElements()
    flat_web_scroll.add_widget(self.display_window.flat_web)
    self.display_window.add_widget(flat_web_scroll)	
	  
  def activateWebDisplay(self, *args):
    self.display_window.clear_widgets()   
    self.static_search_bar.parent_display_type = 'web'	  
    current_focus = self.focus_element
    self.display_window.web_layout = ElementWeb(size=self.display_window.size, 
                                                pos=self.display_window.pos, 
                                                focus=current_focus,
                                                root_link=self)
    self.display_window.add_widget(self.display_window.web_layout)
    self.display_window.web_layout.getElementWeb()

  def activateNewElementPopUp(self, *args):
    new_el_pop_up = NewElementPopUp()
    self.app_overlay = AnchorLayout(anchor_x='center',
                                    anchor_y='center',
                                    size=self.display_window.size,
                                    pos=self.display_window.pos
                                    )
    self.add_widget(self.app_overlay)
    self.app_overlay.add_widget(new_el_pop_up)

  def on_focus_element(self, *args):
    try:
      self.web_data.id_history.index(self.focus_element.id)
    except ValueError:
      self.web_data.id_history.insert(0, self.focus_element.id)
      self.web_data.save()
    else:
      self.web_data.id_history.remove(self.focus_element.id)
      self.web_data.id_history.insert(0, self.focus_element.id)
      self.web_data.save()
    self.loadRecentElements()
	
class SearchBar(TextInput):
  filter = StringProperty(None)
  selected_result = NumericProperty(None)
  parent_display_type = StringProperty()
  results_orientation = StringProperty('below')
  results_view_link = ObjectProperty(None)
  results_tray_link = ObjectProperty(None)
  parent_linker_type = ObjectProperty(None)
  
  def dynamicSearch(self, search_str, filter):
    app = App.get_running_app()
    search_results = app.root.web_data.search(search_str, filter)
    if len(search_results) > 0:
      
      if self.parent_display_type == 'web':
        self.results_tray_link.clear_widgets()
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
      elif self.parent_display_type == 'flat':
        search_result_elements = {}
        for key in search_results:
          e_id = search_results[key]
          search_result_elements[e_id] = app.root.web_data.elements[e_id]
        app.root.display_window.flat_web.elements = search_result_elements
        app.root.display_window.flat_web.getFlatElements()
  
  def on_focus(self, *args):
    app = App.get_running_app()
    if self.focus == True:
      if self.parent_display_type == 'web':
        if self.results_orientation == 'above':
          pos_for_results = [self.pos[0], self.pos[1] + self.height]
        else:
          pos_for_results = self.pos[0], self.pos[1] - 125
        if self.parent_linker_type == None:
          app.root.app_overlay = SearchOverlay(size=app.root.size)
          app.root.app_overlay.input_obj = self
          app.root.add_widget(app.root.app_overlay)
        app.root.search_res_display = SearchResults(search_bar_width=self.width, 
                                                    search_bar_pos=pos_for_results,
                                                    results_orientation=self.results_orientation
                                                    )      
        app.root.app_overlay.add_widget(app.root.search_res_display)
        app.root.app_overlay.results_obj = app.root.search_res_display	  
        self.results_view_link = app.root.search_res_display	  
        self.results_tray_link = app.root.search_res_display.results_tray  
	  
class SearchOverlay(FloatLayout):
  input_obj = ObjectProperty(None)
  results_obj = ObjectProperty(None)
  
  def on_touch_down(self, touch):
    app = App.get_running_app()
    if (self.input_obj.collide_point(*touch.pos) or
        self.results_obj.collide_point(*touch.pos)):
      super(FloatLayout, self).on_touch_down(touch) # This lets the touch pass on to children.
      return True
    else:
      self.input_obj.text = ''
      app.root.remove_widget(self)
      return True
	  
class SearchResults(ScrollView):
  num_results = NumericProperty(0)
  results_orientation = StringProperty()
  search_results_height = NumericProperty(50)
  results_anchor = ObjectProperty(None)
  results_tray = ObjectProperty(None)
  search_bar_pos = ListProperty(None)
  search_bar_width = NumericProperty(None)
  
  def on_num_results(self, *args):
    if self.num_results < 5 and self.results_orientation == 'above':
      self.search_results_height = self.num_results * 25
    else:
      self.search_results_height = 125
	# The results_anchor is enclosed in the ScrollView and thus can be as tall as needed:
    self.results_anchor.size = self.width, self.num_results * 25	  

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
    new_element_pos = [0, 0]
    # If the selected search result is a "Add new element..." search "result":
    if self.mode == 'new':
      new_element = NewElementPopUp()
      # For searches called by linker buttons in the element web, create a NewElementPopUp
	  # prompt to replace the search bar: 
      if self.parent_linker_type != None:
        new_element_pos = [self.root_link.search_res_display.pos[0],
                           self.root_link.search_res_display.pos[1] + 124]
        new_element.pos = new_element_pos
		# Tells the NewElementPopUp object to link the resulting new element to the focus:
        new_element.link_to_focus = True 
        new_element.parent_linker_type = self.parent_linker_type
      # For searches called by the static search bar, create a NewElement prompt and 
	  # place it roughly in the center of the display window, and instruct the NewElement
	  # object to set the focus as the new element upon creation:
      else: 
        self.root_link.display_window.clear_widgets()
        new_element_pos = self.root_link.display_window.center
        new_element.center = new_element_pos
      new_element.parent_display_type = self.parent_display_type		
      self.root_link.app_overlay.clear_widgets()
      self.root_link.app_overlay.input_obj = new_element
      self.root_link.app_overlay.add_widget(new_element)
    else:
      # If the selected search result was an element, behavior depends on what called the 
	  #search:
	  # For searches called by the static search bar, simply make the selected element 
	  # the focus and reset the static search bar's text:
      if (self.parent_linker_type == None and self.parent_display_type == 'web'):
        self.root_link.focus_element = self.element_data
        self.root_link.activateWebDisplay()
        self.root_link.static_search_bar.text = ''
      # For searches called by a linker button, link the selected element to the focus:
      else:
        self.root_link.updateElementLinks(link_type_to_update=self.parent_linker_type, 
                                          id_to_link=self.element_data.id
                                          )
      self.root_link.remove_widget(self.root_link.app_overlay)	
      self.root_link.activateWebDisplay()
  
  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      touch.grab(self)
      touch.ungrab(self)
      super(Button, self).on_touch_down(touch) #This lets the touch act on the button.
      return True
	
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
  flat_web = ObjectProperty(None)
  
# Tab that displays all Elements in the Web on one screen:
class ElementFlatScroll(ScrollView):
  flat_web = ObjectProperty(None)
  
class ElementFlat(StackLayout):
  root_link = ObjectProperty(None)
  elements = DictProperty(None)
  
  # Loops through all Elements in the Web and adds them to the ScrollView:
  def getFlatElements(self):
    self.clear_widgets()
    counter = 0
    for e_id in self.elements:
      data = self.elements[e_id]
      new_element = Element(element_data=data,
                            details_link=self.root_link.element_details,
                            root_link=self.root_link					
                            )
      self.add_widget(new_element)
      counter += 1
    add_element_button = Button(text='Add new element...', 
                                padding=[10, 10],
                                size_hint=(None,None)
                                )
#    add_element_button.texture_update()
#    add_element_button.size = add_element_button.texture_size
#    add_element_button.bind(on_press=self.root_link.activateNewElementPopUp)
#    self.add_widget(add_element_button)		
  
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
    unlinker_type = layout_type
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
      unlinker_type = 'children'
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
                          unlinker_type=unlinker_type,
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
  details_link = ObjectProperty(None) # Used to access the details window.
  
  def __init__(self, **kwargs):
    super(Button, self).__init__(**kwargs)
    self.element_name = self.element_data.name
    self.type_color = self.root_link.web_data.type_colors_kivy[self.element_data.type]
  
  def selectElement(self):
    self.root_link.selected_element = self.element_data
    self.details_link.activateElementDetails()
	
  def on_touch_down(self, touch):
    if touch.is_double_tap and self.collide_point(touch.pos[0], touch.pos[1]):
      self.root_link.focus_element = self.element_data
      self.root_link.activateWebDisplay()
    elif self.collide_point(touch.pos[0], touch.pos[1]):
      self.root_link.selected_element = self.element_data
      self.selectElement()

class NewElementPopUp(BoxLayout):
  parent_display_type = StringProperty()
  link_to_focus = BooleanProperty(False)
  parent_linker_type = StringProperty(None)    
  type_dropdown_btn = ObjectProperty(None)
  type_dropdown = ObjectProperty(None)
  name_input = ObjectProperty(None)
  validate_btn = ObjectProperty(None)
  type_error_msg = ObjectProperty(None)

  def __init__(self, **kwargs):
    super(BoxLayout, self).__init__(**kwargs)
    app = App.get_running_app()
    if self.parent_display_type == 'flat':
      self.pos_hint = [None, None]
    self.type_dropdown = DropDown()
	
    # Populate dropdown with types from the web's meta_data:
    for type in app.root.web_data.meta_data["available_types"]:
      btn = Button(text=type, size_hint_y=None, height=25, background_normal='', color=[0, 0, 0, 1])
      color_array = app.root.web_data.type_colors_kivy[type] 
      btn.background_color=color_array		
      btn.bind(on_release=lambda btn: self.type_dropdown.select(btn.text))
      self.type_dropdown.add_widget(btn)

    self.type_dropdown_btn.bind(on_release=self.type_dropdown.open)
    self.type_dropdown.bind(on_select=lambda instance, x: setattr(self.type_dropdown_btn, 'text', x))

  def clearError(self, *args):
    self.type_error_msg.text = ''

  def validateNewElement(self):
    if self.type_dropdown_btn.text == 'select type':
      self.type_error_msg.text = 'Type is required.'
      Clock.schedule_once(self.clearError, 2)
    else:
      self.addNewElementToWeb()

  def addNewElementToWeb(self):
    app = App.get_running_app()
    name = self.name_input.text
    type = self.type_dropdown_btn.text
    # Assemble new element data based on where the NewElement button sits in the tree:
    new_element_dict = {"name": name, "notes": "", "type": type}
    if new_element_dict["type"] == 'NPC':
      new_element_dict["rank"] = 'None'
      new_element_dict["stats"] = {"Charisma": -1, "Intellect": -1, "Reputation": -1}
    elif (new_element_dict["type"] == 'Faction' or new_element_dict["type"] == 'Party'):
      new_element_dict["stats"] = {"Clout": -1}
      new_element_dict["cause"] = ""
    new_element_id = app.root.web_data.addElement(new_element_dict)
    app.root.web_data.save()
    # If the NewElementPopUp object was created from a linker's search, we need to link it to the focus:
    if self.link_to_focus:
      app.root.updateElementLinks(link_type_to_update=self.parent_linker_type, 
                                  id_to_link=new_element_id
                                  )
    elif self.parent_display_type == 'web':
      app.root.focus_element = app.root.web_data.elements["e" + str(new_element_id)]
    app.root.remove_widget(app.root.app_overlay)	
    if self.parent_display_type == 'web':
      app.root.activateWebDisplay()
    else: 
      app.root.activateFlatDisplay()	
  
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
	
    app.root.app_overlay = SearchOverlay(size=app.root.size)
    app.root.app_overlay.input_obj = link_search_bar
    app.root.add_widget(app.root.app_overlay)	
    app.root.app_overlay.add_widget(link_search_bar)
  
class LinkElementInput(TextInput):
  pass

  
"""
These widgets make up the right hand window of the application, which shows notes and other details 
about elements selected in the Element Web window.
"""
class ElementDetails(BoxLayout):
  root_link = ObjectProperty(None)
  detail_display_bar = ObjectProperty(None)
  dynamic_bar_content = ObjectProperty(None)
  notes_container = ObjectProperty(None)
  type_content = ObjectProperty(None)
  
  def activateElementDetails(self):
    selected_element = self.root_link.selected_element
	
    # Clear the dynamic display bar content and repopulate:
    self.dynamic_bar_content.clear_widgets()
    selected_element_name = DetailNameInput(root_link=self.root_link,
                                            text=selected_element.name)
    self.dynamic_bar_content.add_widget(selected_element_name)
	
	# Add notes:
    self.notes_container.activateElementNotes()

	# Add content based on selected element type:
    self.type_content.addTypeContent(selected_element.type)
	
class DetailNameInput(TextInput):
  root_link = ObjectProperty(None)

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
  
class StatToggles(BoxLayout):
  high_btn = ObjectProperty(None)
  med_btn = ObjectProperty(None)
  low_btn = ObjectProperty(None)
  stat_group = StringProperty()
  stat_val = NumericProperty()
  
  def setStat(self, stat, stat_val):
    app = App.get_running_app()
    app.root.updateElementDetails(['stats', stat], stat_val)
    app.root.element_details.type_content.addTypeContent(app.root.selected_element.type)
	  
class RankDropdown(DropDown):
  def onSelect(self, btn_to_change, selected_rank):
    app = App.get_running_app()
    setattr(btn_to_change, 'text', selected_rank)
    app.root.updateElementDetails(['rank'], selected_rank)
	
class CauseInput(TextInput):
  root_link = ObjectProperty(None)
  
class Agenda(BoxLayout):
  root_link = ObjectProperty(None)
  player_element = ObjectProperty(None)
  button_bar = ObjectProperty(None)
  agenda_scope = StringProperty()
  ambition_input = ObjectProperty(None)
  opposition_input = ObjectProperty(None)
  objective_tray = ObjectProperty(None)
  support_tray = ObjectProperty(None)
  num_objectives = NumericProperty(0)
  num_support = NumericProperty(0)
  
  def activateAgenda(self):
    app = App.get_running_app()
    self.ambition_input.text = self.player_element.agenda["ambition"]
    self.opposition_input.text = self.player_element.agenda["opposition"]
	
    self.agenda_scope = self.player_element.agenda["scope"]
    
	# Add the scope dropdown:
    dropdown = ScopeDropdown()
      
    # Populate dropdown with scopes from the web's meta_data:
    for scope in app.root.web_data.meta_data["agenda_scopes"]:
      btn = Button(text=scope, size_hint_y=None, height=25)	
      btn.bind(on_release=lambda btn: dropdown.select(btn.text))
      dropdown.add_widget(btn)
	  
    if self.agenda_scope == '':
      displayed_scope = 'select scope'
    else:
      displayed_scope = self.agenda_scope	
		
    # Add the button that triggers the dropdown:
    dropdown_btn = Button(text=displayed_scope, height=25)
    dropdown_btn.bind(on_release=dropdown.open)
    dropdown.bind(on_select=lambda instance, x: dropdown.onSelect(dropdown_btn, x))
	
    self.button_bar.add_widget(dropdown_btn)
    
    if self.agenda_scope == '':
      pass
    else: 
      if self.player_element.objectives == {}:
        self.createObjectives()
      else:
        self.loadObjectives()
      if self.player_element.support == {}:
        self.createSupport()
      else:
        self.loadSupport()
	
  def createObjectives(self):
    app = App.get_running_app()
    self.num_objectives = app.root.web_data.meta_data["agenda_scopes"][self.agenda_scope]["objectives"]
    objective_dict = {}
    for i in range(1, self.num_objectives + 1):
      obj_id = "obj_" + str(i)
      objective_dict[obj_id] = {"completed?": 0, "obj_text": ''}
      objective = Objective(root_link=app.root,
                            obj_id=obj_id,
                            objective_text=objective_dict[obj_id]["obj_text"])
      self.objective_tray.add_widget(objective)
    app.root.updateElementDetails(['objectives'], objective_dict)

  def loadObjectives(self):
    app = App.get_running_app()
    self.num_objectives = app.root.web_data.meta_data["agenda_scopes"][self.agenda_scope]["objectives"]
    for i in range(1, self.num_objectives + 1):
      obj_id = "obj_" + str(i)
      obj_data = self.player_element.objectives[obj_id]
      if obj_data["completed?"] == 1:
        complete_boolean = True
      else:
        complete_boolean = False
      objective = Objective(root_link=app.root,
                            obj_id=obj_id,	  
                            complete_ind=complete_boolean)
      objective.objective_text.text = obj_data["obj_text"]
      self.objective_tray.add_widget(objective)
	
  def createSupport(self):
    app = App.get_running_app()
    self.num_support = app.root.web_data.meta_data["agenda_scopes"][self.agenda_scope]["support"]
    supp_dict = {}
    for i in range(1, self.num_support + 1):
      supp_id = "supp_" + str(i)
      supp_dict[supp_id] = ''
      support = Support(text=supp_dict[supp_id],
                        root_link=app.root,
                        supp_id=supp_id
                        )
      self.support_tray.add_widget(support)
    app.root.updateElementDetails(['support'], supp_dict) 

  def loadSupport(self):
    app = App.get_running_app()
    self.num_support = app.root.web_data.meta_data["agenda_scopes"][self.agenda_scope]["support"]
    for i in range(1, self.num_support + 1):
      supp_id = "supp_" + str(i)
      supp_data = self.player_element.support[supp_id]
      support = Support(text=supp_data,
                        root_link=app.root,
                        supp_id=supp_id
                        )
      self.support_tray.add_widget(support)
	  
  def clearConfirm(self):
    app = App.get_running_app()
    conf_screen = ClearConfirmation(root_link=app.root)
    app.root.add_widget(conf_screen)
  
class AgendaInput(TextInput):
  pass
  
class Objective(BoxLayout):
  root_link = ObjectProperty(None)
  obj_id = StringProperty()
  complete_toggle = ObjectProperty(None)
  complete_ind = BooleanProperty(False)
  objective_text = ObjectProperty(None)
  
  def completeObjToggle(self):
    checkbox_val = 0
    if self.complete_toggle.active:
      checkbox_val = 1
    self.root_link.updateElementDetails(['objectives', self.obj_id, 'completed?'], checkbox_val)
  
class Support(TextInput):
  root_link = ObjectProperty(None)
  supp_id = StringProperty()
  
class ScopeDropdown(DropDown):
  def onSelect(self, btn_to_change, selected_scope):
    app = App.get_running_app()
    setattr(btn_to_change, 'text', selected_scope)
    app.root.updateElementDetails(['agenda', 'scope'], selected_scope)
    app.root.element_details.activateElementDetails()
	
class ClearConfirmation(AnchorLayout):
  root_link = ObjectProperty(None)
  confirmation_box = ObjectProperty(None)
	
  def clearAgenda(self):
    self.root_link.updateElementDetails(['agenda', 'ambition'], '')
    self.root_link.updateElementDetails(['agenda', 'opposition'], '')
    self.root_link.updateElementDetails(['agenda', 'scope'], '')
    self.root_link.updateElementDetails(['objectives'], {})
    self.root_link.updateElementDetails(['support'], {})
    self.root_link.element_details.activateElementDetails()
    self.root_link.remove_widget(self)
	
  def on_touch_down(self, touch):
    app = App.get_running_app()
    if (self.confirmation_box.collide_point(*touch.pos)):
      super(AnchorLayout, self).on_touch_down(touch) # This lets the touch pass on to children.
      return True
    else:
      self.root_link.remove_widget(self)	
      return True

class Promises(BoxLayout):
  promise_data = DictProperty(None)
  
  def activatePromises(self):
    app = App.get_running_app()
    for i in range(1, 6):
      prom_key = 'prom_' + str(i)
      promise_holder = PromiseHolder(root_link=app.root, promise_key=prom_key)
      promise_holder.promise_input.text = self.promise_data[prom_key]["promise"]
      promise_holder.promised_to_input.text = self.promise_data[prom_key]["promised_to"]
      self.add_widget(promise_holder)
  
class PromiseHolder(BoxLayout):
  root_link = ObjectProperty(None)
  promise_key = StringProperty()
  promise_input = ObjectProperty(None)
  promised_to_input = ObjectProperty(None)
  
  def clearPromise(self):
    self.promise_input.text = ''
    self.promised_to_input.text = ''

class TypeSpecificContent(BoxLayout):
  
  def addTypeContent(self, type):
    app = App.get_running_app()
    self.clear_widgets()
	
	# Add stat display for appropriate types:
    if (type == 'NPC' or type == 'Faction' or type == 'Party'):
      if type == 'NPC':
        stat_display_size = .7
      else:
        stat_display_size = .44
      stat_display = GridLayout(cols=8, size=self.size, pos=self.pos, size_hint_y=stat_display_size)

	  # Set up the stats to loop over (if needed) when creating the stat grid based on the 
	  # element's type:
      if (type == 'Faction' or type == 'Party'):
        # Create a widget to hold the bubble label, and toggles:
        stat_holder = BoxLayout(orientation='vertical', size_hint=(None, 1))
		
        # Grab "Clout" from the stats dict and create a bubble for it:
        clout_list = [10, 8, 6]
        clout_position = app.root.selected_element.stats["Clout"]
        clout_val = -1
        if clout_position == -1:
          clout_val = 0
        else:
          clout_val = clout_list[clout_position]
        stat_bubble = StatBubble(stat='d' + str(clout_val))
        stat_holder.add_widget(stat_bubble)
        
		# Add a Clout label:
        stat_label = Label(text='Clout', color=[0, 0, 0, 1], size_hint_y=0.2)
        stat_holder.add_widget(stat_label)
		
        # Add StatToggles:
        stat_toggles = StatToggles(stat_group='Clout')
        if clout_position == 0:
          stat_toggles.high_btn.state = 'down'
        elif clout_position == 1:
          stat_toggles.med_btn.state = 'down'
        elif clout_position == 2:
          stat_toggles.low_btn.state = 'down'			
        stat_holder.add_widget(stat_toggles)
		
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
          # Create a widget to hold the bubble, label, and toggles:
          stat_holder = BoxLayout(orientation='vertical', size_hint=(None, 1))
		  
		  # Get the high/medium/low (0/1/2) index of the current stat and create a bubble for it:
          stat_position = app.root.selected_element.stats[i]
          stat_value = -1
          if stat_position == -1:
            stat_value = 0
          else:
            stat_value = stats_to_loop[stat_position]
          stat_bubble = StatBubble(stat='d' + str(stat_value))
		  
		  # Add the appropriate stat label:
          stat_label = Label(text=i, color=[0, 0, 0, 1], size_hint_y=0.2)
		  
          # Determine which button should be down and add stat toggles:
          stat_toggles = StatToggles(stat_group=i)
          if stat_position == 0:
            stat_toggles.high_btn.state = 'down'
          elif stat_position == 1:
            stat_toggles.med_btn.state = 'down'
          elif stat_position == 2:
            stat_toggles.low_btn.state = 'down'		  
          		  
		  # Add the bubble and then the label to the BoxLayout holder widget:
          stat_holder.add_widget(stat_bubble)
          stat_holder.add_widget(stat_label)
          stat_holder.add_widget(stat_toggles)
		  
          stat_display.add_widget(stat_holder)
        
		# Now loop over the remaining items in stats_to_loop (rank_stats):
        for i in rank_stats:
          # Create a widget to hold the bubble and a dummy label:
          stat_holder = BoxLayout(orientation='vertical', size_hint=(None, 1))
		  
		  # Add the stat bubble:
          stat_bubble = StatBubble(stat='d' + str(i))
          stat_holder.add_widget(stat_bubble)
		  
		  # Add a dummy label:
          stat_label = Label(text="Rank", color=[1, 1, 1, 1], size_hint_y=0.2)
          stat_holder.add_widget(stat_label)
		  
          # Add a dummy toggle:
          dummy_toggle = Label(text='None', color=[1, 1, 1, 1], size_hint_y=0.2)
          stat_holder.add_widget(dummy_toggle)
          
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

    elif type == 'Player':
      promise_layout = Promises()
      promise_layout.promise_data = app.root.selected_element.promises
      promise_layout.activatePromises()
      self.add_widget(promise_layout)
      agenda = Agenda(root_link=app.root, player_element=app.root.selected_element)
      agenda.activateAgenda()
      self.add_widget(agenda)
  
"""
Build the app:
"""
class elementWebApp(App):
  app = ObjectProperty(None)
  
  def build(self):
    Window.maximize()
    self.app = AppFrame()
    self.title = 'Element Web - ' + self.app.web_data.meta_data["web_name"]
    initial_id = self.app.web_data.id_history[0]
    initial_key = "e" + str(initial_id)
    self.app.focus_element = self.app.web_data.elements[initial_key]
    # .75 is the earliest these can fire without firing before Window.maximize()...
    Clock.schedule_once(self.app.activateWebDisplay, 1)
    Clock.schedule_once(self.app.loadRecentElements, 1)
    return self.app

if __name__ == '__main__':
  elementWebApp().run()
  