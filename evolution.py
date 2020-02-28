import pygame
from pygame.locals import *
import random
import math
import json
import statistics


#class lists
blobs = []
delBlobs = []
foods = []
foodSpawns = []
delFoods = []

#base vars
time = 0
x = 0
y = 0

#logging Vars
foodEaten = 0
blobsDied = 0
blobsReproduced = 0
cycleNumber = 0
popAvg = []

#config JSON
with open("/Users/lucas/Documents/cody stuff/Evolution 2.0/config.json") as f:
	config = json.load(f)

def isOccupied(coord, blobMove):
	#checks if a given coordinate would collide with any blobs
	for blob in blobs:
		if blobMove != blob and blob.rect.colliderect(pygame.Rect(coord[0], coord[1], 20, 20)):
			return True

	return False

def getCommonPattern():
	#finds the most common parent pattern between all blobs
	patternDict = {}

	for blob in blobs:
		count = 0
		pattern = []

		for direction in blob.parents:
			if count == 0 or count % 5 == 0:
				pattern.append(list(direction)[0].capitalize())
			count += 1
		if str(pattern) in patternDict:
			patternDict[str(pattern)] += 1
		else:
			patternDict[str(pattern)] = 1

	return [max(patternDict, key=patternDict.get), patternDict[max(patternDict, key=patternDict.get)]]

def getLongestLiving():
	#finds the blob that has lived for the longest time
	longestLiving = blobClass(0, 0, [], [0, 0], [])

	for blob in blobs:
		if blob.daysLived >= longestLiving.daysLived:
			longestLiving = blob

	return longestLiving

def spawnFood(foodNumber):
	global foods
	if len(foodSpawns) == 0 and not config["randomFoodSpawn"]:
		#randomly spawns food
		while len(foodSpawns) < foodNumber:
			sameBool = False
	
			food_thing = foodClass(random.randint(20, 760), random.randint(20, 760))
			for food in foodSpawns:
				if [food.x, food.y] == [food_thing.x, food_thing.y]:
					sameBool = True
			if not sameBool:
				foodSpawns.append(food_thing)

	elif not config["randomFoodSpawn"]:
		foods = []
		for food in foodSpawns:
			foods.append(food)

	else:
		foods = []
		while len(foods) < foodNumber:
			sameBool = False
	
			food_thing = foodClass(random.randint(20, 760), random.randint(20, 760))
			for food in foods:
				if [food.x, food.y] == [food_thing.x, food_thing.y]:
					sameBool = True
			if not sameBool:
				foods.append(food_thing)

def spawnBlobs(blobNumber):
	#randomly spawns blobs on all edges
	for x in range(blobNumber):
		blobMoves = []
		uniqueHome = False

		for x in range(121):
				direction = random.choice(["right", "down", "up", "left"])
				for x in range(5):
					blobMoves.append(direction)

		if not uniqueHome:
			if random.randint(1, 2) == 1:
				x = random.randint(0, 780)
				if random.randint(1, 2) == 1:
					y = 780
				else:
					y = 0
			else:
				y = random.randint(0, 780)
				if random.randint(1, 2) == 1:
					x = 780
				else:
					x = 0
			uniqueHome = True
			for blob in blobs:
				if blob.rect.colliderect(pygame.Rect(x, y, 20, 20)):
					uniqueHome = False
			if uniqueHome:
				blobs.append(blobClass(x, y, blobMoves, [x, y], blobMoves))
		#spawning function that allows overlapping spawns
		'''
		if random.randint(1, 2) == 1:
			x = random.randint(0, 780)
			if random.randint(1, 2) == 1:
				y = 780
			else:
				y = 0
		else:
			y = random.randint(0, 780)
			if random.randint(1, 2) == 1:
				x = 780
			else:
				x = 0
		blobs.append(blobClass(x, y, blobMoves, [x, y]))
		'''

def detect(blob):
	#searches for food inthe 8 surrounding "tiles"
	x = blob.x - 20
	y = blob.y - 20

	for food in foods:
		rright, rbottom = x + 60/2, y + 60/2

		cleft, ctop	 = food.x-10, food.y-10
		cright, cbottom = food.x+10, food.y+10

		for x in (x, x + 60):
			for y in (y, y + 60):

				if math.hypot(x-food.x, y-food.y) <= 10:
					return [True, [food.x, food.y]]
					break

			if x <= food.x <= rright and y <= food.y <= rbottom:
				[True, [food.x, food.y]]
				break

	return [False, []]

def eatFood(blob):
	#if the blob is touching food it will eat it
	global foodEaten

	for food in foods:
		rright, rbottom = blob.x + 20/2, blob.y + 20/2

		cleft, ctop	 = food.x-10, food.y-10
		cright, cbottom = food.x+10, food.y+10

		for x in (blob.x, blob.x+20):
			for y in (blob.y, blob.y+20):

				if math.hypot(x-food.x, y-food.y) <= 10:
					delFoods.append(food)
					blob.food += 1	
					foodEaten += 1
					if config["verboseLogging"]:
						print(str(blob.blobTag) + "ate a food")
					break

			if blob.x <= food.x <= rright and blob.y <= food.y <= rbottom:
				delFoods.append(food)
				blob.food += 1
				foodEaten += 1
				if config["verboseLogging"]:
					print(str(blob.blobTag) + "ate a food")
				break

