import pygame
from pygame.locals import *
import random
import math

blobs = []
delBlobs = []
foods = []
delFoods = []
time = 0
x = 0
y = 0

pygame.init()
screen = pygame.display.set_mode((800, 800), DOUBLEBUF)
clock = pygame.time.Clock()
clippingRect = Rect(0, 0, 800, 800)
screen.set_clip(clippingRect)

def isOccupied(coord, blobMove):
	for blob in blobs:
		if blobMove != blob and blob.rect.colliderect(pygame.Rect(coord[0], coord[1], 20, 20)):
			return True
	return False

def spawnFood(foodNumber):
	while len(foods) < foodNumber:
		sameBool = False

		food_thing = foodClass(random.randint(20, 760), random.randint(20, 760))
		for food in foods:
			if [food.x, food.y] == [food_thing.x, food_thing.y]:
				sameBool = True
		if not sameBool:
			foods.append(food_thing)

def spawnBlobs(blobNumber):
	for x in range(blobNumber):
		blobMoves = []
		uniqueHome = False

		for x in range(120):
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
				blobs.append(blobClass(x, y, blobMoves, [x, y]))

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

def eatFood(blob):
	for food in foods:
		rright, rbottom = blob.x + 20/2, blob.y + 20/2

		cleft, ctop	 = food.x-10, food.y-10
		cright, cbottom = food.x+10, food.y+10

		for x in (blob.x, blob.x+20):
			for y in (blob.y, blob.y+20):

				if math.hypot(x-food.x, y-food.y) <= 10:
					delFoods.append(food)
					blob.food += 1	
					break

			if blob.x <= food.x <= rright and blob.y <= food.y <= rbottom:
				delFoods.append(food)
				blob.food += 1
				break

def getPriority(blob, canGo):
	x = blob.x
	y = blob.y
	priorityDict = {"left": 0, "right": 0, "up": 0, "down": 0}
	leftBox = pygame.Rect(x + 40, y + 20, 20, 60)
	rightBox = pygame.Rect(x - 20, y + 20, 20, 60)
	upBox = pygame.Rect(x - 20, y + 20, 60, 20)
	downBox = pygame.Rect(x - 20, y - 40, 60, 20)
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
	x = blob.x
	y = blob.y
	if len(canGo) < 2:
		return random.choice(["right", "down", "up", "left"])
	else:
		if priority == "up": moveInfo=[y > 5, not isOccupied([x, y-5], blob), "up"]
		elif priority == "down": moveInfo=[y < 775, not isOccupied([x, y+5], blob), "down"]
		elif priority == "left": moveInfo=[x < 775, not isOccupied([x-5, y], blob), "left"]
		elif priority == "right": moveInfo=[x > 5, not isOccupied([x+5, y], blob), "right"]
		if moveInfo[0] and moveInfo[1]:
			return moveInfo[2]
		else:
			canGo.remove(priority)
			return moveAI(canGo, getPriority(blob, canGo), blob)

class foodClass(object):
	def __init__(self, x, y):
		self.x = x 
		self.y = y

	def update(self):
		pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 10)

class blobClass(object):
	blobTag = 1
	def __init__(self, x, y, moves, home, food = 0):
		self.x = x
		self.y = y
		self.home = home
		self.rect = pygame.Rect(self.x, self.y, 20, 20)
		self.number = blobClass.blobTag
		self.moves = moves
		self.moveCount = 0
		self.homeVar = False
		self.foodVar = False
		self.food = food
		blobClass.blobTag += 1

	def move(self):
		foodVar = detect()
		if not self.homeVar:
			direction = moveAI(["right", "down", "up", "left"], self.moves[time], self)
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
		elif foodVar:
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
		blobs.append(blobClass(newHome[0], newHome[1], newMoves, newHome, 1))

	def update(self):
		self.rect = pygame.Rect(self.x, self.y, 20, 20)
		self.rect.clamp_ip(screen.get_rect())
		pygame.draw.rect(screen, (0, 255, 0), self.rect)

spawnFood(50)
spawnBlobs(10)

while True:
	pygame.display.flip()
	screen.fill((0, 0, 0))

	for blob in blobs:
		blob.move()
		blob.update()
		if blob.food > 1:
			blob.homeVar = True

	for food in foods:
		food.update()

	time += 1
	if time == 600:
		for blob in blobs:
			blob.homeVar = True
	if time > 750:
		time = 0
		foods = []
		spawnFood(50)
		for blob in blobs:
			blob.homeVar = False
			if blob.food == 0:
				delBlobs.append(blob)
			elif blob.food > 1:
				blob.reproduce()
			blob.food = 0
		print(len(blobs))
	for blob in delBlobs:
		blobs.remove(blob)
	for food in delFoods:
		if food in foods:
			foods.remove(food)
	delBlobs = []

	clock.tick(30)