from pxr import Usd, Sdf
open("sub.usda","w").write('#usda 1.0\ndef "S" { double v.timeSamples = { 0: 0, 10: 10, }\n}\n')
open("root.usda","w").write('#usda 1.0\n(\n subLayers = [\n @./sub.usda@ (offset = 100; scale = 0.5)\n ]\n startTimeCode = 1\n endTimeCode = 240\n framesPerSecond = 24\n timeCodesPerSecond = 24\n)\n')
s = Usd.Stage.Open("root.usda")
print(s.GetAttributeAtPath("/S.v").GetTimeSamples())
print(s.GetRootLayer().subLayerOffsets)
print(s.GetStartTimeCode(), s.GetEndTimeCode(), s.GetFramesPerSecond(), s.GetTimeCodesPerSecond(), s.HasAuthoredTimeCodeRange())
s.SetStartTimeCode(1001); s.SetEndTimeCode(1100)
print(s.GetRootLayer().startTimeCode)
print([n for n in dir(Usd.Stage) if 'Time' in n or 'Interp' in n or 'Frame' in n])
# default + samples in usda
l = Sdf.Layer.CreateAnonymous(".usda")
l.ImportFromString('#usda 1.0\ndef "A"\n{\n    double h = 1\n    double h.timeSamples = {\n        1.5: 2,\n        24: 3,\n    }\n}\n')
st = Usd.Stage.Open(l)
a = st.GetAttributeAtPath("/A.h"); print(a.Get(), a.Get(1), a.Get(1.5), a.GetTimeSamples(), a.GetResolveInfo(Usd.TimeCode.Default()).GetSource(), a.GetResolveInfo(5).GetSource())
print(l.ListAllTimeSamples(), l.ListTimeSamplesForPath("/A.h"), l.QueryTimeSample("/A.h", 24))
ci = Usd.TimeCode.SafeStep.__doc__
print(Usd.TimeCode.SafeStep())
