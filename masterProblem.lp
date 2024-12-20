\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x93a3df7a5208bfb8
Minimize
  - 4 x0 - 7 x1 - x2 - 3 x3 - 3 x4 + 0.3333333333333333 theta0
   + 0.3333333333333333 theta1 + 0.3333333333333333 theta2
Subject To
 R0: - 8 x0 - 8 x1 - 8 x2 - 8 x3 - 8 x4 + theta0 >= -32
 R1: - 8 x0 - 8 x1 - 8 x2 - 8 x3 - 8 x4 + theta1 >= -32
 R2: - 8 x0 - 8 x1 - 8 x2 - 8 x3 - 8 x4 + theta2 >= -32
 R3: - x0 - x1 + x2 - x3 - x4 + theta0 >= -3
 R4: - 4 x0 - 4 x1 + 4 x2 - 4 x3 - 4 x4 + theta1 >= -12
 R5: - 4 x0 - 4 x1 + 4 x2 - 4 x3 - 4 x4 + theta2 >= -12
 R6: - 7 x0 - 7 x1 - 7 x2 - 7 x3 + 7 x4 + theta0 >= -21
 R7: - 7 x0 - 7 x1 - 7 x2 - 7 x3 + 7 x4 + theta1 >= -21
 R8: - 7 x0 - 7 x1 - 7 x2 - 7 x3 + 7 x4 + theta2 >= -21
 R9: - 8 x0 - 8 x1 - 8 x2 + 8 x3 - 8 x4 + theta0 >= -24
 R10: - 8 x0 - 8 x1 - 8 x2 + 8 x3 - 8 x4 + theta1 >= -24
 R11: - 8 x0 - 8 x1 - 8 x2 + 8 x3 - 8 x4 + theta2 >= -24
 R12: x0 - x1 - x2 - x3 - x4 + theta0 >= -3
 R13: x0 - x1 - x2 - x3 - x4 + theta1 >= -3
 R14: x0 - x1 - x2 - x3 - x4 + theta2 >= -3
 R15: - 3 x0 - 3 x1 + 3 x2 - 3 x3 + 3 x4 + theta1 >= -6
 R16: - 3 x0 - 3 x1 + 3 x2 - 3 x3 + 3 x4 + theta2 >= -6
Bounds
 theta0 <= 10000
 theta1 <= 10000
 theta2 <= 10000
Binaries
 x0 x1 x2 x3 x4
End
