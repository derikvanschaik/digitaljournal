import PySimpleGUI as sg
import datetime as datetime
from db import Db

# CONSTANTS #
sg.theme('Material1')
BG_COLOR =   'PeachPuff2'# 'light green'
WIDGET_COLOR = sg.theme_background_color()
DB = 'yourdiary.json' #this is the name of the json file that will store your entries for persistence. 

# FUNCTIONS #
def vertical_spacing(num):
	return [[sg.Text('', background_color = BG_COLOR)] for i in range(num)]

#horizontal spacing
def space(x, y):
	return sg.Text('', background_color = BG_COLOR, size=(x,y))

def button(text, key, disabled=False, size=(15,2), color = 'black'):
	return sg.Button(text, key=key, size=size, button_color=(color, WIDGET_COLOR ), disabled=disabled)

def errorMessage():
	return sg.Text('', key = '-ERROR-', text_color = 'red',font = ('default 15 italic'), background_color = BG_COLOR, justification='center', size=(30, 2))

def listbox(titles):
	return sg.Listbox(
		values = titles,
		key = '-SEARCH-RESULTS-',
		select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, 
		enable_events = True, 
		font= 'default 13 italic',
		text_color = 'grey', 
		highlight_text_color = 'black', 
		highlight_background_color = 'PeachPuff2', 
		size=(45, 10), background_color = WIDGET_COLOR, 
		no_scrollbar = True)

def new_entry_layout():
	layout = [
			  [sg.Text('Title', background_color = BG_COLOR, justification='center')], 
			  [sg.Input(key='-TITLE-', background_color=WIDGET_COLOR, text_color='black')],
			  [sg.Text('Tags', background_color = BG_COLOR, text_color='black', justification='center')],
			  [sg.Input(key='-TAGS-', background_color=WIDGET_COLOR, text_color='black')],
			  [sg.Multiline(key='-TEXT-',background_color = WIDGET_COLOR, text_color = 'black', autoscroll=True, size=(50, 15))],
			  [button('Done','-DONE-')]
			  ]

	return layout

def new_entry_window(layout):
	return sg.Window('Add entry', layout, background_color=BG_COLOR)

def browse_entry_layout(previous_disabled, next_disabled):
	layout = new_entry_layout()[:-1] #we want to remove the done button but use the rest of the elements from new entry layout 
	layout.append(	[
					button('previous','-PREVIOUS-',disabled=previous_disabled), #we want the previous button to become visible when we are showing an entry which is not first
					button('Next','-NEXT-',disabled=next_disabled), 
					sg.Button('Edit', key='-EDIT-', button_color = ('black', 'orange'), size=(15,2), metadata=False) # False -- when clicked turns to true
					]
				) 
	return layout 

def browse_entry_window(layout):
	return sg.Window('Browse Entries', layout, background_color=BG_COLOR)

def get_time_and_date():
	return datetime.datetime.now().strftime("%A %b %d, %Y [%I:%M:%S %p]") 

def update_entry_window(window, entries_list, cur_entry_num, text_disabled):
	if entries_list:
		cur_entry = entries_list[cur_entry_num][1]
		date = entries_list[cur_entry_num][0] 
		window['-TITLE-'].update(cur_entry['title'], disabled=True) #disabled since we are viewing only. 
		window['-TAGS-'].update(" ".join(cur_entry['tags']), disabled=True)
		window['-TEXT-'].update(date+'\n\n'+cur_entry['text'], disabled= not text_disabled)

def get_updated_titles(entries_list):
	titles = list( map(lambda entry: entry[1]['title'], entries_list) )
	return titles 

def sort_banner():
	return sg.Text(
		f'Sorted (Oldest-Newest)',
		font=("default 12 italic"),key='-SORT-VALUE-',
		text_color='Navy Blue', background_color=BG_COLOR,
		size = (26,1), 
		)

# helper function for sort function
def get_title(entry):
	return entry[1]['title'].lower()

# sorts the titles (and entries) based on the type of query -- there are 4 types of queries available. 
def sort_function(sort_value, entries):
	sorts = [[None, False], [None, True], [get_title , False], [get_title, True] ] 
	return sorted(entries, key= sorts[sort_value][0], reverse= sorts[sort_value][1])

