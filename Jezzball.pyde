import math


class Dimension:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)

class BallDirection:
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, BallDirection):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def opposite(self):
        if self.value == 0:
            return BallDirection.SW
        elif self.value == 1:
            return BallDirection.NW
        elif self.value == 2:
            return BallDirection.NE
        elif self.value == 3:
            return BallDirection.SE
        
    def flipVertical(self):
        if self.value == 0:
            return BallDirection.SE
        elif self.value == 1:
            return BallDirection.NE
        elif self.value == 2:
            return BallDirection.NW
        elif self.value == 3:
            return BallDirection.SW
        
    def flipHorizontal(self):
        if self.value == 0:
            return BallDirection.NW
        elif self.value == 1:
            return BallDirection.SW
        elif self.value == 2:
            return BallDirection.SE
        elif self.value == 3:
            return BallDirection.NE
        
BallDirection.NE = BallDirection(0)
BallDirection.SE = BallDirection(1)
BallDirection.SW = BallDirection(2)
BallDirection.NW = BallDirection(3)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return 0

class Atom:
    def __init__(self, position, direction, bounced = False):
        self.position = position
        self.direction = direction
        self.bounced = bounced


class DivDirection:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, DivDirection):
            return self.value == other.value
        return 0

    def __ne__(self, other):
        return not self.__eq__(other)

DivDirection.N = DivDirection(0)
DivDirection.E = DivDirection(1)
DivDirection.S = DivDirection(2)
DivDirection.W = DivDirection(3)

class Divider:
    def __init__(self, box_color, x, y, direction):
        self.box_color = box_color
        self.x = x
        self.y = y
        self.direction = direction
        self.box_progress = 1

gameDimensions = Dimension(28, 20)
gridSize = 25.0
margin = 10
level = 2

atoms = []
board = [[1 for y in range(gameDimensions.height)] for x in range(gameDimensions.width)]

screenSize = Dimension(gameDimensions.width * gridSize + margin * 2, gameDimensions.height * gridSize + margin * 2)


def setup():
    global atoms, dividers, covered_sections

    positions = []

    dividers = []

    covered_sections = []

    println("Screen: " + str(screenSize.width) + ", " + str(screenSize.height))
    size(screenSize.width, screenSize.height, P3D)
    
    for i in range(level + 1):
        pos = getNewPos(positions)
        positions.append(pos)
        dir = BallDirection(int(random(4)))
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
        direction = BallDirection.NW if direction == BallDirection.NE else BallDirection.SW
    elif bounceLeft:
        direction = BallDirection.NE if direction == BallDirection.NW else BallDirection.SE
    if bounceTop:
        direction = BallDirection.SE if direction == BallDirection.NE else BallDirection.SW
    elif bounceBottom:
        direction = BallDirection.NE if direction == BallDirection.SE else BallDirection.NW
    
    return Atom(atom.position, direction, True) if direction != atom.direction else atom

def moveAtom(atom):
    if atom.direction == BallDirection.NE:
        return bounceAtom(Atom(Point(atom.position.x + speed, atom.position.y - speed), BallDirection.NE))
    elif atom.direction == BallDirection.SE:
        return bounceAtom(Atom(Point(atom.position.x + speed, atom.position.y + speed), BallDirection.SE))
    elif atom.direction == BallDirection.SW:
        return bounceAtom(Atom(Point(atom.position.x - speed, atom.position.y + speed), BallDirection.SW))
    elif atom.direction == BallDirection.NW:
        return bounceAtom(Atom(Point(atom.position.x - speed, atom.position.y - speed), BallDirection.NW))
    else:
        raise Exception('Unexpected value for direction: ' + str(atom.direction.value))
        
def distance(pos1, pos2):
    return math.sqrt(pow(pos1.x - pos2.x, 2) + pow(pos1.y - pos2.y, 2))

moving = True

def mouseClicked():
    global rects

    if mouseButton == LEFT:
        global atoms, dividers, covered_sections

        positions = []

        dividers = []

        atoms = []

        covered_sections = []

        for i in range(level + 1):
            pos = getNewPos(positions)
            positions.append(pos)
            dir = BallDirection(int(random(4)))
            atoms.append(Atom(pos, dir))
    
    if mouseButton == RIGHT:
        divider1 = Divider((255, 0, 0), mouseX, mouseY, DivDirection.N)
        divider2 = Divider((0, 0, 255), mouseX, mouseY, DivDirection.S)
        dividers.append([divider1, divider2])

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
    # TODO: divider colision detection
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
                    if atoms[i].direction == BallDirection.SE or atoms[j].direction == BallDirection.SE:
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

    # divider logic
    translate(0 - position.x, 0 - position.y, 0)
    for divider in dividers:
        for num in [0, 1]:
            # check when to stop increasing progress
            if divider[num].direction == DivDirection.N:
                if divider[num].y - divider[num].box_progress + margin < 1:
                    divider[num].box_color = (0, 0, 0)
            elif divider[num].direction == DivDirection.S:
                if divider[num].y + divider[num].box_progress + margin > screenSize.height:
                    divider[num].box_color = (0, 0, 0)

    # draw dividers
    pushStyle()
    stroke(0, 0, 0)
    for divider in dividers:
        for num in [0, 1]:
            if divider[num].box_color != (0, 0, 0):
                divider[num].box_progress += 3
            fill(divider[num].box_color[0], divider[num].box_color[1], divider[num].box_color[2])
            if divider[num].direction == DivDirection.S:
                rect(divider[num].x, divider[num].y, 10, divider[num].box_progress)
            elif divider[num].direction == DivDirection.N:
                rect(divider[num].x, divider[num].y, 10, -divider[num].box_progress)
    popStyle()