def getPriority(blob, canGo):
	#finds direction with least other blobs
	x = blob.x
	y = blob.y

	priorityDict = {"left": 0, "right": 0, "up": 0, "down": 0}
	leftBox = pygame.Rect(x + 40, y - 20, 20, 60)
	rightBox = pygame.Rect(x - 20, y - 20, 20, 60)
	upBox = pygame.Rect(x - 20, y - 20, 60, 20)
	downBox = pygame.Rect(x - 20, y + 40, 60, 20)
	for blob in blobs:
		if blob.rect.colliderect(leftBox):
			priorityDict["left"] += 1
		if blob.rect.colliderect(rightBox):
			priorityDict["right"] += 1
		if blob.rect.colliderect(upBox):
			priorityDict["up"] += 1
		if blob.rect.colliderect(downBox):
			priorityDict["down"] += 1

	while True:
		if len(canGo) == 1:
			return canGo[0]
		if min(priorityDict, key=priorityDict.get) in canGo:
			return min(priorityDict, key=priorityDict.get)
		else:
			del priorityDict[min(priorityDict, key=priorityDict.get)]
	
def moveAI(canGo, priority, blob):
	#prevents blob from going into walls and into other blobs
	x = blob.x
	y = blob.y
	if len(canGo) < 2:
		return random.choice(["right", "down", "up", "left"])
	else:
		if priority == "up": moveInfo=[y > 5, not isOccupied([x, y-10], blob), "up"]
		elif priority == "down": moveInfo=[y < 775, not isOccupied([x, y+10], blob), "down"]
		elif priority == "left": moveInfo=[x < 775, not isOccupied([x-10, y], blob), "left"]
		elif priority == "right": moveInfo=[x > 5, not isOccupied([x+10, y], blob), "right"]
		if moveInfo[0] and moveInfo[1]:
			return moveInfo[2]
		else:
			canGo.remove(priority)
			return moveAI(canGo, getPriority(blob, canGo), blob)
		

class foodClass(object):
	'''
		x: x-coordinate
		y: y-coordinate
	'''
	def __init__(self, x, y):
		self.x = x 
		self.y = y

	def update(self):
		#updates food position every tick
		pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 10)

