import pygame
import math
import sys
from random import randint

class Planet():
	def __init__(self, x=0, y=0, z=0, name="Some Planet", radius=0, angle=0, orbital_dis=0,interplant_gravity=False, colour=(0,255,0),system=None,mass=0, center=None):
		self.x = x
		self.y = y
		self.z = z
		self.name = name
		self.radius = radius#radius of the planet
		self.angle = angle#angle from up to center to planet
		self.orbital_dis = orbital_dis#distance from center
		self.interplant_gravity = interplant_gravity
		self.colour = colour#pretty self explanatory RGB
		self.system = system
		self.center = center
		self.mass = mass

		if self.orbital_dis > 0:#checks to see if the orbital distance is greater than 0
			'''
			This is the code which calculates the velocity the planet will need to travel
			in order to stay in orbit around the center planet
			'''
			self.vel = math.sqrt(((6.673*(10**2))*center.mass)/self.orbital_dis)

		self.system.planets.append(self)

	def update_pos(self):
		circumference_change_ratio = self.vel/(math.pi*(self.orbital_dis*2))
		self.angle += 360*circumference_change_ratio

		x_change = math.cos(math.radians(self.angle))*self.orbital_dis
		y_change = math.sin(math.radians(self.angle))*self.orbital_dis

		if self.interplant_gravity:
			#calculate gravity shift
			pass

		self.x = x_change+self.center.x
		self.y = y_change+self.center.y

class System():
	def __init__(self, target_fps, screen_width, screen_height, stars, planets=[], zoom_level=1):
		self.target_fps = target_fps
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.zoom_level = zoom_level
		self.stars = stars

		self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
		self.clock = pygame.time.Clock()

		self.planets = planets
		self.selected_planet = None
		self.place_mode = False
		self.new_planet_size = 10

		self.running = True
		self.paused = False

		self.genrate_stars()

	def genrate_stars(self):
		area_to_be_covered = (self.screen_width*self.screen_height)*self.stars[2]
		number_stars = round(area_to_be_covered/(self.stars[0]*self.stars[1]))

		self.star_coords = []

		for n in range(number_stars):
			self.star_coords.append([randint(0,self.screen_width),randint(0,self.screen_height)])

	def zoom_shift(self, x, y):
		delta_x = x-(self.screen_width/2)
		delta_y = y-(self.screen_height/2)

		angle_from_center = math.atan((delta_y/delta_x))

		hyp = math.sqrt(((abs(x-(self.screen_width/2))**2)+(abs(y-(self.screen_height/2))**2)))
		hyp = hyp*self.zoom_level

		#print(f"X shift{(math.cos(angle_from_center)*hyp)}")
		#print(f"Y shift{(math.sin(angle_from_center)*hyp)}")

		x = (math.cos(angle_from_center)*hyp)
		y = (math.sin(angle_from_center)*hyp)

		return x, y


	def run(self):
		self.clock.tick(self.target_fps)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 5:
					self.zoom_level += 0.05
				elif event.button == 4:
					self.zoom_level -= 0.05

				mouse_x, mouse_y = pygame.mouse.get_pos()

				for p in self.planets:
					if math.sqrt((abs(mouse_x-p.x)**2)+(abs(mouse_y-p.y)**2)) <= p.radius:
						print(f"Clicked on planet {p.name}")
						self.selected_planet = p
						break

					self.selected_planet = None


		keys = pygame.key.get_pressed()

		if keys[pygame.K_d]:
			if not self.prev_keys[pygame.K_d]:
				if not self.place_mode:
					self.place_mode = True
				else:
					self.place_mode = False

		if keys[pygame.K_p]:
			if not self.prev_keys[pygame.K_p]:
				if not self.paused:
					self.paused = True
				else:
					self.paused = False

		if keys[pygame.K_UP]:
			if self.place_mode:
				self.new_planet_size += 1

		if keys[pygame.K_DOWN]:
			if self.place_mode:
				self.new_planet_size -= 1


		if self.place_mode and keys[pygame.K_RETURN]:
			#print(round(math.sqrt(abs(mouse_x-self.screen_width//2)+abs(mouse_y-self.screen_height//2))))
			mouse_x, mouse_y = pygame.mouse.get_pos()

			new_p = Planet(x=mouse_x,y=mouse_y,radius=self.new_planet_size,orbital_dis=math.sqrt(((abs(mouse_x-self.planets[0].x)**2)+(abs(mouse_y-self.planets[0].y)**2))),colour=(0,0,255),center=self.planets[0])
			self.planets.append(new_p)
			self.place_mode = False


		self.screen.fill((0,0,0))

		for star in self.star_coords:
			pygame.draw.rect(self.screen, (255,255,255), (star[0], star[1], self.stars[0], self.stars[1]))

		test_box_x, test_box_y = self.zoom_shift(100,100)
		pygame.draw.rect(self.screen, (0,255,255), (test_box_x, test_box_y, 100*self.zoom_level, 50*self.zoom_level))

		if self.place_mode:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			pygame.draw.circle(self.screen, (255,255,255), (mouse_x, mouse_y), self.new_planet_size, width=2)

		pygame.draw.circle(self.screen, self.planets[0].colour, (self.planets[0].x, self.planets[0].y), self.planets[0].radius)
		for p in self.planets[1:]:
			if not self.paused:
				p.update_pos()
			pygame.draw.circle(self.screen, p.colour, (p.x, p.y), p.radius)

		if self.selected_planet:
			pygame.draw.rect(self.screen, (255,255,255), (self.selected_planet.x-self.selected_planet.radius, self.selected_planet.y-self.selected_planet.radius, self.selected_planet.radius*2, self.selected_planet.radius*2), width=2)


		self.prev_keys = keys
		#print(f"Target FPS: {TARGET_FPS}, Actual FPS: {clock.get_fps()}")
		pygame.display.update()





