#matplotlib inline

import sympy as sp
from sympy.plotting import plot, plot_parametric
import matplotlib.pyplot as plt
from IPython.core.display import HTML
from IPython.display import display
from sympy import Derivative, Eq, dsolve

t = sp.symbols('t')
y = sp.symbols('y',cls=sp.Function)
lambda0, omega0 = sp.symbols("lambda_0 omega_0")
eq0 = Derivative(y(t),t,t) + 2*lambda0*Derivative(y(t),t) + omega0**2*y(t)
display("EDO ",eq0)

Valnum={lambda0:1/sp.S(4),omega0:1}
Delta = float((lambda0*2-omega0**2).subs(Valnum))
CI={y(0):1,Derivative(y(t),t).subs(t,0):0}
sol = dsolve(eq0.subs(Valnum),ics=CI)
display("solution :",sol)
y1 = sol.rhs
y2 = y1.diff(t)
plot_parametric((y1,y2),(t,0,10),title="trajectoire espace des phases (avec amortissement)")