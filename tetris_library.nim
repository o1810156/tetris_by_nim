import sequtils
import math
import random

randomize()

const STEPFLAME = 180

type
  MinoColor = enum
    dfColor, iColor, oColor, sColor, zColor, jColor, lColor, tColor, gColor

  Direction = enum
    north, east, south, west
  
  MoveDir = enum
    up, down, right, left

  Mino = ref object
  # Mino = object
    shape: seq[seq[bool]]
    color: MinoColor
    firstPos: Pos
  
  ActiveMino = ref object
  # ActiveMino = object
    pos: Pos
    kind: Mino
    dir: Direction
    boxs: Boxs
  
  Pos = tuple[x, y: int]

  Box = ref object
  # Box = object
    isFilled: bool
    color: MinoColor
  
  Boxs = seq[seq[Box]]

  Board = array[22, array[12, Box]]

  Field = ref object
  # Field = object
    board: Board
    frame: int
    am: ActiveMino
    gm: seq[seq[Box]]
    # minos: seq[Mino]
    minos: array[14, Mino]
    score: int
    clearlines: int

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

proc renderBox(m: var ActiveMino) = # 回転後テトリミノを描写

  proc setBox(b: var Boxs, m: ActiveMino; i, j, t, s: int) =
    var itsColor = if m.kind.shape[i][j]: m.kind.color else: dfColor
    b[t][s] = Box(isFilled: m.kind.shape[i][j], color: itsColor)

  let l = len(m.kind.shape)-1
  var
    b: Boxs = @[]
    bb: seq[Box] = @[]
  for i in 0..l:
    for j in 0..l:
      bb.add(Box())
    b.add(bb)

  case m.dir:
  of north:
    for i in 0..l:
      for j in 0..l:
        setBox(b, m, i, j, i, j)
  of east:
    for i in 0..l:
      for j in 0..l:
        setBox(b, m, i, j, j, l-i)       
  of south:
    for i in 0..l:
      for j in 0..l:
        setBox(b, m, i, j, l-i, l-j)
  of west:
    for i in 0..l:
      for j in 0..l:
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
# proc fixGhost(f: var Field)

proc dropStep(f: var Field) {. exportc .} =
  if f.frame mod STEPFLAME == 0:
    # echo $f.am.pos.x & " " & $f.am.pos.y
    if not f.am.move(f.board, down):
      f.fixAM()

proc gameOver()

#[ <script>
function shuffle(array) {
    var n = array.length, t, i;

    while (n) {
        i = Math.floor(Math.random() * n--);
        t = array[n];
        array[n] = array[i];
        array[i] = t;
    }
}
</script> ]#

# proc shuffle(arr: var seq[Mino]) =
proc shuffle(arr: var array[14, Mino]) =
  var
    n = len(arr)
    t: int
    i: int

  while n > 0:
    i = int(floor(random(max=1.0) * float(n)))
    n -= 1
    (arr[n], arr[i]) = (arr[i], arr[n])

# proc shuffled(arr: seq[Mino]): seq[Mino] =
proc shuffled(arr: array[14, Mino]): array[14, Mino] =
  result = arr
  result.shuffle()

# var minos = @[I, O, S, Z, J, L, T]
# minos.shuffle()

# proc pop0(ms: var seq[Mino]): Mino =
#   result = ms[0]
#   ms = ms[1..^1]

proc pop0(ms: var array[14, Mino]): Mino =
  result = ms[0]
  for i in 0..12:
    ms[i] = ms[i+1]
  ms[13] = nil

proc dropStart(f: var Field) {. exportc .} =
  var mino: Mino = f.minos.pop0()
  # if len(f.minos) < 4:
    # f.minos.add(shuffled(@[I, O, S, Z, J, L, T]))
  var nil_num = 0
  for mi in f.minos:
    if mi == nil:
      nil_num += 1
  
  if nil_num >= 11:
    var add_minos = [I, O, S, Z, J, L, T]
    add_minos.shuffle()
    for i in (14-nil_num)..(20-nil_num):
      f.minos[i] = add_minos[i+nil_num-14]

  f.am = ActiveMino(pos: mino.firstPos, kind: mino, dir: north)
  f.am.renderBox()
  if not f.am.posVerify(f.board): gameOver()

proc lineCheck(f: var Field): int =
  result = 0
  for i, line in f.board[0..^2]:
    if line.all(proc (b: Box): bool = return b.isFilled):
      result += 1
      for t, line in f.board[0..<i]:
        f.board[t+1][1..^2] = line[1..^2]
      f.board[0][1..^2] = (var ln: seq[Box] = @[]; for _ in 0..9: ln.add(Box(isFilled: false, color: dfColor)); ln)

proc fixAM(f: var Field) =
  if not f.am.posVerify(f.board): return
  for i, bs in f.am.boxs:
    for j, b in bs:
      if b.isFilled:
        f.board[f.am.pos.x+i][f.am.pos.y+j] = b
  # echo "dropstart"
  var cllines = f.lineCheck()
  f.clearlines += cllines
  # f.score += [0, 1, 3, 6, 10][cllines]
  f.score += [0, 1, 3, 6, 9][cllines]
  f.dropStart()

proc fixGhost(f: var Field) =
  for i, line in f.board:
    for j, b in line:
      if not b.isFilled:
        f.board[i][j] = Box(isFilled: false, color: dfColor)
  var x = f.am.pos.x
  while f.am.move(f.board, down): discard
  for i, bs in f.am.boxs:
    for j, b in bs:
      if b.isFilled:
        f.board[f.am.pos.x+i][f.am.pos.y+j] = Box(isFilled: false, color: gColor)
  f.am.pos.x = x