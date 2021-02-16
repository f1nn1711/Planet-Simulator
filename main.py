#All the imports
import pygame
import math
import sys
from random import randint
from time import sleep
import traceback

#This is the class for a planet
class Planet():
	def __init__(self, x=0, y=0, name="Some Planet", radius=0, angle=0, orbital_dis=0, colour=(0,255,0),system=None,mass=0, center=None):
		self.x = x
		self.y = y
		self.name = name#The name to be displayed next to the planet
		self.radius = radius#Radius of the planet
		self.angle = angle#Angle from up to center to planet
		self.orbital_dis = round(orbital_dis)#Distance from center
		self.colour = colour#RGB colour code for the planet
		self.system = system#The solar system the planet is part of
		self.center = center#Another planet which this plant will orbit around
		self.mass = mass#The mass of this planet

		if self.orbital_dis > 0:#Checks to see if the orbital distance is greater than 0, if this was 0 then it will be the central planet for the solar system
			#This calculates the velocity that planet will need to orbit at for it to be able to remain in a constant orbit
			self.vel = math.sqrt(((6.673*(10**1))*center.mass)/self.orbital_dis)

		self.system.planets.append(self)#Adds this planet to the solar system
	
	#This updates the position of the planet
	def update_pos(self):
		circumference_change_ratio = (self.vel*self.system.time_scale)/(math.pi*(self.orbital_dis*2))#Calculates the ratio of the distance traveled around the orbit compared to the whole circumference
		
		self.angle += 360*circumference_change_ratio#Calculates the planets angle around the orbit

		new_x = math.cos(math.radians(self.angle))*self.orbital_dis#Calculates the new x coordinate for the planet 
		new_y = math.sin(math.radians(self.angle))*self.orbital_dis#Calculates the new y coordinate for the planet 

		self.x = new_x+self.center.x+self.center.radius#Sets the planets x coordinate to the new x coordinate
		self.y = new_y+self.center.y+self.center.radius#Sets the planets y coordinate to the new y coordinate

