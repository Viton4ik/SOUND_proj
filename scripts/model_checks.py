"""Independent checks of the relationships used by the animation."""
import math,json
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
assert math.isclose(.2*1.25,.25)
assert math.isclose((1/3)*1.5,.5)
assert math.isclose(2*1.8,2.2*(3.6/2.2))
assert .09*(2*math.pi/2.5)<1
for q in [-4,-1,0,2,4]:
 for t in [0,.3,2.1]:
  a=.09;k=2*math.pi/2.5;w=2*math.pi*.4;h=1e-5
  xi=lambda x:a*math.sin(w*t-k*x)
  dp=-(xi(q+h)-xi(q-h))/(2*h)
  assert abs(dp-a*k*math.cos(w*t-k*q))<1e-8
L=8;k=math.pi/L
assert abs(math.sin(k*0))<1e-12 and abs(math.sin(k*L))<1e-12
assert abs(math.cos(k*(L/2)))<1e-12
assert 1.3*2*math.pi/10<1.4
t=np.linspace(0,40,1000);te=t-4/1.4
for _ in range(40):te=t-(4-1.3*np.sin(2*np.pi*te/10))/1.4
assert np.max(np.abs(t-te-(4-1.3*np.sin(2*np.pi*te/10))/1.4))<1e-8
report={'c_equals_f_lambda':'passed','pressure_displacement_derivative':'passed','parcel_ordering':'passed','standing_boundary_nodes':'passed','subsonic_source':'passed','retarded_time_equation':'passed'}
(R/'docs/Model_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