def main():
	database = Db(DB)
	entries_list = list(database.get_all_entries().items()) 
	titles = get_updated_titles(entries_list) #start of session titles
	sort_value = 0 
	sort_values = ["Oldest-Newest","Newest-Oldest","Alpha Numeric", "Reverse Alpha Numeric"] 

	layout = [
				[space(50,1), sg.Button('✕', key='-WIN-CLOSED-', size=(4,1), button_color=('black', 'white'), pad=(0, 0))], 
				[sort_banner(), button('New Sort', key='-CHANGE-SORT-', size=(15, 2), color='Navy Blue')], 
				[listbox(titles)], 
				[vertical_spacing(2)],
				[space(3, 1), button('New', '-NEW-'), space(5,1) , button('Browse', '-BROWSE-')], 
				[vertical_spacing(1)]]

	home_window = sg.Window('', layout, background_color=BG_COLOR, no_titlebar=True, grab_anywhere=True)
	cur_entry_num = 0
	#There is a bug if I do not have this here -- will inspect later
	updated_entries_list = sort_function( sort_value, list(database.get_all_entries().items()) )

	while 1:
		event, values = home_window.read() #we need a timeout so that we can update the newly added titles quickly 
		home_window['-SEARCH-RESULTS-'].block_focus(block=True)

		if event in (sg.WIN_CLOSED, '-WIN-CLOSED-'):
			break 
		
		elif event == '-CHANGE-SORT-':
			sort_value = (sort_value + 1)%len(sort_values)
			home_window['-SORT-VALUE-'].update(f'Sorted ({sort_values[sort_value]})')

		elif event=='-BROWSE-':

			if updated_entries_list: # We don't want the user to be able to browse the entries if there are none...

				n = len(updated_entries_list)
				browse_window = browse_entry_window(browse_entry_layout(cur_entry_num==0, cur_entry_num == n -1)).finalize()
				update_entry_window(browse_window, updated_entries_list, cur_entry_num, browse_window['-EDIT-'].metadata)
				
				while 1:
					browse_event, browse_values = browse_window.read()
					next_visible = None
					previous_visible = None
					

					if browse_event==sg.WIN_CLOSED:
						break

					elif browse_event == '-NEXT-':
						cur_entry_num = cur_entry_num +1 if cur_entry_num < n -1  else n -1 
						
					elif browse_event == '-PREVIOUS-': 
						cur_entry_num = cur_entry_num - 1 if cur_entry_num > 0 else 0

					elif browse_event == '-EDIT-':
						browse_window['-EDIT-'].metadata = not browse_window['-EDIT-'].metadata
						edit_mode = browse_window['-EDIT-'].metadata
						browse_window['-EDIT-'].update(
							text = "Done Editing" if edit_mode else "Edit",
							button_color = ('black', 'red') if edit_mode else ('black', 'orange')
														)
						if not browse_window['-EDIT-'].metadata: # we just made a change

							cur_entry = updated_entries_list[cur_entry_num]
							cur_entry_date = cur_entry[0]
							cur_entry_title = cur_entry[1]["title"]
							cur_entry_tags = cur_entry[1]["tags"]
							text_without_date = list(filter( lambda line: line not in (cur_entry_date, ''), browse_values['-TEXT-'].split("\n")) )
							cur_time_and_date = get_time_and_date()
							new_text = text_without_date
							new_text = "\n".join(new_text)
							database.delete(cur_entry_date) # deletes this from json file 
							database.write(cur_time_and_date, cur_entry_title, cur_entry_tags, new_text)

							updated_entries_list = sort_function( sort_value, list(database.get_all_entries().items()) ) # to view the changes made immediately
							titles = get_updated_titles(updated_entries_list)
							cur_entry_num = titles.index(cur_entry_title) # if not it will shuffle us along somewhere else in the entry list viewer
							# as it updated the index of the newly updated entry due to the sort function 
 

					next_visible = cur_entry_num < n -1 
					previous_visible = cur_entry_num > 0
					update_entry_window(browse_window, updated_entries_list, cur_entry_num, browse_window['-EDIT-'].metadata)
					next_button = browse_window['-NEXT-']
					previous_button = browse_window['-PREVIOUS-']
					next_button.update(disabled = not next_visible)
					previous_button.update(disabled = not previous_visible)


				browse_window.close()

			else:
				sg.popup("No entries to browse! Try making a new one :)")



		elif event =='-NEW-':

			entry_window = new_entry_window(new_entry_layout())

			while 1:
				entry_win_event, entry_win_values = entry_window.read()
				if entry_win_event in (sg.WIN_CLOSED, '-DONE-'):

					blank_text = '\n' # This is what will be in the text field if the user submits no text.
					tags = entry_win_values['-TAGS-']
					title = entry_win_values['-TITLE-']
					text = entry_win_values['-TEXT-']
					if text != blank_text and tags and title:

						entry_time_and_date = get_time_and_date()
						tags = tags.split(" ") #tags are spaced 
						database.write(entry_time_and_date, title, tags, text)

				break

			entry_window.close()



		elif event == '-SEARCH-RESULTS-': #searching

			if values['-SEARCH-RESULTS-']: # When the program is first booted without any entries we do not want the user to crash the program. 

				selected_title = values['-SEARCH-RESULTS-'][0] # every value of the listbox is a list of a single element
				cur_entry_num = titles.index(selected_title)

		# We want to update the listbox results after every event so that it updates in real time 
		updated_entries_list = sort_function( sort_value, list(database.get_all_entries().items()) )
		titles = get_updated_titles(updated_entries_list)

		home_window['-SEARCH-RESULTS-'].update(
			values = titles, 
			set_to_index=cur_entry_num,
			scroll_to_index = cur_entry_num if cur_entry_num > 10 else None,
			
											   )

		# print("entires list:", updated_entries_list)

	


	home_window.close()

if __name__ == '__main__':
	main()