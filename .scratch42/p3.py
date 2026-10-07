import sys
from pxr import Tf, Usd, Sdf
Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)
s = Usd.Stage.CreateInMemory()
s.DefinePrim("/A")
sys.stdout.flush()
print("PYDONE")
