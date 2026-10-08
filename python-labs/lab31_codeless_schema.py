"""Lab 31 — schema.usda parses; SchemaRegistry needs usdGenSchema."""
import shutil
from pxr import Sdf, Usd

print("usdGenSchema", shutil.which("usdGenSchema"))
sr = Usd.SchemaRegistry()
print("Cube registered",
      sr.FindConcretePrimDefinition("Cube") is not None)
print("Cube size fallback",
      sr.FindConcretePrimDefinition("Cube").GetAttributeFallbackValue(
          "size"))
print("IsConcrete Cube", sr.IsConcrete("Cube"))
print("IsAppliedAPISchema MaterialBindingAPI",
      sr.IsAppliedAPISchema("MaterialBindingAPI"))
print("Door registered",
      sr.FindConcretePrimDefinition("Door") is not None)

lyr = Sdf.Layer.CreateAnonymous(".usda")
lyr.ImportFromString("""#usda 1.0
over "GLOBAL" (
    customData = {
        string libraryName = "studio"
        bool skipCodeGeneration = 1
    }
)
{
}
class "Door" (
    inherits = </Typed>
)
{
    bool sliding = 0
}
""")
print("parsed classes:", [p.name for p in lyr.rootPrims])
print("skipCodeGeneration",
      lyr.GetPrimAtPath("/GLOBAL").customData.get("skipCodeGeneration"))
print("Door still unregistered",
      sr.FindConcretePrimDefinition("Door") is None)
