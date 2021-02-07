import pygame
import math
import sys
from random import randint
from time import sleep
import traceback

class Planet():
	def __init__(self, x=0, y=0, name="Some Planet", radius=0, angle=0, orbital_dis=0, colour=(0,255,0),system=None,mass=0, center=None):
		self.x = x
		self.y = y
		self.name = name
		self.radius = radius#radius of the planet
		self.angle = angle#angle from up to center to planet
		self.orbital_dis = round(orbital_dis)#distance from center
		self.colour = colour#pretty self explanatory RGB
		self.system = system#the system the planet is part of
		self.center = center#the center for the planets orbit
		self.mass = mass#the mass of the plaet

		if self.orbital_dis > 0:#checks to see if the orbital distance is greater than 0
			'''
			This is the code which calculates the velocity the planet will need to travel
			in order to stay in orbit around the center planet
			'''
			self.vel = math.sqrt(((6.673*(10**1))*center.mass)/self.orbital_dis)#6.673

		self.system.planets.append(self)#adds the planet to the system

	def update_pos(self):
		circumference_change_ratio = (self.vel*self.system.time_scale)/(math.pi*(self.orbital_dis*2))#calculates the ratio of the distance traveled compared to the whole circumference
		self.angle += 360*circumference_change_ratio#calculates the angle around its orbut

		x_change = math.cos(math.radians(self.angle))*self.orbital_dis
		y_change = math.sin(math.radians(self.angle))*self.orbital_dis

		self.x = x_change+self.center.x+self.center.radius
		self.y = y_change+self.center.y+self.center.radius

