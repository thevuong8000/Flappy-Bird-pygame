import pygame
import random
import os
import time

pygame.font.init()  # init font
pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
PIPE_VEL = 3
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
HIGHEST_SCORE = 0

icon = pygame.image.load('images/bird2.png')
icon = pygame.transform.scale(icon, (256, 256))
pygame.display.set_icon(icon)

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha())
background = pygame.transform.scale(pygame.image.load(os.path.join("images","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")).convert_alpha())

class Bird:
	MAX_ROTATION = 25
	IMGS = bird_images
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.gravity = 9.8
		self.tilt = 0  # degrees to tilt
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.vel = -20
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1
		self.vel += 2.5

		self.y = self.y + self.vel

		if self.y < self.height + 25:  # tilt up
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:  # tilt down
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, screen):
		self.img_count += 1

		# For animation of bird, loop through three images
		if self.img_count <= self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count <= self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count <= self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		# so when bird is nose diving it isn't flapping
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2


		# tilt the bird
		blitRotateCenter(screen, self.img, (self.x, self.y), self.tilt)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe():
	GAP = 190
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.gap = 100  # gap between top and bottom pipe

		# where the top and bottom of the pipe is
		self.top = 0
		self.bottom = 0

		self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
		self.PIPE_BOTTOM = pipe_img

		self.passed = False

		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, screen):
		# draw top
		screen.blit(self.PIPE_TOP, (self.x, self.top))
		# draw bottom
		screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


	def collide(self, bird, screen):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask,top_offset)

		if b_point or t_point:
			return True

		return False

class Base:
	VEL = 5
	WIDTH = base_img.get_width()
	IMG = base_img

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, screen):
		screen.blit(self.IMG, (self.x1, self.y))
		screen.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
	rotated_image = pygame.transform.rotate(image, angle)
	new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

	surf.blit(rotated_image, new_rect.topleft)

def end_screen(screen):
	run = True
	esc_label = END_FONT.render("Press Esc to Exit", 1, (34,130,40))
	restart_label = END_FONT.render("Press Space to Restart", 1, (64,70,179))
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					main(screen)
				elif event.key == 27: # ESC
					pygame.quit()
					quit()

		screen.blit(esc_label, (SCREEN_WIDTH/2 - esc_label.get_width()/2, 400))
		screen.blit(restart_label, (SCREEN_WIDTH/2 - restart_label.get_width()/2, 500))
		pygame.display.update()

	pygame.quit()
	quit()

def draw_window(screen, bird, pipes, base, score):
	screen.blit(background, (0, 0))

	for pipe in pipes:
		pipe.draw(screen)

	base.draw(screen)
	bird.draw(screen)

	# score
	highest_score_label = STAT_FONT.render("Highest Score: " + str(HIGHEST_SCORE), 1, (255,255,255))
	score_label = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	screen.blit(score_label, (SCREEN_WIDTH - score_label.get_width() - 15, 50))
	screen.blit(highest_score_label, (SCREEN_WIDTH - highest_score_label.get_width() - 15, 10))

level = {1 : 23, 20 : 22, 50 : 21, 80 : 20, 100 : 19, 130 : 18, 180 : 17, 200 : 16, 250 : 15}
def main(screen):
	global HIGHEST_SCORE
	bird = Bird(230,350)
	base = Base(FLOOR)
	pipes = [Pipe(700)]
	score = 0

	clock = pygame.time.Clock()
	start = False
	lost = False

	DELAY = 23

	run = True
	while run:
		pygame.time.delay(DELAY + 1)
		clock.tick(150)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break

			if event.type == pygame.KEYDOWN and not lost:
				if event.key == pygame.K_SPACE:
					if not start:
						start = True
					bird.jump()

		# Move Bird, base and pipes
		if start:
			bird.move()
		if not lost:
			base.move()

			if start:
				rem = []
				add_pipe = False
				for pipe in pipes:
					pipe.move()
					# check for collision
					if pipe.collide(bird, screen) or bird.y + bird_images[0].get_height() - 10 >= FLOOR:
						lost = True
						screen.fill((209, 227, 214))
						pygame.display.update()
						bird.jump()
						pygame.time.delay(25)

					if pipe.x + pipe.PIPE_TOP.get_width() < 0:
						rem.append(pipe)

					if not pipe.passed and pipe.x < bird.x:
						pipe.passed = True
						add_pipe = True

				if add_pipe:
					score += 1
					HIGHEST_SCORE = max(HIGHEST_SCORE, score)
					if score in level.keys():
						DELAY = level[score]
					pipes.append(Pipe(SCREEN_WIDTH))

				for r in rem:
					pipes.remove(r)


		if bird.y + bird_images[0].get_height() - 10 >= FLOOR:
			bird.y = FLOOR - 45
			draw_window(screen, bird, pipes, base, score)
			pygame.display.update()
			break

		draw_window(screen, bird, pipes, base, score)
		if not start:
			start_label = END_FONT.render("Press Space to Start", 1, (64,70,179))
			screen.blit(start_label, ((SCREEN_WIDTH/2 - start_label.get_width()/2, 500)))
		pygame.display.update()

	end_screen(screen)


if __name__ == '__main__':
	main(SCREEN)