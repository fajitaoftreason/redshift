#imports the pygame library, and sys library.
import pygame, sys, math, random
#import all your key names
from pygame.locals import *

BLACK = pygame.Color(0,0,0)
RED = pygame.Color(255,0,0)
MAXAGE = 40
RESOLUTION = (640, 480)
MAXSPEED = 15
TURNRATE = .15
STARTINGASTEROIDS = 4
POWERUPSIZE = 10

class shot:
    shotspeed = 10
    def __init__(self, fromShip):
        self.angle = fromShip.angle
        self.x = fromShip.p1x
        self.y = fromShip.p1y
        self.dX = fromShip.dX + self.shotspeed*math.cos(self.angle)
        self.dY = fromShip.dY + self.shotspeed*math.sin(self.angle)
        self.age = 0
    def step(self):
        self.x = (self.x + self.dX)%RESOLUTION[0]
        self.y = (self.y + self.dY)%RESOLUTION[1]
        self.age += 1
    def getline(self):
        return [self.x - self.dX, self.y - self.dY]
    
class asteroid:
    def __init__(self, parentAsteroid=0):
        if parentAsteroid == 0:
            i = random.randint(0, 1)
            self.x = 0
            self.y = 0
            if i == 0:
                self.x = random.randint(0, RESOLUTION[0])
            else:
                self.y =  random.randint(0, RESOLUTION[1])
            self.dX = random.random()*8 - 4
            self.dY = random.random()*6 - 3
            self.radius = random.randint(20, 50)
        else:  #this is used to create smaller asteroids based off the parent's location and speed
            #spawn in square centered in the parent, with side lengths = parent's radius
            self.x = random.randint(0, parentAsteroid.radius) - parentAsteroid.radius/2 + parentAsteroid.x
            self.y = random.randint(0, parentAsteroid.radius) - parentAsteroid.radius/2 + parentAsteroid.y
            
            #add or subtract up to 2 to it's parent's velocity
            self.dX = random.random()*6 - 3 + parentAsteroid.dX
            self.dY = random.random()*6 - 3 + parentAsteroid.dY
            self.radius = random.randint(15, 25)
        
    def step(self):
        self.x = (self.x + self.dX)%RESOLUTION[0]
        self.y = (self.y + self.dY)%RESOLUTION[1]
        
    def breakApart(self):
        numchildren = int(math.ceil((self.radius - 40)/3.2))+1
        children = []
        for i in range(numchildren):
            children.append(asteroid(self))
        return children

class powerup:
    def __init__(self):
        
        self.x = random.randint(0, RESOLUTION[0] - 100)
        if self.x > (RESOLUTION[0] - 100)/2:
            self.x += 100
            
        self.y = random.randint(0, RESOLUTION[1] - 100)
        if self.y > (RESOLUTION[1] - 100)/2:
            self.y += 100
        
        self.powerType = random.randint(0, 5)
        

class ship:
    def __init__(self):
        self.angle = 0
        self.x = RESOLUTION[0]/2
        self.y = RESOLUTION[1]/2
        self.p1x = 0
        self.p2x = 0
        self.p3x = 0
        self.p1y = 0
        self.p2y = 0
        self.p3y = 0
        self.dX = 0
        self.dY = 0
        self.shipColor = pygame.Color(0,0,0)
        self.weaponPower = 0
        self.shield = 1
        self.shieldRadius = 30
        self.redness = 0
        self.step()
        
    def step(self):
        #update position
        self.x = (self.x + self.dX) % RESOLUTION[0]  
        self.y = (self.y + self.dY) % RESOLUTION[1]
        
        #calculate location of front of ship
        self.p1x = 20*math.cos(self.angle) + self.x
        self.p1y = 20*math.sin(self.angle) + self.y
        
        #calculate location of back corners
        self.p2x = -20*math.cos(self.angle) + 10*math.cos(self.angle+math.pi/2) + self.x
        self.p2y = -20*math.sin(self.angle) + 10*math.sin(self.angle+math.pi/2) + self.y
           
        self.p3x = -20*math.cos(self.angle) + 10*math.cos(self.angle-math.pi/2) + self.x
        self.p3y = -20*math.sin(self.angle) + 10*math.sin(self.angle-math.pi/2) + self.y
    
    def getPoints(self):
        return [[self.p1x, self.p1y], [self.p2x, self.p2y], [self.p3x, self.p3y]]
        
    def rotate(self, angleInRads):
        self.angle += angleInRads
    
    def accelerate(self):
        self.dX += math.cos(self.angle)
        self.dY += math.sin(self.angle)
        
        #cap speed
        if math.sqrt(self.dX**2 + self.dY**2) > MAXSPEED:
            self.dX = MAXSPEED * math.cos(math.atan2(self.dY, self.dX))
            self.dY = MAXSPEED * math.sin(math.atan2(self.dY, self.dX))
            
    def gainShield(self):
        self.shield += 1
        self.shieldRadius += 10
    def loseShield(self):
        self.shield -= 1
        self.shieldRadius -= 10
    
    def win(self, roundNumber):
        self.redness += 1
        self.shipColor = pygame.Color(min(26 * self.redness, 255), 0, 0)
        
    def lose(self):
        self.__init__()

    
          