TARGET_FPS = 20
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

system = System(target_fps=20,screen_width=1200,screen_height=750,stars=[2,2,0.001])

center_planet = Planet(x=SCREEN_WIDTH//2,y=SCREEN_HEIGHT//2,name="Sun",radius=30,colour=(255,255,255),mass=1*10^6,system=system)
planet_1 = Planet(x=SCREEN_WIDTH//2,y=100,name="Mercury",radius=10,orbital_dis=100,colour=(255,0,0),center=center_planet,system=system)
planet_2 = Planet(x=SCREEN_WIDTH//2,y=150,name="Venus",radius=10,orbital_dis=150,colour=(0,255,0),center=center_planet,system=system)
planet_3 = Planet(x=SCREEN_WIDTH//2,y=200,name="Earth",radius=10,orbital_dis=200,colour=(0,0,255),center=center_planet,system=system)
planet_4 = Planet(x=SCREEN_WIDTH//2,y=300,name="Mars",radius=10,orbital_dis=300,colour=(0,255,255),center=center_planet,system=system)

#planets = [center_planet,planet_1,planet_2,planet_3,planet_4]



print(system.zoom_shift(500,275))

if __name__ == '__main__':
	while system.running:
		system.run()

'''
running = True
paused = False

new_planet_size = 10
place_mode = False

selected_planet = None

while running:
	clock.tick(TARGET_FPS)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()

			for p in planets:
				if math.sqrt((abs(mouse_x-p.x)**2)+(abs(mouse_y-p.y)**2)) <= p.radius:
					print(f"Clicked on planet {p.name}")
					selected_planet = p
					break

				selected_planet = None


	keys = pygame.key.get_pressed()

	if keys[pygame.K_d]:
		if not prev_keys[pygame.K_d]:
			if not place_mode:
				place_mode = True
			else:
				place_mode = False

	if keys[pygame.K_p]:
		if not prev_keys[pygame.K_p]:
			if not paused:
				paused = True
			else:
				paused = False

	if keys[pygame.K_UP]:
		if place_mode:
			new_planet_size += 1

	if keys[pygame.K_DOWN]:
		if place_mode:
			new_planet_size -= 1


	if place_mode and keys[pygame.K_RETURN]:
		print(round(math.sqrt(abs(mouse_x-SCREEN_WIDTH//2)+abs(mouse_y-SCREEN_HEIGHT//2))))
		mouse_x, mouse_y = pygame.mouse.get_pos()

		new_p = Planet(x=mouse_x,y=mouse_y,radius=new_planet_size,orbital_dis=math.sqrt(((abs(mouse_x-center_planet.x)**2)+(abs(mouse_y-center_planet.y)**2))),colour=(0,0,255),center=center_planet)
		planets.append(new_p)
		place_mode = False


	screen.fill((0,0,0))
	if place_mode:
		mouse_x, mouse_y = pygame.mouse.get_pos()
		pygame.draw.circle(screen, (255,255,255), (mouse_x, mouse_y), new_planet_size, width=2)

	pygame.draw.circle(screen, center_planet.colour, (center_planet.x, center_planet.y), center_planet.radius)
	for p in planets:
		if not paused:
			p.update_pos()
		pygame.draw.circle(screen, p.colour, (p.x, p.y), p.radius)

	if selected_planet:
		pygame.draw.rect(screen, (255,255,255), (selected_planet.x-selected_planet.radius, selected_planet.y-selected_planet.radius, selected_planet.radius*2, selected_planet.radius*2), width=2)


	prev_keys = keys
	#print(f"Target FPS: {TARGET_FPS}, Actual FPS: {clock.get_fps()}")
	pygame.display.update()
'''