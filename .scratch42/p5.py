from pxr import Tf, Usd
print(Tf.Debug.IsDebugSymbolNameEnabled("USD_STAGE_OPEN"), Tf.Debug.IsDebugSymbolNameEnabled("USD_CHANGES"))
s = Usd.Stage.CreateInMemory()