def main():
    #initialize the library and start a clock, just in case we want it.
    pygame.init()

    #initialize the clock that will determine how often we render a frame
    clock = pygame.time.Clock()

    #create our canvas that will be draw on.

    canvas = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption('RedShift')

    #Pick our background and other colors with R,G,B values between 0 and 255
    backgroundColor = pygame.Color(255,255,255)
    
     #initialize font object
    font = pygame.font.Font(None, 30)
    largeFont = pygame.font.Font(None, 125)
    
    roundNumber = 0
    keyspressed = []
    projectiles = []
    asteroids = []
    hero = ship()

    
    
    #for ever and ever, keep rendering a new frame of our game.
    #this is where code that needs to be run every single frame belongs
    while True:
        #get all of our input events that have happened since the last frame
        for event in pygame.event.get():

            #deal with key presses
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return    
                elif event.key == K_SPACE:
                    projectiles.append(shot(hero))
                
                keyspressed.append(event.key)
            if event.type == KEYUP:
				keyspressed.remove(event.key)
			
                 
            
                    
        if K_RIGHT in keyspressed:
            hero.rotate(TURNRATE)
        if K_LEFT in keyspressed:
            hero.rotate(-1*TURNRATE)
        if K_UP in keyspressed:
            hero.accelerate()
                

            
        #Done dealing with events, lets draw updated things on our canvas
        #fill our canvas with a background color, effectively erasing the last frame
        canvas.fill(backgroundColor)
        
        canvas.blit(font.render("Round: " + str(roundNumber), 1, BLACK), (5, 5))
        if hero.redness >= 10:
            canvas.blit(font.render("RedShift Available", 1, RED), ((RESOLUTION[0]/2 - font.size("RedShift Available")[0]/2), 5))
        
        
        
        #if you kill all the asteroids, add one more, then populate
        if len(asteroids)==0:
            hero.win(roundNumber)
            roundNumber += 1
            if roundNumber % 2 == 0:
                hero.gainShield()
            for i in range(STARTINGASTEROIDS + roundNumber):
                asteroids.append(asteroid())
        
        hero.step()

        #draw shield if there is one
        if hero.shield > 0:
            lightness = min(90 + hero.shieldRadius*2, 200) 
            pygame.draw.circle(canvas, pygame.Color(lightness,lightness,255), [int(hero.x), int(hero.y)], hero.shieldRadius)        
        #draw ship
        pygame.draw.polygon(canvas, hero.shipColor, hero.getPoints(), 0)


                
        for pew in projectiles:
            #update position
            pew.step()
            #shots have a limited life span, this will delete them
            if pew.age > MAXAGE:
                projectiles.remove(pew)
            #draw shots
            pygame.draw.line(canvas, pygame.Color(255, 0, 125), [pew.x, pew.y], pew.getline(), 2)
        
        for rock in asteroids:
            #if the game has ended, we start deleting rocks
            if roundNumber == 0:
                asteroids.remove(rock)
                break
            #update position
            rock.step()
            #draw rock
            pygame.draw.circle(canvas, BLACK, [int(rock.x), int(rock.y)], rock.radius)
            
            #test for rock hitting shield
            if hero.shield > 0:
                if math.sqrt((hero.x - rock.x)**2 + (hero.y - rock.y)**2) < (hero.shieldRadius + rock.radius):
                    asteroids.remove(rock)
                    hero.loseShield()
                    break
            
            #test for rock going boom
            for pew in projectiles:
                if math.sqrt((pew.x - rock.x)**2 + (pew.y - rock.y)**2) < rock.radius:
                    asteroids.remove(rock)
                    projectiles.remove(pew)
                    if rock.radius > 40:
                        asteroids.extend(rock.breakApart())
                    break

            #test to see if player died
            if math.sqrt((hero.p1x - rock.x)**2 + (hero.p1y - rock.y)**2) < rock.radius or math.sqrt((hero.p2x - rock.x)**2 + (hero.p2y - rock.y)**2) < rock.radius or math.sqrt((hero.p3x - rock.x)**2 + (hero.p3y - rock.y)**2) < rock.radius:
                if hero.redness < 10:
                    roundNumber = 0
                    hero.lose()
                    sizeoftext = largeFont.size("Game Over")
                    canvas.blit(largeFont.render("Game Over", 1, BLACK), ((RESOLUTION[0]/2 - sizeoftext[0]/2), (RESOLUTION[1]/2 - sizeoftext[1]/2)))
                    pygame.display.update()
                    for i in range(60):
                        clock.tick(30)
                    break
                else: #activate redshift
                    break
        
        if hero.redness >= 10:
            canvas.blit(font.render("RedShift Available", 1, RED), ((RESOLUTION[0]/2 - font.size("RedShift Available")[0]/2), 5))
        
        #done drawing all the stuff on our canvas, now lets show it to the user
        pygame.display.update()

        #wait the amount of time which
        clock.tick(30)

    
main()
