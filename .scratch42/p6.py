import sys
from pxr import Tf, Usd
Tf.Debug.SetOutputFile(sys.__stderr__)
Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)
s = Usd.Stage.CreateInMemory()
s.DefinePrim("/A")
print("PYDONE")