#Class for an on-screen button
class Button():
	def __init__(self, screen, x, y, width, height, text, text_colour=(255,255,0), box_colour=(255,0,0), function=None, item_type="button", id=None):
		self.screen = screen#Pygame screen object
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text#Text on the inside of the button
		self.text_colour = text_colour
		self.box_colour = box_colour
		self.function = function#A callable object that will be called when the button is clicked
		self.item_type = item_type
		self.id = id
	
	#Draws the button on the screen
	def render(self):
		pygame.draw.rect(self.screen, self.box_colour, (self.x, self.y, self.width, self.height))#Draws a rectangle

		font = pygame.font.SysFont("Ariel", 20)#Sets the font family and size
		text = font.render(self.text, True, self.text_colour)#Creates the text object
		text_rect = text.get_rect(center=(self.x+(self.width//2), self.y+(self.height//2)))#Creates a box for the next to go in
		screen.blit(text, text_rect)#Draws the text within the text box
	
	#Method that is called when the button is clicked
	def active(self):
		self.function()

#Class for an on-screen label
class Label():
	def __init__(self, screen, x, y, text, font="Ariel", font_size=20, colour=(255,255,255), item_type="label"):
		self.screen = screen#Pygame screen object
		self.x = x
		self.y = y
		self.text = text
		self.font = font
		self.font_size = font_size
		self.colour = colour
		self.item_type = item_type

	#Draws the label on the scree
	def render(self):
		font = pygame.font.SysFont(self.font, self.font_size)#Sets the font family and size
		text = font.render(self.text, True, self.colour)#Creates the text object
		screen.blit(text, (self.x,self.y))#Draws the text at the give (x,y) coordinates

class System():
	def __init__(self, target_fps, screen_width, screen_height, divider, stars, planets=[], zoom_level=1):
		self.target_fps = target_fps
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.divider = divider#The width of the sidebar on the right
		self.zoom_level = zoom_level
		self.stars = stars#This is a list which contains the data for the start generation, it is in the structure for [start width, start height, proportion of screen with stars on]
		self.time_scale = 1

		self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))#Pygame screen object with a given width and height
		self.clock = pygame.time.Clock()#A pygame clock object which will control the frame rate of the simulation

		self.planets = planets#A list which contains all of the planets in the system
		self.selected_planet = None#What planet has been clicked on
		self.place_mode = False#Does the user want to add another planet
		self.new_planet_size = 10#Inital size for a new planet

		self.new_name = ""#Variable to store the name of a planet which is being changed
		self.edit_mode = False#Is the user currently changing a planets name

		self.running = True#Is mainloop running
		self.paused = False#Is the simulation paused

		self.genrate_stars()#Calls the function to generate all the stars

	#This function creates a 2D list containing the [x,y] coordinates of each start
	def genrate_stars(self):
		area_to_be_covered = (self.screen_width*self.screen_height)*self.stars[2]#Calculates how much of the screen needs to be covered in stars (in pixels)
		number_stars = round(area_to_be_covered/(self.stars[0]*self.stars[1]))#The number of stars required

		self.star_coords = []#New blank list for the stars to be stored in

		for n in range(number_stars):#Ittrates for the number of stars needed
			self.star_coords.append([randint(0,self.screen_width),randint(0,self.screen_height)])#Generates a random x and y coordinate and adds it to the list of starts

	#Calculates how the x and y coordinates have changed bassed on how zoomed in/out the user is
	def zoom_shift(self, x, y, w, h):
		cx = x + (w/2)#Since the given (x,y) coordinates are for the top left corner this finds the coordinates for the center of the shape
		cy = y + (h/2)

		dx = cx - self.planets[0].x#Calculates the difference between the center of the shape and the center of the central planet(which is the the center of zoom)
		dy = cy - self.planets[0].y

		new_dx = dx * self.zoom_level#Calculates the new difference between the center of the shape and central planet by multiplying the original distance by the zoom level
		new_dy = dy * self.zoom_level

		fx = self.planets[0].x+new_dx+(w/2)#Calculates the new top left hand corner coordinate for to now zoomed in shape
		fy = self.planets[0].y+new_dy+(h/2)

		return fx, fy#Returns the new coordinates
	
	#Function to remove a planet from the system
	def remove_planet(self):
		for planet in self.planets:#Itterates through all the planets currently in the system
			if planet.center == self.selected_planet:#If the planets center planet (in which it orbits around) is the same as the selected planet
				print("Other planets are orbitting this planet so it can't be deleted.")
				return#Returns from the function without deleting any planet
		
		self.planets.remove(self.selected_planet)#Removes the selected planet from the list of planets in the system
		self.selected_planet = None#Makes no planet selected
		
	#Function to toggle if the user is adding a planet
	def add_planet(self):
		if self.place_mode:#If the user is currently adding a planet
			self.place_mode = False#Cancel adding a planet
		else:#If they aren't adding a planet
			self.place_mode = True#Set the user wanting to add a planet to true

	#Function that toggles whether the simulation is paused
	def toggle_pause(self):
		if not self.paused:
			self.paused = True
		else:
			self.paused = False

	#Function that cancels any planet being selected
	def cancel_selected_planet(self):
		self.selected_planet = None

	#Function that increases the time multiplier
	def speed_up_time(self):
		self.time_scale += 0.25

	#Function that resets the time multiplier to the default of 1
	def reset_time(self):
		self.time_scale = 1

	#Function that decreases the time multiplier
	def slow_down_time(self):
		if self.time_scale > 0:
			self.time_scale -= 0.25

	#Function that enteres the user in to the mode where they can edit a planets name
	def set_to_edit_name(self):
		self.edit_mode = True#Sets the name editting mode to true
		self.new_name = self.selected_planet.name#Sets the new name of the planet to the current name of the planet

	#Function that cancels the edit of a planets name
	def cancel_edit_name(self):
		self.new_name = ""#Resets the new name of a planet
		self.edit_mode = False#Exits the name editing mode
	
	#Function that resets the zoom level to the default of 1
	def reset_zoom(self):
		self.zoom_level = 1

	#Function that increases the red RBG value of a planet
	def add_red(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[0]+5 <= 255:#If the current red RGB value plus 5 is less than 255
			l_colours[0] += 5#Add 5 to the red value
		else:
			l_colours[0] = 255#Set the red value to 255

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it
		
	#Function that decreases the red RBG value of a planet
	def rem_red(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[0]-5 >= 0:#If the current red RGB value subtract 5 is greater than 0
			l_colours[0] -= 5#Subtracts 5 from the red value
		else:
			l_colours[0] = 0#Set the red value to 0

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it
		
	#Function that increases the green RBG value of a planet
	def add_green(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[1]+5 <= 255:#If the current green RGB value plus 5 is less than 255
			l_colours[1] += 5#Add 5 to the green value
		else:
			l_colours[1] = 255#Sets the green value to 255

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it

	#Function that decreases the green RBG value of a planet
	def rem_green(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[1]-5 >= 0:#If the current green RGB value subtract 5 is greater than 0
			l_colours[1] -= 5#Subtracts 5 from the green value
		else:
			l_colours[1] = 0#Sets the green value to 0

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it

	#Function that increases the blue RBG value of a planet
	def add_blue(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[2]+5 <= 255:#If the current blue RGB value plus 5 is less than 255
			l_colours[2] += 5#Add 5 to the blue value
		else:
			l_colours[2] = 255#Sets the blue value to 255

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it

	#Function that decreases the blue RBG value of a planet
	def rem_blue(self):
		l_colours = list(self.selected_planet.colour)#Converts the RGB tuple in to a list

		if self.selected_planet.colour[2]-5 >= 0:#If the current blue RGB value subtract 5 is greater than 0
			l_colours[2] -= 5#Subtracts 5 from the blue value
		else:
			l_colours[2] = 0#Sets the blue value to 0

		self.selected_planet.colour = tuple(l_colours)#Convert the list of colour values back in to a tuple and set the planets colour to it

	def run(self):
		#Sets the target frame rate of the simulation
		self.clock.tick(self.target_fps)

		#Itterates through all the events that have happend in the frame
		for event in pygame.event.get():
			#Quit the program if the user clicks the 'X'
			if event.type == pygame.QUIT:
				sys.exit()

			#If a mouse button was pressed
			if event.type == pygame.MOUSEBUTTONDOWN:
				#If the user scrolls up
				if event.button == 5:
					#If the current zoom level plus 0.1 is less than or equal to 10
					if self.zoom_level+0.1 <= 10:
						self.zoom_level += 0.1#Adds 0.1 to the zoom level
				#If the user scrolls down
				elif event.button == 4:
					#If the current zoom level subracts 0.1 is greater than or equal to 0
					if self.zoom_level-0.1 >= 0:
						self.zoom_level -= 0.1#Subtracts 0.1 from the zoom level

				#If the LMB is clicked
				elif event.button == 1:
					#Get the x and y coordinates of the mouse
					mouse_x, mouse_y = pygame.mouse.get_pos()
					
					#Has the user clicked on a button, by default this is set to false
					selected_button = False
					
					#Itterates through all of the items such as buttons that are on the scree
					for item in self.items:
						#If that item is a button
						if item.item_type == "button":
							#If the mouse x and y is within the bounding box of the button
							if mouse_x >= item.x and mouse_x <= item.x+item.width and mouse_y >= item.y and mouse_y <= item.y+item.height:
								#Then selected button is true because they have clicked on a button
								selected_button = True
								#Call the function associated with that button
								item.function()
								
					#If the user hasn't clicked a button
					if not selected_button:
						#Itterates through all of the planets
						for p in self.planets:
							#If the distance between the mouse coordinates is less than the radius of the planet
							if math.sqrt((abs(mouse_x-(p.x+p.radius))**2)+(abs(mouse_y-(p.y+p.radius))**2)) <= p.radius*self.zoom_level:
								#Sets the selected planet to the planet the user has clicked on
								self.selected_planet = p
								#Breaks out the loop meaning no more planets will be checked
								break
							
							#If no planet is clicked on then the selected planet is set to false
							self.selected_planet = None
							#It will cancel the edit of any planets name
							cancel_edit_name()

			#If a key is pressed and the user is in name edit mode
			if event.type == pygame.KEYDOWN and self.edit_mode:
				#Try to get the ascii code for the entered key
				try:
					entered_ascii_code = ord(event.unicode)
				except:
					#If the ascii code doesnt exist for the pressed key then it set to -1
					entered_ascii_code = -1
				
				#If the entered letter is in the alphabet
				if isalpha(event.unicode):
					#Add that letter to the new name
					self.new_name += event.unicode
				#If the ascii code is equal to 32 then the spacebar has been pressed
				elif entered_ascii_code == 32:
					#Add a space to the new name
					self.new_name = self.new_name + " "
				#If the user pressed the backspace key
				elif event.key == pygame.K_BACKSPACE:
					#Slice the new name to exclude the last character of the new name
					self.new_name = self.new_name[:-1]
					
				#Set the planets name to the new name
				self.selected_planet.name = self.new_name

		#Gets all the keys which pressed
		keys = pygame.key.get_pressed()
		
		#If the user is in name edit mode and they havent pressed escape
		if self.edit_mode and not keys[pygame.K_ESCAPE]:
			#Cancel all the keys which are pressed as to not interfer with the new name
			keys = []
		#If the user presses the escape key
		elif keys[pygame.K_ESCAPE]:
			#Exit out of name edit mode
			cancel_edit_name()
		#If the user presses the up key and they are placing a new planet
		elif keys[pygame.K_UP] and self.place_mode:
			#Increse the the size of the new planet
			self.new_planet_size += 1
		
		#If the user presses the down arrow key and they are placing a new planet
		elif keys[pygame.K_DOWN] and self.place_mode:
			#Decrease the the size of the new planet
			self.new_planet_size -= 1

		#If the user is placing a new planet and they press the enter/return key
		elif self.place_mode and keys[pygame.K_RETURN]:
			#Get the position of the mouse
			mouse_x, mouse_y = pygame.mouse.get_pos()
			
			#Get the position of the central planet
			center_planet_x = self.planets[0].x
			center_planet_y = self.planets[0].y
			
			#Get the difference between the mouse position and the central planet
			x_diff = (mouse_x-center_planet_x)
			y_diff = (mouse_y-center_planet_y)
			
			#Calulate the angle between the mouse position and the central planet
			angle = math.degrees(math.atan(y_diff/x_diff))
			
			#If the mouse is on the left hand side of the screen
			if mouse_x < center_planet_x:
				#Add 180 degrees to the angle
				angle += 180
			
			#Create a new planet
			new_p = Planet(x=mouse_x,y=mouse_y,radius=self.new_planet_size/self.zoom_level,angle=angle,orbital_dis=(math.sqrt(((abs(mouse_x-self.planets[0].x)**2)+(abs(mouse_y-self.planets[0].y)**2))))/self.zoom_level,colour=(0,0,255),center=self.planets[0],system=self)
			#Exit out of placing an new planet mode
			self.place_mode = False

		#Clears the screen so its blank before being drawn on
		self.screen.fill((0,0,0))

		#Itterates through all of the stars
		for star in self.star_coords:
			#Draw a rectangle the size of the star at the location of that star
			pygame.draw.rect(self.screen, (255,255,255), (star[0], star[1], self.stars[0], self.stars[1]))

		#Ff the user is in place mode
		if self.place_mode:
			#Get the mouse position
			mouse_x, mouse_y = pygame.mouse.get_pos()
			#Draw an empty circle at the location of the mouse with the size of the new planet
			pygame.draw.circle(self.screen, (255,255,255), (mouse_x, mouse_y), self.new_planet_size, 2)

		#Enumerates through all the planets
		for n, p in enumerate(self.planets):
			#If the simulation isn't paused and it isn't the the first planet as this is the central planet
			if not self.paused and n != 0:
				#Update the the position of the planet
				p.update_pos()
			
			#If the planet is selected
			if p == self.selected_planet:
				#Make the text lable red
				textsurface = font.render(p.name, True, (255, 0, 0))
			else:
				#If it isnt selected make the text white
				textsurface = font.render(p.name, True, (255, 255, 255))

			#Calculate the position of the planet after the zoom level has been taken in to account
			adj_x, adj_y = self.zoom_shift(p.x, p.y, p.radius, p.radius)
	
			#Draw the planet label
			screen.blit(textsurface,(int(adj_x),int(adj_y-(24+(p.radius*self.zoom_level)))))
			#Draw the Planet
			pygame.draw.circle(self.screen, p.colour, (round(adj_x), round(adj_y)), p.radius*self.zoom_level)
		
		#Create an empty list where the items will be stored, an item is a button or a label
		self.items = []

		#If a planet is selected
		if self.selected_planet:
			#Add a button to cancel the planet celection
			self.items.append(Button(self.screen, 1020,20,100,25,"Cancel",box_colour=(255,0,0),text_colour=(0,0,0),function=self.cancel_selected_planet))
			#Add a button to delete the planet
			self.items.append(Button(self.screen, 1020,50,100,25,"Remove",function=self.remove_planet))
			
			#If the user isnt in edit mode
			if not self.edit_mode:
				#Add a button to enter name edit mode
				self.items.append(Button(self.screen, 1020,80,100,25,"Edit Name",function=self.set_to_edit_name))
			else:
				#Add a button to exit out of name edit mode
				self.items.append(Button(self.screen, 1020,80,125,25,"Save (Esc)",function=self.cancel_edit_name))


			#Add a label
			self.items.append(Label(self.screen, 1020, 110, f"Control the RGB values", font_size=24))
			
			#Add a label along with a + and - button to alter the red RGB value
			self.items.append(Button(self.screen, 1020,140,30,25,"-",box_colour=(255,0,0),text_colour=(0,0,0),function=self.rem_red))
			self.items.append(Label(self.screen, 1055, 145, f"Red: {self.selected_planet.colour[0]}", font_size=24))
			self.items.append(Button(self.screen, 1140,140,30,25,"+",box_colour=(255,0,0),text_colour=(0,0,0),function=self.add_red))

			#Add a label along with a + and - button to alter the green RGB value
			self.items.append(Button(self.screen, 1020,170,30,25,"-",box_colour=(0,255,0),text_colour=(0,0,0),function=self.rem_green))
			self.items.append(Label(self.screen, 1055, 175, f"Green: {self.selected_planet.colour[1]}", font_size=24))
			self.items.append(Button(self.screen, 1140,170,30,25,"+",box_colour=(0,255,0),text_colour=(0,0,0),function=self.add_green))

			#Add a label along with a + and - button to alter the blue RGB value
			self.items.append(Button(self.screen, 1020,200,30,25,"-",box_colour=(0,0,255),text_colour=(0,0,0),function=self.rem_blue))
			self.items.append(Label(self.screen, 1055, 205, f"Blue: {self.selected_planet.colour[2]}", font_size=24))
			self.items.append(Button(self.screen, 1140,200,30,25,"+",box_colour=(0,0,255),text_colour=(0,0,0),function=self.add_blue))
			
			#Add a label to display the name of the planet and the distance from the planet it orbits around
			self.items.append(Label(self.screen, 1020, 230, f"Planet Name: {self.selected_planet.name}", font_size=24))
			self.items.append(Label(self.screen, 1020, 250, f"Orbital Distance: {self.selected_planet.orbital_dis}", font_size=24))

			#If the user is in name edit mode
			if self.edit_mode:
				#Add labels to explain what to do
				self.items.append(Label(self.screen, 1020, 270, f"Start typing or press backspace to", font_size=24))
				self.items.append(Label(self.screen, 1020, 290, f"delete current text. Once you have", font_size=24))
				self.items.append(Label(self.screen, 1020, 310, f"finished typing click 'Save (Esc)'.", font_size=24))
				
		#If they are in place mode
		elif self.place_mode:
			#Add a button to exit place mode
			self.items.append(Button(self.screen, 1020,20,125,25,"Cancel",box_colour=(255,0,0),text_colour=(0,0,0),function=self.add_planet))
			#Add labels to explain what to do
			self.items.append(Label(self.screen, 1020, 60, f"Press ENTER to confirm planets location", font_size=20))
			self.items.append(Label(self.screen, 1020, 80, f"Press UP to increase the planets size", font_size=20))
			self.items.append(Label(self.screen, 1020, 100, f"Press DOWN to decrease the planets size", font_size=20))
		
		#If no planet is selcted and the user isnt in place mode
		else:
			#If the simulation isnt paused
			if self.paused == False:
				#Add a pause button
				self.items.append(Button(self.screen, 1020,20,125,25,"Pause",box_colour=(255,0,0),text_colour=(0,0,0),function=self.toggle_pause))
			#If the simulation is paused
			else:
				#Add a play button
				self.items.append(Button(self.screen, 1020,20,125,25,"Play",box_colour=(0,255,0),text_colour=(0,0,0),function=self.toggle_pause))
			
			#Add a button to enter place mode
			self.items.append(Button(self.screen, 1020,50,125,25,"Add Planet",box_colour=(0,255,0),text_colour=(0,0,0),function=self.add_planet))

			#Add button to control the rate of time
			self.items.append(Button(self.screen, 1020,100,125,25,"Speed Up Time",box_colour=(0,255,0),text_colour=(0,0,0),function=self.speed_up_time))
			self.items.append(Button(self.screen, 1020,130,125,25,"Reset Time",box_colour=(255,191,0),text_colour=(0,0,0),function=self.reset_time))
			self.items.append(Button(self.screen, 1020,160,125,25,"Slow Down Time",box_colour=(255,0,0),text_colour=(0,0,0),function=self.slow_down_time))

			#Add a button to reset the zoom level
			self.items.append(Button(self.screen, 1020,210,125,25,"Reset Zoom",box_colour=(255,191,0),text_colour=(0,0,0),function=self.reset_zoom))

			#Add labels to explain what the user can do
			self.items.append(Label(self.screen, 1020, 250, f"Press a planet to edit it or just", font_size=25))
			self.items.append(Label(self.screen, 1020, 270, f"watch the world go by!", font_size=25))

			#Add a quit button
			self.items.append(Button(self.screen, 1020,SCREEN_HEIGHT-30,125,25,"Quit",box_colour=(255,0,0),text_colour=(0,0,0),function=sys.exit))

		#Drawing the side bar on the right
		pygame.draw.rect(self.screen, (0,0,0), (self.screen_width-self.divider, 0, self.divider, self.screen_height))
		pygame.draw.rect(self.screen, (255,0,0), (self.screen_width-self.divider, 0, 2, self.screen_height))

		#Itterates through all of the items in the list
		for item in self.items:
			#Draws that item
			item.render()

		#Displays all the stats in the upper left
		screen.blit(small_font.render(f"Target FPS: {self.target_fps}", True, (255, 255, 255)),(0,0))
		screen.blit(small_font.render(f"Actual FPS: {round(self.clock.get_fps(),2)}", True, (255, 255, 255)),(0,20))
		screen.blit(small_font.render(f"Running At: {round((self.clock.get_fps()/self.target_fps)*100,1)}%", True, (255, 255, 255)),(0,40))
		screen.blit(small_font.render(f"Speed: {self.time_scale}x", True, (255, 255, 255)),(0,60))

		#Saves this frames keys
		self.prev_keys = keys
		#Updates the pygame window
		pygame.display.update()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

#Initializes the pygame module
pygame.init()
#Create the pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#Initialize the pygame text engine
pygame.font.init()

#Create the default fonts and sizes
font = pygame.font.SysFont('Ariel', 24)
small_font = pygame.font.SysFont('Ariel', 26)

#Create a system object
system = System(target_fps=60,screen_width=1300,screen_height=750,divider=300,stars=[2,2,0.001])

#Creat the different planets
center_planet = Planet(x=SCREEN_WIDTH//2,y=SCREEN_HEIGHT//2,name="Sun",radius=30,colour=(255,255,255),mass=1*10^6,system=system)
mercury = Planet(x=SCREEN_WIDTH//2,y=100,name="Mercury",radius=10,orbital_dis=100,colour=(255,0,0),center=center_planet,system=system)
venus = Planet(x=SCREEN_WIDTH//2,y=150,name="Venus",radius=10,orbital_dis=150,colour=(0,255,0),center=center_planet,system=system)
earth = Planet(x=SCREEN_WIDTH//2,y=200,name="Earth",radius=10,orbital_dis=200,colour=(0,0,255),center=center_planet,system=system,mass=1*10^8)
moon = Planet(x=SCREEN_WIDTH//2,y=250,name="Moon",radius=5,orbital_dis=50,colour=(0,0,255),center=earth,system=system)
mars = Planet(x=SCREEN_WIDTH//2,y=300,name="Mars",radius=10,orbital_dis=300,colour=(0,255,255),center=center_planet,system=system)

#Main
if __name__ == '__main__':
	#Try to run the simulation
	try:
		while system.running:
			system.run()
	#If a exception occurs
	except Exception as e:
		#Print the exception traceback
		print(traceback.format_exc())
		#Wait for 10 seconds so the console doesnt immediatly close
		sleep(10)
