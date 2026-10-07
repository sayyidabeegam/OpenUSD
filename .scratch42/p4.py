import os
os.environ["TF_DEBUG"] = "USD_STAGE_OPEN"
from pxr import Tf, Usd
print(Tf.Debug.IsDebugSymbolNameEnabled("USD_STAGE_OPEN"))
