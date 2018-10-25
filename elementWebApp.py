from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.graphics import BorderImage

from elementWebData import *

# The core of the application. When initialized it taps into the web data file:
class AppFrame(BoxLayout):
  web_data = ObjectProperty(webData())
  selected_element = ObjectProperty(None)
  focus_object = ObjectProperty(None)
  element_display = ObjectProperty(None)
  element_details = ObjectProperty(None)
  
  # Updates values for whatever element is currently selected, saves the element back to the web:
  def updateElement(self, value_to_update, new_value):
    # These lines are repetitive... clean up somehow?
    self.selected_element.element_dict[value_to_update] = new_value
    self.web_data.elements[self.selected_element.element_key].element_dict[value_to_update] = new_value
    self.web_data.elements[self.selected_element.element_key].resynchronize()
    self.web_data.save()

"""
These widgets make up the left hand window of the application, which contains all widgets for the 
Element Web itself.
"""
# Holds the various ways of displaying Elements and the ElementDisplayBar:
class ElementDisplay(BoxLayout):
  pass
  
# A bar of display formats for Elements in the Web. Sits at the top of ElementDisplay:
class ElementDisplayBar(BoxLayout):
  detail_display_label = ObjectProperty(None)
  
# A window of display formats resulting from ElementDisplayBar selections:
class ElementDisplayWindow(Widget):
  pass
  
# Tab that displays all Elements in the Web on one screen:
class ElementFlatScroll(ScrollView):
  pass
  
class ElementFlat(StackLayout):
  web_to_display = ObjectProperty(None)
  root_link = ObjectProperty(None)
  
  # Loops through all Elements in the Web and adds them to the ScrollView:
  def getFlatElements(self):
    self.clear_widgets()
    counter = 0
    for e_id in self.root_link.web_data.elements:
      data = self.root_link.web_data.elements[e_id]
      new_element = Element(id=e_id, 
                            element_data=data,
                            element_name=data.name,
                            details_link=self.root_link.element_details							
                            )
      color_array = self.root_link.web_data.type_colors_kivy[data.type] 
      new_element.background_color=color_array
      self.add_widget(new_element)
      counter += 1
    print("Added %i elements to flat element display." % counter)
    add_element_button = NewElement(parent_display_type='flat')
    self.add_widget(add_element_button)		
  
# Tab that displays a focus Element and its related Elements from the Web:
class ElementWeb(BoxLayout):
  focus = ObjectProperty()

# Used to block out the sub-regions of the ElementWeb window:
class WebRegion(BoxLayout):
  pass
  
# All visible widgets in the ElementWeb and ElementFlat are Elements of various types.
class Element(Button):
  element_key = StringProperty()
  element_data = ObjectProperty(None)
  element_name = StringProperty()
  details_link = ObjectProperty(None)
  
  def selectElement(self):
    self.parent.root_link.selected_element = self.element_data
    print('Selected ' + self.element_data.name)
    self.details_link.notes_container.activateElementNotes()
    self.details_link.detail_display_bar.detail_display_label.text = 'Currently selected: ' + self.element_name
    self.details_link.type_content.addTypeContent(self.element_data.type)
	
class NewElement(BoxLayout):
  name_request = ObjectProperty(None)
  type_request = ObjectProperty(None)
  new_element_obj = ObjectProperty(None)
  parent_display_type = StringProperty()
  
  def addNewElementToWeb(self, text, type):
    app = App.get_running_app()
	
    # Assemble new element data based on where the NewElement button sits in the tree:
    if self.parent_display_type == 'flat':
      new_element_dict = {"name": text, "notes": "", "type": type}
      if new_element_dict["type"] == 'NPC':
        new_element_dict["rank"] = 'None'
        new_element_dict["stats"] = {"Charisma": -1, "Intellect": -1, "Reputation": -1}
      elif (new_element_dict["type"] == 'Faction' or new_element_dict["type"] == 'Party'):
        new_element_dict["stats"] = {"Clout": 0}
        new_element_dict["clout"] = ""
    app.root.web_data.addElement(new_element_dict)
    app.root.web_data.save()
    if self.parent_display_type =='flat':
      self.clear_widgets()
	
    # Add the new element object to the parent
	
  def nameNewElement(self):
    app = App.get_running_app()
    self.clear_widgets()
    if self.parent_display_type == 'flat':
      # For new elements in the flat element display, add a text input and type select dropdown:
      # Add the text input:
      self.name_request = NewElementInput(size_hint_y=1.1, focus=True)
      self.add_widget(self.name_request)
      
	  # Add the dropdown:
      dropdown = DropDown()
      
      # Populate dropdown with types from the web's meta_data:
      for type in app.root.web_data.meta_data["available_types"]:
        btn = Button(text=type, size_hint_y=None, height=25, background_normal='')
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
  
#class NewElementDropdownBtn(Button):
#  pass
  
class NewElementDropdownList(DropDown):
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
    self.clear_widgets()
    self.element_notes = ElementNotes(size=self.size, pos=self.pos)
    self.add_widget(self.element_notes)
    self.setNotesText()
	
  def setNotesText(self):
    self.element_notes.text = self.parent.root_link.selected_element.notes
	
class ElementNotes(TextInput):
  pass
  
class StatBubble(Widget):
  stat = StringProperty()
	  
class RankDropdown(DropDown):
  def onSelect(self, btn_to_change, selected_rank):
    app = App.get_running_app()
    setattr(btn_to_change, 'text', selected_rank)
    app.root.updateElement('rank', selected_rank)
	
class CauseInput(TextInput):
  pass
  
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
    Window.maximize()
#    app.focus_name = app_data.web_data.elements["e" + str(app_data.web_data.meta_data["last_id"])].name
    print(app.web_data.meta_data)
#    print(app_data.focus_name)
	
    return app


if __name__ == '__main__':
  elementWebApp().run()