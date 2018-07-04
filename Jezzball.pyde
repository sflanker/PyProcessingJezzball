import math


class Dimension:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)

class Direction:
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Direction):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def opposite(self):
        if self.value == 0:
            return Direction.SW
        elif self.value == 1:
            return Direction.NW
        elif self.value == 2:
            return Direction.NE
        elif self.value == 3:
            return Direction.SE
        
    def flipVertical(self):
        if self.value == 0:
            return Direction.SE
        elif self.value == 1:
            return Direction.NE
        elif self.value == 2:
            return Direction.NW
        elif self.value == 3:
            return Direction.SW
        
    def flipHorizontal(self):
        if self.value == 0:
            return Direction.NW
        elif self.value == 1:
            return Direction.SW
        elif self.value == 2:
            return Direction.SE
        elif self.value == 3:
            return Direction.NE
        
Direction.NE = Direction(0)
Direction.SE = Direction(1)
Direction.SW = Direction(2)
Direction.NW = Direction(3)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Atom:
    def __init__(self, position, direction, bounced = False):
        self.position = position
        self.direction = direction
        self.bounced = bounced

gameDimensions = Dimension(28, 20)
gridSize = 25.0
margin = 10
level = 2

atoms = []
board = [[1 for y in range(gameDimensions.height)] for x in range(gameDimensions.width)]

screenSize = Dimension(gameDimensions.width * gridSize + margin * 2, gameDimensions.height * gridSize + margin * 2)


def setup():
    global atoms

    positions = []

    println("Screen: " + str(screenSize.width) + ", " + str(screenSize.height))
    size(screenSize.width, screenSize.height, P3D)
    
    for i in range(level + 1):
        pos = getNewPos(positions)
        positions.append(pos)
        dir = Direction(int(random(4)))
        atoms.append(Atom(pos, dir))

speed = 0.05


def getNewPos(positions):
    while True:
        pos = Point(int(random(gameDimensions.width)), int(random(gameDimensions.height)))
        if pos in positions:
            continue
        return pos

def bounceAtom(atom):
    bounceRight = atom.position.x > gameDimensions.width
    bounceLeft = atom.position.x < 0
    bounceTop = atom.position.y < 0
    bounceBottom = atom.position.y > gameDimensions.height
    
    direction = atom.direction
    if bounceRight:
        direction = Direction.NW if direction == Direction.NE else Direction.SW
    elif bounceLeft:
        direction = Direction.NE if direction == Direction.NW else Direction.SE
    if bounceTop:
        direction = Direction.SE if direction == Direction.NE else Direction.SW
    elif bounceBottom:
        direction = Direction.NE if direction == Direction.SE else Direction.NW
    
    return Atom(atom.position, direction, True) if direction != atom.direction else atom

def moveAtom(atom):
    if atom.direction == Direction.NE:
        return bounceAtom(Atom(Point(atom.position.x + speed, atom.position.y - speed), Direction.NE))
    elif atom.direction == Direction.SE:
        return bounceAtom(Atom(Point(atom.position.x + speed, atom.position.y + speed), Direction.SE))
    elif atom.direction == Direction.SW:
        return bounceAtom(Atom(Point(atom.position.x - speed, atom.position.y + speed), Direction.SW))
    elif atom.direction == Direction.NW:
        return bounceAtom(Atom(Point(atom.position.x - speed, atom.position.y - speed), Direction.NW))
    else:
        raise Exception('Unexpected value for direction: ' + str(atom.direction.value))
        
def distance(pos1, pos2):
    return math.sqrt(pow(pos1.x - pos2.x, 2) + pow(pos1.y - pos2.y, 2))

moving = True

def mouseClicked():
    if mouseButton == LEFT:
        global atoms

        positions = []

        atoms = []

        for i in range(level + 1):
            pos = getNewPos(positions)
            positions.append(pos)
            dir = Direction(int(random(4)))
            atoms.append(Atom(pos, dir))
    
    if mouseButton == RIGHT:
        pass

def draw():
    global atoms
    global moving
    
    # draw the board
    background(192)
    
    stroke(0)
    for x in range(gameDimensions.width)[1:]:
        screenX = margin + x * gridSize
        line(screenX, margin, screenX, screenSize.height - margin)
        
    for y in range(gameDimensions.height)[1:]:
        screenY = margin + y * gridSize
        line(margin, screenY, screenSize.width - margin, screenY)
        
    stroke(0, 0, 255)
    for x in [0, gameDimensions.width]:
        screenX = margin + x * gridSize
        line(screenX, margin, screenX, screenSize.height - margin)
        
    for y in [0, gameDimensions.height]:
        screenY = margin + y * gridSize
        line(margin, screenY, screenSize.width - margin, screenY)
    
    # move the balls
    atoms = map(moveAtom, atoms)
    
    # collision detection
    num = 1
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            posi = atoms[i].position
            posj = atoms[j].position
            deltax = posi.x - posj.x
            angle = math.degrees(math.atan(float(posi.y - posj.y) / float(deltax))) if abs(deltax) > 0 else 90
            pushStyle()
            fill(255, 0, 0)
            textSize(24)
            text("atom[%d]<->atom[%d] (distance = %d; angle = %d)" %(i, j, distance(posi, posj), angle), 18, 18 * num)
            popStyle()
            num += 1
            if atoms[i].direction != atoms[j].direction and distance(posi, posj) < 2:
                if atoms[i].direction.opposite() == atoms[j].direction:
                    println("Opposing!")
                    moving = False
                    # the atoms are moving in opposite directions, determine if they should bounce it reverse directions or at right angles
                    println("Angle: atain((" + str(posi.y) + " - " +  str(posj.y) +") / (" + str(posi.x) + " - " +  str(posj.x) + ")) = " + str(angle))
                    if atoms[i].direction == Direction.SE or atoms[j].direction == Direction.SE:
                        if angle > 45 or angle < -67.5:
                            # glance bounce vertically
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.flipVertical())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.flipVertical())
                        elif angle >= -67.5 and angle < -22.5:
                            # direct repel
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.opposite())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.opposite())
                        elif angle >= -22.5 and angle < 45:
                            # glancing bounce horizontally
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.flipHorizontal())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.flipHorizontal())
                    else:
                        if angle < -45 or angle > 67.5:
                            # glance bounce vertically
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.flipVertical())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.flipVertical())
                        elif angle <= 67.5 and angle > 22.5:
                            # direct repel
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.opposite())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.opposite())
                        elif angle < 22.5 and angle > -45:
                            # glancing bounce horizontally
                            atoms[i] = Atom(atoms[i].position, atoms[i].direction.flipHorizontal())
                            atoms[j] = Atom(atoms[j].position, atoms[j].direction.flipHorizontal())
        
    # draw the balls
    noStroke()
    lights()
    translate(margin, margin, 0)
    position = Point(0, 0)
    atomNum = 0
    for atom in atoms:
        newPosition = Point(atom.position.x * gridSize, atom.position.y * gridSize)
        translate(newPosition.x - position.x,  newPosition.y - position.y, 0)
        position = newPosition
        sphere(gridSize) # / 2.0
        textSize(32)
        text(str(atomNum), 32, 24)
        atomNum += 1
