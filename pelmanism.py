import pyxel
import random

GAME_WIDTH  = 160
GAME_HEIGHT = 120

class CellSubject:
    def __init__(self) :
        self.observers = []
    
    def subscribe(self, observer):
        self.observers.append(observer)
    
    def notify(self, mark):
        for observer in self.observers:
            observer(mark)

class Player:
    def __init__(self, cellCount):
        self.allCellsNum  = cellCount*cellCount
        self.gatherdMarks = []
        self.prevItem     = None
        self.targetItem   = None
        self.opendCount   = 0
        self.frame        = 0
        self.nextReservedFrame   = -1

    def draw(self):
        self.drawOpendCount()
        self.drawCongratulations()
        self.frame += 1

    def update(self):
        self.updateClosingProcess()
    
    def drawOpendCount(self):
        pyxel.text(5, 5, str(self.opendCount), 9)
        pyxel.text(20, 5,  'Clicked!', 8)

    def drawCongratulations(self):
        if self.isCompleted() and self.frame % 5 == 0:
            pyxel.text(GAME_WIDTH/2, GAME_HEIGHT-20,  'Congratulations!', 13)
    
    def openCell(self, cell):
        if self.isCompleted() :
            return
        cell.isOpend = True
        if self.canGetItem(cell):
            self.gatherdMarks.append(cell.mark)
            cell.isGatherd = True
            self.prevItem.isGatherd = True
        self.storeOpendCount()
        self.closeOpendCellIfNecessary(cell)

    def isCompleted(self):
        if self.allCellsNum % 2 == 0:
            return self.allCellsNum == (len(self.gatherdMarks)*2)
        else :
            return self.allCellsNum == (len(self.gatherdMarks)*2)+1
    
    def canGetItem(self, targetItem):
        if self.prevItem is not None:
            return self.prevItem.mark == targetItem.mark
        return False

    def storeOpendCount(self):
        self.opendCount += 1

    def closeOpendCellIfNecessary(self, cell):
        if self.opendCount % 2 == 0:
            self.reserveClosingProcess(cell)
        else:
            #Note:奇数時に前回のアイテムを保存するが、メソッド名と内容があっていないので要修正
            self.prevItem = cell
    
    def reserveClosingProcess(self, cell):
        #集められたということは、消す必要がないのでこの処理は虫する
        if cell.isGatherd: 
            return
        Cell.isVisibleTime = True
        self.targetItem        = cell
        self.nextReservedFrame = self.frame + 45#Note:45は適当な数字

    def updateClosingProcess(self):
        if Cell.isVisibleTime and self.frame >= self.nextReservedFrame:
            self.targetItem.isOpend = False
            self.prevItem.isOpend = False
            self.prevItem   = None
            self.targetItem = None
            Cell.isVisibleTime = False



class Cell:
    isVisibleTime = False
    def __init__(self, mark, size, x, y, baseX, baseY):
        self.mark = mark
        self.size = size
        self.x = x
        self.y = y
        self.baseX = baseX
        self.baseY = baseY
        self.subject = CellSubject()
        self.isOpend = False
        self.isGatherd = False
        
    @property
    def top(self):
        return  self.baseY + (self.y * self.size)

    @property
    def bottom(self):
        return  self.baseY + (self.y * self.size) + self.size
    
    @property
    def left(self):
        return  self.baseX + (self.x * self.size)

    @property
    def right(self):
        return  self.baseX + (self.x * self.size) + self.size

    
    @property
    def centerX(self):
        return  (self.right - self.left)

    @property
    def centerY(self):
        return  (self.top - self.bottom)

    def update(self):
        self.updateInput();

    def updateInput(self):
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and self.isHit() and not (self.isOpend or self.isGatherd) and not Cell.isVisibleTime :
            self.subject.notify(self)

    def draw(self):
        self.drawPointedRect()
        self.drawCheckMark()
    
    def drawPointedRect(self):
        if self.isHit():
            pyxel.rect(self.left + 1, self.top + 1, self.right - 1, self.bottom - 1, 12)

    def drawCheckMark(self):
        if self.isOpend or self.isGatherd:
            pyxel.text(self.left + self.size/2, self.top + self.size/2, self.mark, 2)

    def isHit(self):
        return not(self.top >= pyxel.mouse_y or self.bottom <= pyxel.mouse_y or self.left >= pyxel.mouse_x or self.right <= pyxel.mouse_x)

class GameField:
    def __init__(self, cellsCount, size, width, height):
        self.cellsCount = cellsCount
        self.width  = width
        self.height = height
        self.size   = size
        self.x      = (self.width-self.size)/2
        self.y      = (self.height-self.size)/2
        self.cells  = self.createCells()
        self.player = Player(self.cellsCount)

    def update(self):
        self.player.update()
        for cell in self.cells:
            cell.update()

    def draw(self):
        self.drawBorad()
        self.drawLines()
        self.player.draw()
        #子要素を描画
        for cell in self.cells:
            cell.draw()

    def drawBorad(self) :
        pyxel.cls(0)
        pyxel.rect(self.x, self.y, self.x + self.size, self.y + self.size, 3)
    
    def drawLines(self) :
        padding = self.size/self.cellsCount
        xLength = self.x + self.size
        yLength = self.y + self.size
        self.drawVerticalLine(padding, xLength)
        self.drawHorizontalLine(padding, yLength)

    def drawVerticalLine(self, padding, xLength):
        for i in range(self.cellsCount-1):
            pyxel.line(self.x, self.y + padding*(i+1), xLength, self.y + padding*(i+1), 4)

    def drawHorizontalLine(self, padding, yLength):
        for i in range(self.cellsCount-1):
            pyxel.line(self.x + padding*(i+1), self.y, self.x + padding*(i+1), yLength, 4)

    def createAlphabetCollection(self):
        #hack:もっと綺麗な作成方法があるはず。
        return ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D', 'E', 'E', 'F', 'F', 'G', 'G',
         'H', 'H', 'I', 'I', 'J', 'J', 'K', 'K', 'L', 'L', 'M', 'M', 'N', 'N', 'O', 'O',
          'P', 'P', 'Q', 'Q', 'R', 'R', 'S', 'S', 'T', 'T', 'U', 'U', 'V', 'V', 'W', 'W', 'Z'
          '1', '1', '2', '2', '3', '3', '4', '4', '5', '5', '6', '6', '7', '7', '8', '8', '9', '9']
    
    def createCells(self):
        cells = []
        maxCount = (self.cellsCount*self.cellsCount)
        alphabets = self.createAlphabetCollection()
        while len(cells) != maxCount:
            x = random.randint(0, self.cellsCount - 1)
            y = random.randint(0, self.cellsCount - 1)
            if all((cell.x != x or cell.y != y) for cell in cells):
                newCell = Cell(alphabets.pop(0), self.size/self.cellsCount, x, y, self.x, self.y)
                newCell.subject.subscribe(lambda mark:self.player.openCell(mark))
                cells.append(newCell)
        return cells

class App:
    def __init__(self):
        #幅と高さを設定して初期化
        pyxel.init(GAME_WIDTH, GAME_HEIGHT, scale=4)
        pyxel.mouse(True)
        self.initializeGameField()
        #ゲーム開始
        pyxel.run(self.update, self.draw)

    def update(self):
        self.updateInput()
        self.gameField.update()

    def draw(self):
        self.gameField.draw()
    
    def updateInput(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.initializeGameField()
    
    def initializeGameField(self):
        self.gameField = GameField(5, 70, GAME_WIDTH, GAME_HEIGHT)

App()