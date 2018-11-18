include tetris_library

proc alert(st: cstring) {. importc .}

var
  F: Field

# proc gameInit(): Field {. exportc .} =
proc gameInit() {. exportc .} =
  var board: array[22, array[12, Box]]
  # for i in 0..<board.len-1:
  for i in 0..<21:
    board[i][0] = Box(isFilled: true, color: dfColor)
    # board[i][board.len-1] = Box(isFilled: true, color: dfColor)
    board[i][11] = Box(isFilled: true, color: dfColor)
    # for j in 1..<board[0].len-1:
    for j in 1..<11:
      board[i][j] = Box(isFilled: false, color: dfColor)
  # for i in 0..<board[0].len:
  for i in 0..<12:
    # board[board.len-1][i] = Box(isFilled: true, color: dfColor)
    board[21][i] = Box(isFilled: true, color: dfColor)

  # result = Field(board: board, frame: 0)
  # var mns = @[I, O, S, Z, J, L, T]
  var mns = [I, O, S, Z, J, L, T, I, O, S, Z, J, L, T]
  mns.shuffle()
  F = Field(board: board, frame: 0, minos: mns, score: 0, clearlines: 0)
  F.dropStart()

var gameOverFlag = false

type
  Controller = enum
    bNon, bA, bB, bHd, bUp, bDwn, bRgt, bLft, bHld
  
  Button = ref object
    kind: Controller
    isPushed: bool
    contFlames: int

var buttons: seq[Button] = @[]

for b in Controller:
  buttons.add(Button(kind: b, isPushed: false, contFlames: 0))

proc buttonCheck(c: array[8, bool]) =

  for i, b in c:
    if not b:
      buttons[i].isPushed = false
      buttons[i].contFlames = 0

  if c[ord(bA)]:
    if not buttons[ord(bA)].isPushed:
      F.am.rightSpin(F.board)
      buttons[ord(bA)].isPushed = true
  elif c[ord(bB)]:
    if not buttons[ord(bB)].isPushed:
      F.am.leftSpin(F.board)
      buttons[ord(bB)].isPushed = true

  if c[ord(bRgt)]:
    if (not buttons[ord(bRgt)].isPushed) or buttons[ord(bRgt)].contFlames > 30:
      discard F.am.move(F.board, right)
      buttons[ord(bRgt)].isPushed = true
    else:
      buttons[ord(bRgt)].contFlames += 1
  elif c[ord(bLft)]:
    if (not buttons[ord(bLft)].isPushed) or buttons[ord(bLft)].contFlames > 30:
      discard F.am.move(F.board, left)
      buttons[ord(bLft)].isPushed = true
    else:
      buttons[ord(bLft)].contFlames += 1
  
  if c[ord(bDwn)]:
    discard F.am.move(F.board, down)
  
  if c[ord(bHd)]:
    if not buttons[ord(bHd)].isPushed:
      while F.am.move(F.board, down): discard
      F.fixAM()
      buttons[ord(bHd)].isPushed = true

proc gameStep(c: array[8, bool]) {. exportc .} =
  if gameOverFlag: return

  buttonCheck(c)
  F.frame.inc()
  F.dropStep()

proc getBoard(): Board {. exportc .} =
  var
    board = F.board
    am = F.am
  # echo repr(am.boxs)
  F.fixGhost()
  for i, bs in am.boxs:
    for j, b in bs:
      if b.isFilled:
        board[am.pos.x+i][am.pos.y+j] = b
  return board

proc getScore(): int {. exportc .} =
  F.score

proc getClearLines(): int {. exportc .} =
  F.clearlines

proc getNext(): Boxs {. exportc .} =
  var
    m = F.minos[0]
    p0 = int(len(m.shape)/2) mod 2
  result = @[]
  for _ in 0..3:
    var tmp: seq[Box] = @[]
    for _ in 0..3:
      tmp.add(Box(isFilled: false, color: dfColor))
    result.add(tmp)
  for i in 0..<len(m.shape):
    for j in 0..<len(m.shape):
      result[p0+i][p0+j] = Box(isFilled: m.shape[i][j], color: (if m.shape[i][j]: m.color else: dfColor))

proc gameOver() =
  gameOverFlag = true
  alert("gameOver!")