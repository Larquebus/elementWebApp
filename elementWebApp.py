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
      self.name_request = NewElementInput(size_hint_y=1.1)
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
  
class TypeSpecificContent(BoxLayout):
  def addTypeContent(self, type):
    app = App.get_running_app()
    self.clear_widgets()
    if (type == 'NPC' or type == 'Faction' or type == 'Party'):
      stat_display = GridLayout(cols=8, size=self.size, pos=self.pos)

	  # Set up the stats to loop over when creating the stat grid based on the element's type:
      if type == 'NPC':	
        stats_to_loop = app.root.web_data.meta_data["npc_ranks"][app.root.selected_element.rank]
      else:
        pass
		
      for i in stats_to_loop:
        if (type == 'Faction' or type == 'Party'):
          pass
          #stat_bubble = StatBubble(stat='d' + str(i))
          #stat_display.add_widget(stat_bubble)
        else:
          stat_bubble = StatBubble(stat='d' + str(i))
          stat_display.add_widget(stat_bubble)
      self.add_widget(stat_display)
	  
    if type == 'NPC':
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

class StatBubble(Widget):
  stat = StringProperty()
	  
class RankDropdown(DropDown):
  def onSelect(self, btn_to_change, selected_rank):
    app = App.get_running_app()
    setattr(btn_to_change, 'text', selected_rank)
    app.root.updateElement('rank', selected_rank)
  
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