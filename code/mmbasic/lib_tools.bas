' lib_tools.bas v0.0.1
' ---------------------
' Tools
' ---------------------------------------------------------------------------
Option Base 0
Option Explicit
Option Escape
Option Default Float

' ---------------------------------------------------------------------------
Sub lpins()
  Local integer n, p
  Local string gp$, pu$
  For n=0 To 29
    gp$ = "GP"+Str$(n, 2)
    On error skip
    p = MM.Info(pinno gp$)
    If Not MM.Errno Then
      pu$ = MM.Info(pin p)
    Else
      p=-1
      pu$=MM.ErrMsg$
    EndIf
    Print gp$; p, pu$
  Next
End Sub


' ---------------------------------------------------------------------------
                                                                                                  