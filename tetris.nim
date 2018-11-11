import sequtils

proc alert(st: cstring) {. importc .}

const STEPFLAME = 120

type
  MinoColor = enum
    dfColor, iColor, oColor, sColor, zColor, jColor, lColor, tColor

  Direction = enum
    north, east, south, west
  
  MoveDir = enum
    up, down, right, left

  Mino = ref object
    shape: seq[seq[bool]]
    color: MinoColor
    firstPos: Pos
  
  ActiveMino = ref object
    pos: Pos
    kind: Mino
    dir: Direction
    boxs: Boxs
  
  Pos = tuple[x, y: int]

  Box = ref object
    isFilled: bool
    color: MinoColor
  
  Boxs = seq[seq[Box]]

  Board = array[22, array[12, Box]]

  Field = ref object
    board: Board
    frame: int
    am: ActiveMino

  Controller = enum
    bNon, bA, bB, bHd, bUp, bDwn, bRgt, bLft, bHld
  
  Button = ref object
    kind: Controller
    isPushed: bool
    contFlames: int

var
  I = Mino(
    shape: @[
      @[false, false, false, false],
      @[true, true, true, true],
      @[false, false, false, false],
      @[false, false, false, false]
    ],
    color: iColor,
    firstPos: (0, 4)
  )
  O = Mino(
    shape: @[
      @[true, true],
      @[true, true]
    ],
    color: oColor,
    firstPos: (0, 5)
  )
  S = Mino(
    shape: @[
      @[false, true, true],
      @[true, true, false],
      @[false, false, false]
    ],
    color: sColor,
    firstPos: (0, 4)
  )
  Z = Mino(
    shape: @[
      @[true, true, false],
      @[false, true, true],
      @[false, false, false]
    ],
    color: zColor,
    firstPos: (0, 4)
  )
  J = Mino(
    shape: @[
      @[true, false, false],
      @[true, true, true],
      @[false, false, false]
    ],
    color: jColor,
    firstPos: (0, 4)
  )
  L = Mino(
    shape: @[
      @[false, false, true],
      @[true, true, true],
      @[false, false, false]
    ],
    color: lColor,
    firstPos: (0, 4)
  )
  T = Mino(
    shape: @[
      @[false, true, false],
      @[true, true, true],
      @[false, false, false]
    ],
    color: tColor,
    firstPos: (0, 4)
  )

proc renderBox(m: var ActiveMino) =

  # proc setBox_n(b: var Boxs, m: ActiveMino; i,j,l: int) =
  #   var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor
  #   b[i][j] = Box(isFilled: m.kind.shape[i][j], color: itsColor)
  # proc setBox_e(b: var Boxs, m: ActiveMino; i,j,l: int) =
  #   var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor    
  #   b[j][l-i] = Box(isFilled: m.kind.shape[i][j], color: itsColor)
  # proc setBox_s(b: var Boxs, m: ActiveMino; i,j,l: int) =
  #   var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor
  #   b[l-i][l-j] = Box(isFilled: m.kind.shape[i][j], color: itsColor)
  # proc setBox_w(b: var Boxs, m: ActiveMino; i,j,l: int) =
  #   var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor
  #   b[l-j][i] = Box(isFilled: m.kind.shape[i][j], color: itsColor)

  proc setBox(b: var Boxs, m: ActiveMino; i, j, t, s: int) =
    var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor
    b[t][s] = Box(isFilled: m.kind.shape[i][j], color: itsColor)

  let l = len(m.kind.shape)-1
  var
    b: Boxs
    bb: seq[Box]
  for i in 0..l:
    for j in 0..l:
      bb.add(Box())
    b.add(bb)

  case m.dir:
  of north:
    for i in 0..l:
      for j in 0..l:
        # setBox_n(b, m, i, j, l)
        setBox(b, m, i, j, i, j)
  of east:
    for i in 0..l:
      for j in 0..l:
        # setBox_e(b, m, i, j, l)
        setBox(b, m, i, j, j, l-i)       
  of south:
    for i in 0..l:
      for j in 0..l:
        # setBox_s(b, m, i, j, l)
        setBox(b, m, i, j, l-i, l-j)
  of west:
    for i in 0..l:
      for j in 0..l:
        # setBox_w(b, m, i, j, l)
        setBox(b, m, i, j, l-j, i)

  m.boxs = b

