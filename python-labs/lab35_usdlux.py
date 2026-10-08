"""Lab 35 — Distant 50000 vs Sphere 1; LightAPI built-in; exposure."""
from pxr import Usd, UsdLux

stage = Usd.Stage.CreateInMemory()
sun = UsdLux.DistantLight.Define(stage, "/Lights/Sun")
bulb = UsdLux.SphereLight.Define(stage, "/Lights/Bulb")
print("distant I:", sun.GetIntensityAttr().Get())
print("sphere I:", bulb.GetIntensityAttr().Get())
print("HasAPI LightAPI:", sun.GetPrim().HasAPI(UsdLux.LightAPI))
print("applied:", list(sun.GetPrim().GetAppliedSchemas()))
print("distant boundable:", sun.GetPrim().IsA(UsdLux.BoundableLightBase))
print("sphere boundable:", bulb.GetPrim().IsA(UsdLux.BoundableLightBase))
print("sun angle:", round(sun.GetAngleAttr().Get(), 2))
api = UsdLux.LightAPI(bulb.GetPrim())
api.GetIntensityAttr().Set(3)
api.GetExposureAttr().Set(2)
print("bulb I/E:", api.GetIntensityAttr().Get(),
      api.GetExposureAttr().Get())
print("scale intensity*2**exposure:",
      api.GetIntensityAttr().Get() * (2 ** api.GetExposureAttr().Get()))
print("enableColorTemp fallback:",
      api.GetEnableColorTemperatureAttr().Get())
