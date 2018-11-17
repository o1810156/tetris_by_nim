include tetris_library
import strutils, unicode

var
  F: Field
  pre_F: Field
  pre_score: int
  reward: int
  done: bool

proc gameInit() =
  reward = 0
  done = false
  var board: array[22, array[12, Box]]
  for i in 0..<21:
    board[i][0] = Box(isFilled: true, color: dfColor)
    board[i][11] = Box(isFilled: true, color: dfColor)
    for j in 1..<11:
      board[i][j] = Box(isFilled: false, color: dfColor)
  for i in 0..<12:
    board[21][i] = Box(isFilled: true, color: dfColor)

  var mns = @[I, O, S, Z, J, L, T]
  mns.shuffle()
  F = Field(board: board, frame: 0, minos: mns, score: 0, clearlines: 0)
  pre_F.deepCopy(F)
  F.dropStart()
  # echo "check point"

proc observer(): string =
  result = ""
  result = $(ord(F.am.kind.color)-1) & "/["
  for line in F.board[0..^2]:
    result &= "["
    for b in line[1..^2]:
      result &= $b.isFilled & ", "
    result = result[0..^3] & "], "
  result = result[0..^3] & "]/" & $reward & "/" & $done

  #]#

  # return "observer"

  # result = cast[string](result.toRunes)

# proc observer(): array[int] =
#   var
#     field_str: string = ""
#     res: string = ""
#   for line in F.board[0..^2]: # 21段
#     for b in line[1..^2]: # 10列
#       field &= $(if b.isFilled: 1 else: 0)
#   res &= $(ord(F.am.kind.color)-1) & $(if done: 1 else: 0) & $reward
#   return parseInt(res)

proc reset(): cstring {.cdecl, exportc, dynlib.} =
  gameInit()
  return observer()

proc step(action: int): cstring {.cdecl, exportc, dynlib.} =
  pre_F.deepCopy(F)
  # if done: return "gameover"
  if (action < 0) or (40 <= action):
    gameOver()
    return observer()
  pre_score = F.score
  var
    dir_ind: int = int(action / 10)
    pos_y: int = action mod 10

  F.am.dir = [north, east, south, west][dir_ind]
  F.am.renderBox()
  F.am.pos.y = pos_y
  if not F.am.posVerify(F.board):
    discard F.am.posCorrect(F.board)
  while F.am.move(F.board, down): discard
  F.fixAM()
  F.frame += 1
  if F.frame >= 14:
    gameOver()
  reward = F.score - pre_score
  return observer()
  # return observer().toRunes

proc revert() {.cdecl, exportc, dynlib.} =
  F.deepCopy(pre_F)

proc gameOver() =
  done = true