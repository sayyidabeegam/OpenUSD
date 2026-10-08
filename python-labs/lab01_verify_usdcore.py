"""Lab 01 — Install and verify usd-core (USD 26.08)."""
import shutil
from pxr import Usd, UsdGeom, UsdShade, UsdLux

print("USD version:", Usd.GetVersion())
print("has UsdGeom:", bool(UsdGeom.Sphere))
print("has UsdShade:", bool(UsdShade.Material))
print("has UsdLux:", bool(UsdLux.DistantLight))
print("usdcat on PATH:", bool(shutil.which("usdcat")))
print("usdview on PATH:", bool(shutil.which("usdview")))