class Button():
	def __init__(self, screen, x, y, width, height, text, text_colour=(255,255,0), box_colour=(255,0,0), function=None, item_type="button", id=None):
		self.screen = screen#pygame screen object
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text
		self.text_colour = text_colour
		self.box_colour = box_colour
		self.function = function
		self.item_type = item_type
		self.id = id

	def render(self):
		pygame.draw.rect(self.screen, self.box_colour, (self.x, self.y, self.width, self.height))

		font = pygame.font.SysFont("Ariel", 20)
		text = font.render(self.text, True, self.text_colour)
		text_rect = text.get_rect(center=(self.x+(self.width//2), self.y+(self.height//2)))
		screen.blit(text, text_rect)

	def active(self):
		self.function()

class Label():
	def __init__(self, screen, x, y, text, font="Ariel", font_size=20, colour=(255,255,255), item_type="label"):
		self.screen = screen
		self.x = x
		self.y = y
		self.text = text
		self.font = font
		self.font_size = font_size
		self.colour = colour
		self.item_type = item_type

	def render(self):
		font = pygame.font.SysFont(self.font, self.font_size)
		screen.blit(font.render(self.text, True, self.colour),(self.x,self.y))

class System():
	def __init__(self, target_fps, screen_width, screen_height, divider, stars, planets=[], zoom_level=1):
		self.target_fps = target_fps
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.divider = divider
		self.zoom_level = zoom_level
		self.stars = stars
		self.time_scale = 1

		self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
		self.clock = pygame.time.Clock()

		self.planets = planets
		self.selected_planet = None
		self.place_mode = False
		self.new_planet_size = 10

		self.menu_status = 0

		self.new_name = ""
		self.edit_mode = False

		self.running = True
		self.paused = False

		self.genrate_stars()

	def genrate_stars(self):
		area_to_be_covered = (self.screen_width*self.screen_height)*self.stars[2]
		number_stars = round(area_to_be_covered/(self.stars[0]*self.stars[1]))

		self.star_coords = []

		for n in range(number_stars):
			self.star_coords.append([randint(0,self.screen_width),randint(0,self.screen_height)])

	def zoom_shift(self, x, y, w, h):
		cx = x + (w/2)
		cy = y + (h/2)

		dx = cx - self.planets[0].x
		dy = cy - self.planets[0].y

		new_dx = dx * self.zoom_level
		new_dy = dy * self.zoom_level

		fx = self.planets[0].x+new_dx+(w/2)
		fy = self.planets[0].y+new_dy+(h/2)

		return fx, fy

	def remove_planet(self):
		for planet in self.planets:
			if planet.center == self.selected_planet:
				print("Other planets are orbitting this planet so it can't be deleted.")
				return

		self.planets.remove(self.selected_planet)
		self.selected_planet = None

	def add_planet(self):
		if not self.prev_keys[pygame.K_d]:
			if not self.place_mode:
				self.place_mode = True
			else:
				self.place_mode = False

	def toggle_pause(self):
		if not self.paused:
			self.paused = True
		else:
			self.paused = False

	def cancel_selected_planet(self):
		self.selected_planet = None

	def speed_up_time(self):
		self.time_scale += 0.25

	def reset_time(self):
		self.time_scale = 1

	def slow_down_time(self):
		if self.time_scale > 0:
			self.time_scale -= 0.25

	def set_to_edit_name(self):
		self.edit_mode = True
		self.new_name = self.selected_planet.name

	def cancel_edit_name(self):
		self.new_name = ""
		self.edit_mode = False

	def reset_zoom(self):
		self.zoom_level = 1

	def add_red(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[0]+5 <= 255:
			l_colours[0] += 5
		else:
			l_colours[0] = 255

		self.selected_planet.colour = tuple(l_colours)

	def rem_red(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[0]-5 >= 0:
			l_colours[0] -= 5
		else:
			l_colours[0] = 0

		self.selected_planet.colour = tuple(l_colours)

	def add_green(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[1]+5 <= 255:
			l_colours[1] += 5
		else:
			l_colours[1] = 255

		self.selected_planet.colour = tuple(l_colours)

	def rem_green(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[1]-5 >= 0:
			l_colours[1] -= 5
		else:
			l_colours[1] = 0

		self.selected_planet.colour = tuple(l_colours)

	def add_blue(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[2]+5 <= 255:
			l_colours[2] += 5
		else:
			l_colours[2] = 255

		self.selected_planet.colour = tuple(l_colours)

	def rem_blue(self):
		l_colours = list(self.selected_planet.colour)

		if self.selected_planet.colour[2]-5 >= 0:
			l_colours[2] -= 5
		else:
			l_colours[2] = 0

		self.selected_planet.colour = tuple(l_colours)

	def run(self):
		#controls the frame rate of the game
		self.clock.tick(self.target_fps)

		#loops through all the events that have happend in the frame
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			#detects if a mouse button was pressed
			if event.type == pygame.MOUSEBUTTONDOWN:
				#edits the zoom level WIP
				if event.button == 5:
					if self.zoom_level+0.1 <= 10:
						self.zoom_level += 0.1
				elif event.button == 4:
					if self.zoom_level-0.1 >= 0:
						self.zoom_level -= 0.1

				#if LMB then it checks to see if user clicked on planet
				elif event.button == 1:
					mouse_x, mouse_y = pygame.mouse.get_pos()

					selected_button = False

					for item in self.items:
						if item.item_type == "button":
							if mouse_x >= item.x and mouse_x <= item.x+item.width and mouse_y >= item.y and mouse_y <= item.y+item.height:
								selected_button = True
								item.function()

					if not selected_button:
						for p in self.planets:
							if math.sqrt((abs(mouse_x-(p.x+p.radius))**2)+(abs(mouse_y-(p.y+p.radius))**2)) <= p.radius*self.zoom_level:
								self.selected_planet = p
								break

							self.selected_planet = None
							self.new_name = ""
							self.edit_mode = False

			#detects any key pressed down and the user is editing a name
			if event.type == pygame.KEYDOWN and self.edit_mode:
				try:
					entered_ascii_code = ord(event.unicode)
				except:
					entered_ascii_code = -1

				if event.unicode.lower() in accepted_chars:
					self.new_name += event.unicode
					self.selected_planet.name = self.new_name
				elif entered_ascii_code == 32:
					self.new_name = self.new_name + " "
				elif event.key == pygame.K_BACKSPACE:
					self.new_name = self.new_name[:-1]
					self.selected_planet.name = self.new_name

		#gets all the keys which are currently being pressed
		keys = pygame.key.get_pressed()

		if self.edit_mode and not keys[pygame.K_ESCAPE]:
			keys = []
		elif keys[pygame.K_ESCAPE]:
			self.edit_mode = False
			self.new_name = ""

		elif keys[pygame.K_UP]:
			if self.place_mode:
				self.new_planet_size += 1

		elif keys[pygame.K_DOWN]:
			if self.place_mode:
				self.new_planet_size -= 1

		elif self.place_mode and keys[pygame.K_RETURN]:
			mouse_x, mouse_y = pygame.mouse.get_pos()

			center_planet_x = self.planets[0].x
			center_planet_y = self.planets[0].y

			x_diff = (mouse_x-center_planet_x)
			y_diff = (mouse_y-center_planet_y)

			angle = math.degrees(math.atan(y_diff/x_diff))
			if mouse_x < center_planet_x:
				angle += 180

			new_p = Planet(x=mouse_x,y=mouse_y,radius=self.new_planet_size/self.zoom_level,angle=angle,orbital_dis=(math.sqrt(((abs(mouse_x-self.planets[0].x)**2)+(abs(mouse_y-self.planets[0].y)**2))))/self.zoom_level,colour=(0,0,255),center=self.planets[0],system=self)
			self.place_mode = False

		#Clears the screen so its blank before being drawn on
		self.screen.fill((0,0,0))

		#draws the stars
		for star in self.star_coords:
			pygame.draw.rect(self.screen, (255,255,255), (star[0], star[1], self.stars[0], self.stars[1]))

		#if the user is in place mode it draws the planet template
		if self.place_mode:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			pygame.draw.circle(self.screen, (255,255,255), (mouse_x, mouse_y), self.new_planet_size, 2)

		#enumerates through all the planets
		#draws the planet and the relevant text
		for n, p in enumerate(self.planets):
			if not self.paused and n != 0:
				p.update_pos()

			if p == self.selected_planet:
				textsurface = font.render(p.name, True, (255, 0, 0))
			else:
				textsurface = font.render(p.name, True, (255, 255, 255))

			adj_x, adj_y = self.zoom_shift(p.x, p.y, p.radius, p.radius)


			screen.blit(textsurface,(int(adj_x),int(adj_y-(24+(p.radius*self.zoom_level)))))

			pygame.draw.circle(self.screen, p.colour, (round(adj_x), round(adj_y)), p.radius*self.zoom_level)

		self.items = []

		#Choosing what elements should be drawn on the sidebar/menu
		if self.selected_planet:
			self.items.append(Button(self.screen, 1020,20,100,25,"Cancel",box_colour=(255,0,0),text_colour=(0,0,0),function=self.cancel_selected_planet))
			self.items.append(Button(self.screen, 1020,50,100,25,"Remove",function=self.remove_planet))
			if not self.edit_mode:
				self.items.append(Button(self.screen, 1020,80,100,25,"Edit Name",function=self.set_to_edit_name))
			else:
				self.items.append(Button(self.screen, 1020,80,125,25,"Save (Esc)",function=self.cancel_edit_name))


			#Add buttons to alter colour
			self.items.append(Label(self.screen, 1020, 110, f"Control the RGB values", font_size=24))
			#Red
			self.items.append(Button(self.screen, 1020,140,30,25,"-",box_colour=(255,0,0),text_colour=(0,0,0),function=self.rem_red))
			self.items.append(Label(self.screen, 1055, 145, f"Red: {self.selected_planet.colour[0]}", font_size=24))
			self.items.append(Button(self.screen, 1140,140,30,25,"+",box_colour=(255,0,0),text_colour=(0,0,0),function=self.add_red))

			#Green
			self.items.append(Button(self.screen, 1020,170,30,25,"-",box_colour=(0,255,0),text_colour=(0,0,0),function=self.rem_green))
			self.items.append(Label(self.screen, 1055, 175, f"Green: {self.selected_planet.colour[1]}", font_size=24))
			self.items.append(Button(self.screen, 1140,170,30,25,"+",box_colour=(0,255,0),text_colour=(0,0,0),function=self.add_green))

			#Blue
			self.items.append(Button(self.screen, 1020,200,30,25,"-",box_colour=(0,0,255),text_colour=(0,0,0),function=self.rem_blue))
			self.items.append(Label(self.screen, 1055, 205, f"Blue: {self.selected_planet.colour[2]}", font_size=24))
			self.items.append(Button(self.screen, 1140,200,30,25,"+",box_colour=(0,0,255),text_colour=(0,0,0),function=self.add_blue))
			

			self.items.append(Label(self.screen, 1020, 230, f"Planet Name: {self.selected_planet.name}", font_size=24))
			self.items.append(Label(self.screen, 1020, 250, f"Orbital Distance: {self.selected_planet.orbital_dis}", font_size=24))

			if self.edit_mode:
				self.items.append(Label(self.screen, 1020, 270, f"Start typing or press backspace to", font_size=24))
				self.items.append(Label(self.screen, 1020, 290, f"delete current text. Once you have", font_size=24))
				self.items.append(Label(self.screen, 1020, 310, f"finished typing click 'Save (Esc)'.", font_size=24))

			self.menu_status = 1
		elif self.place_mode:
			self.items.append(Button(self.screen, 1020,20,125,25,"Cancel",box_colour=(255,0,0),text_colour=(0,0,0),function=self.add_planet))
			self.items.append(Label(self.screen, 1020, 60, f"Press ENTER to confirm planets location", font_size=20))
			self.items.append(Label(self.screen, 1020, 80, f"Press UP to increase the planets size", font_size=20))
			self.items.append(Label(self.screen, 1020, 100, f"Press DOWN to decrease the planets size", font_size=20))
		else:
			if self.paused == False:
				self.items.append(Button(self.screen, 1020,20,125,25,"Pause",box_colour=(255,0,0),text_colour=(0,0,0),function=self.toggle_pause))
			else:
				self.items.append(Button(self.screen, 1020,20,125,25,"Play",box_colour=(0,255,0),text_colour=(0,0,0),function=self.toggle_pause))

			self.items.append(Button(self.screen, 1020,50,125,25,"Add Planet",box_colour=(0,255,0),text_colour=(0,0,0),function=self.add_planet))

			self.items.append(Button(self.screen, 1020,100,125,25,"Speed Up Time",box_colour=(0,255,0),text_colour=(0,0,0),function=self.speed_up_time))
			self.items.append(Button(self.screen, 1020,130,125,25,"Reset Time",box_colour=(255,191,0),text_colour=(0,0,0),function=self.reset_time))
			self.items.append(Button(self.screen, 1020,160,125,25,"Slow Down Time",box_colour=(255,0,0),text_colour=(0,0,0),function=self.slow_down_time))

			self.items.append(Button(self.screen, 1020,210,125,25,"Reset Zoom",box_colour=(255,191,0),text_colour=(0,0,0),function=self.reset_zoom))

			self.items.append(Label(self.screen, 1020, 250, f"Press a planet to edit it or just", font_size=25))
			self.items.append(Label(self.screen, 1020, 270, f"watch the world go by!", font_size=25))

			self.items.append(Button(self.screen, 1020,SCREEN_HEIGHT-30,125,25,"Quit",box_colour=(255,0,0),text_colour=(0,0,0),function=sys.exit))

		#Drawing the panel on the left
		pygame.draw.rect(self.screen, (0,0,0), (self.screen_width-self.divider, 0, self.divider, self.screen_height))
		pygame.draw.rect(self.screen, (255,0,0), (self.screen_width-self.divider, 0, 2, self.screen_height))

		#Displays all of the items for the menu
		for item in self.items:
			item.render()

		#Displays all the stats in the upper left
		screen.blit(small_font.render(f"Target FPS: {self.target_fps}", True, (255, 255, 255)),(0,0))
		screen.blit(small_font.render(f"Actual FPS: {round(self.clock.get_fps(),2)}", True, (255, 255, 255)),(0,20))
		screen.blit(small_font.render(f"Running At: {round((self.clock.get_fps()/self.target_fps)*100,1)}%", True, (255, 255, 255)),(0,40))
		screen.blit(small_font.render(f"Speed: {self.time_scale}x", True, (255, 255, 255)),(0,60))

		#saves this cycles keys and updates the pygame window
		self.prev_keys = keys
		pygame.display.update()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()

font = pygame.font.SysFont('Ariel', 24)
small_font = pygame.font.SysFont('Ariel', 26)

system = System(target_fps=60,screen_width=1300,screen_height=750,divider=300,stars=[2,2,0.001])

center_planet = Planet(x=SCREEN_WIDTH//2,y=SCREEN_HEIGHT//2,name="Sun",radius=30,colour=(255,255,255),mass=1*10^6,system=system)
mercury = Planet(x=SCREEN_WIDTH//2,y=100,name="Mercury",radius=10,orbital_dis=100,colour=(255,0,0),center=center_planet,system=system)
venus = Planet(x=SCREEN_WIDTH//2,y=150,name="Venus",radius=10,orbital_dis=150,colour=(0,255,0),center=center_planet,system=system)
earth = Planet(x=SCREEN_WIDTH//2,y=200,name="Earth",radius=10,orbital_dis=200,colour=(0,0,255),center=center_planet,system=system,mass=1*10^8)
moon = Planet(x=SCREEN_WIDTH//2,y=250,name="Moon",radius=5,orbital_dis=50,colour=(0,0,255),center=earth,system=system)
mars = Planet(x=SCREEN_WIDTH//2,y=300,name="Mars",radius=10,orbital_dis=300,colour=(0,255,255),center=center_planet,system=system)

accepted_chars = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"," "]

if __name__ == '__main__':
	try:
		while system.running:
			system.run()
	except Exception as e:
		print(traceback.format_exc())
		sleep(10)