proc posVerify(m: var ActiveMino, board: Board): bool =
  for i, bs in m.boxs:
    for j, b in bs:
      if b.isFilled:
        let
          xp = m.pos.x+i
          yp = m.pos.y+j
        if xp < 0 or 21 <= xp or
            yp <= 0 or 11 <= yp:
          return false
        if board[xp][yp].isFilled:
          return false
  return true

proc posCorrect(m: var ActiveMino, board: Board): bool =
  for i in 0..<len(m.boxs):
    m.pos.y += i
    if m.posVerify(board):
      return true
    m.pos.y -= 2*i
    if m.posVerify(board):
      return true
    # m.pos.x -= i
    # if m.posVerify(board):
    #   return true
    # m.pos.x += 2*i
    # if m.posVerify(board):
    #   return true
  return false

proc spin(m: var ActiveMino, a: array[4, Direction], board: Board) =
  let pre_dir = m.dir
  m.dir = a[ord(m.dir)]
  m.renderBox()
  # m.posCorrect()
  if not m.posVerify(board):
    var pre_pos = (m.pos.x, m.pos.y)
    if not m.posCorrect(board):
      (m.pos.x, m.pos.y) = pre_pos
      m.dir = pre_dir
    m.renderBox()

proc rightSpin(m: var ActiveMino, board: Board) =
  spin(m, [east, south, west, north], board)

proc leftSpin(m: var ActiveMino, board: Board) =
  spin(m, [west, north, east, south], board)

proc move(m: var ActiveMino, board: Board, d: MoveDir): bool =
  case d:
  of right:
    m.pos.y += 1
    if not m.posVerify(board):
      m.pos.y -= 1
      return false
  of left:
    m.pos.y -= 1
    if not m.posVerify(board):
      m.pos.y += 1
      return false
  of down:
    m.pos.x += 1
    if not m.posVerify(board):
      m.pos.x -= 1
      return false
  of up:
    return false
  return true

proc fixAM(f: var Field)

proc dropStep(f: var Field) {. exportc .} =
  if f.frame mod STEPFLAME == 0:
    # echo $f.am.pos.x & " " & $f.am.pos.y
    if not f.am.move(f.board, down):
      f.fixAM()

proc gameOver()

proc shuffle(arr: seq[Mino]) {. importc .}

proc shuffled(arr: seq[Mino]): seq[Mino] =
  result = arr
  result.shuffle()

var minos = @[I, O, S, Z, J, L, T]
minos.shuffle()

proc pop0(ms: var seq[Mino]): Mino =
  result = ms[0]
  ms = ms[1..^1]

proc dropStart(f: var Field) {. exportc .} =
  var mino: Mino = minos.pop0()
  if len(minos) < 4:
    minos.add(shuffled(@[I, O, S, Z, J, L, T]))
  f.am = ActiveMino(pos: mino.firstPos, kind: mino, dir: north)
  f.am.renderBox()
  if not f.am.posVerify(f.board): gameOver()

proc lineCheck(f: var Field) =
  for i, line in f.board[0..^2]:
    if line.all(proc (b: Box): bool = return b.isFilled):
      for t, line in f.board[0..<i]:
        f.board[t+1][1..^2] = line[1..^2]
      f.board[0][1..^2] = (var ln: seq[Box] = @[]; for _ in 0..9: ln.add(Box(isFilled: false, color: dfColor)); ln)

proc fixAM(f: var Field) {. exportc .} =
  if not f.am.posVerify(f.board): return
  for i, bs in f.am.boxs:
    for j, b in bs:
      if b.isFilled:
        f.board[f.am.pos.x+i][f.am.pos.y+j] = b
  # echo "dropstart"
  f.lineCheck()
  f.dropStart()

# ===

var F: Field

# ===

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
  F = Field(board: board, frame: 0)
  F.dropStart()

var gameOverFlag = false

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
  for i, bs in am.boxs:
    for j, b in bs:
      if b.isFilled:
        board[am.pos.x+i][am.pos.y+j] = b
  return board

proc gameOver() =
  gameOverFlag = true
  alert("gameOver!")