class blobClass(object):
	'''
		blobTag: unique number
		x: x-coordinate
		y: y-coordinate
		home: coords blob returns to every cycle
		parents: parent move patterns
		moves:curent move pattern
		rect: pygame rect object
		homeVar: var that tells blob to retyrn to home coords
		foodVar: var that holds info to track food
		food: current amount of food
		daysLived: number of days lived
	'''
	blobTag = 1
	def __init__(self, x, y, moves, home, parents, food = 0):
		self.x = x
		self.y = y
		self.home = home
		self.parents = parents
		self.moves = moves
		self.rect = pygame.Rect(self.x, self.y, 20, 20)
		self.homeVar = False
		self.foodVar = [False, []]
		self.food = food
		self.daysLived = 0
		blobClass.blobTag += 1

	def move(self):
		#finds best direction to move
		foodVar = detect(blob)

		if not self.homeVar:
			try:
				direction = moveAI(["right", "down", "up", "left"], self.moves[time], self)
			except:
				print(time)
			if direction == "right": 
				self.x -= 5
				eatFood(self)
			if direction == "left": 
				self.x += 5
				eatFood(self)
			if direction == "down": 
				self.y += 5
				eatFood(self)
			if direction == "up": 
				self.y -= 5
				eatFood(self)

		elif self.foodVar[0]:
			if abs(self.x - self.foodvar[0]) > 5:
				if self.x > self.foodVar[0]:
					self.x -= 5
					eatFood(self)
				else:
					self.x += 5
					eatFood(self)
			elif abs(self.y - self.foodvar[1]) > 5:
				if self.x > self.foodVar[0]:
					self.y -= 5
					eatFood(self)
				else:
					self.y += 5
					eatFood(self)
			else:
				eatFood(self)
				self.foodVar = [False, []]

		else:
			if self.home[0] > self.x:
				self.x += 5
				eatFood(self)
			elif self.home[0] < self.x:
				self.x -= 5
				eatFood(self)
			elif self.home[1] < self.y:
				self.y -= 5
				eatFood(self)
			elif self.home[1] > self.y:
				self.y += 5
				eatFood(self)

	def reproduce(self):
		#adds new blob with mutated moves to the blobs list
		if config["verboseLogging"]:
			print(str(self.blobTag) + "reproduced")
		uniqueHome = False

		while True:
			if not uniqueHome:
				if random.randint(1, 2) == 1:
					x = random.randint(0, 780)
					if random.randint(1, 2) == 1:
						y = 780
					else:
						y = 0
				else:
					y = random.randint(0, 780)
					if random.randint(1, 2) == 1:
						x = 780
					else:
						x = 0
				uniqueHome = True
				for blob in blobs:
					if blob.rect.colliderect(pygame.Rect(x, y, 20, 20)):
						uniqueHome = False
				if uniqueHome:
					newHome = [x, y]
					break
		'''
		if self.home[0] == 780:
			if random.randint(1, 2) == 1:
				newHome = [780, self.home[1] + 20]
			else:
				newHome = [780, self.home[1] - 20]
		elif self.home[0] == 0:
			if random.randint(1, 2) == 1:
				newHome = [0, self.home[1] + 20]
			else:
				newHome = [0, self.home[1] - 20]
		elif self.home[1] == 780:
			if random.randint(1, 2) == 1:
				newHome = [780, self.home[0] + 20]
			else:
				newHome = [780, self.home[0] - 20]
		elif self.home[1] == 0:
			if random.randint(1, 2) == 1:
				newHome = [0, self.home[0] + 20]
			else:
				newHome = [0, self.home[0] - 20]
		'''
		newMoves = []
		countVar = 0

		for direction in self.moves:
			countVar += 1
			if countVar % 5 == 0 or countVar == 0:
				if random.randint(1, 6) == 1:
					if direction == "up" or direction == "down":
						if random.randint(1, 2) == 1:
							newDirection = "right"
						else:
							newDirection = "left"
					else:
						if random.randint(1, 2) == 1:
							newDirection = "up"
						else:
							newDirection = "down"
				else:
					newDirection = direction
				for x in range(5):
					newMoves.append(newDirection)

		blobs.append(blobClass(newHome[0], newHome[1], newMoves, newHome, self.parents, 1))

	def update(self):
		#redraws blob every tick
		self.rect = pygame.Rect(self.x, self.y, 20, 20)
		self.rect.clamp_ip(screen.get_rect())
		pygame.draw.rect(screen, (0, 255, 0), self.rect)

		if config["showSenseOutline"]:
			outline = pygame.Rect(self.x - 20, self.y - 20, 60, 60)
			outline.clamp_ip(screen.get_rect())
			pygame.draw.rect(screen, (0, 255, 0), outline, 1)

#Initiate Pygame Canvas
pygame.init()
screen = pygame.display.set_mode((800, 800), DOUBLEBUF)
clock = pygame.time.Clock()
clippingRect = Rect(0, 0, 800, 800)
screen.set_clip(clippingRect)

#Spawn Entities
spawnBlobs(40)
spawnFood(50)

while True:
	pygame.display.flip()
	pygame.event.get()
	screen.fill((0, 0, 0))

	for blob in blobs:
		#updates blob every tick
		blob.move()
		blob.update()
		if blob.food > 1:
			blob.homeVar = True

	for food in foods:
		#updates food every tick
		food.update()

	if time == 600:
		for blob in blobs:
			blob.homeVar = True

	if time > 750:
		time = 0
		foodEaten = 0
		blobsDied = 0
		blobsReproduced = 0
		cycleNumber += 1
		spawnFood(50)

		for blob in blobs:
			blob.homeVar = False
			if blob.food == 0:
				delBlobs.append(blob)
				blobsDied += 1
				if config["verboseLogging"]:
					print(str(blob.blobTag) + "died")
			elif blob.food > 1:
				blob.reproduce()
				blobsReproduced += 1
			if blob.food > 0:
				blob.daysLived += 1
			blob.food = 0

		popAvg.append(len(blobs) - blobsDied)
		print(
			"-----------------------------------------" + 
			"\nCycle: " + str(cycleNumber) + 
			"\nTotal Foods Eaten: " + str(foodEaten) + 
			"\nNumber of Blobs that Died: " + str(blobsDied) + 
			"\nNumber of Blobs that Reproduced: " + str(blobsReproduced) + 
			"\nCurrent Population: " + str(len(blobs) - blobsDied) + 
			"\nMost Common Move Pattern: " + str(getCommonPattern()[0]).strip("[]").replace("'", "").replace(",", "") + " It appears in " + str(getCommonPattern()[1]) + " blob(s)" + 
			"\nLongest Living Blob: Blob Number " + str(getLongestLiving().blobTag) + " it has lived for " + str(getLongestLiving().daysLived) + " days"
			)
		if config["showAveragePop"]:
			print("The Aveage Population over " + str(cycleNumber) + " cycles is " + str(statistics.mean(popAvg)))
		print("-----------------------------------------")

	for blob in delBlobs:
		blobs.remove(blob)

	for food in delFoods:
		if food in foods:
			foods.remove(food)

	delBlobs = []
	time += 1
	clock.tick(30)