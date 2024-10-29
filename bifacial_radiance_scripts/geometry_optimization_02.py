from pyomo.environ import ConcreteModel, Var, Objective, SolverFactory, Piecewise, Constraint, minimize
import numpy as np
import math

r"""
Slightly enhanced optimization also incuding the bifaciality factor, 
but it is not working with cbc because of non-linearity
"""

# Define the model
model = ConcreteModel()

# Input: Latitude (George Town)
lat = 6

# Input parameters
y = 1.74  # module length (y = N/S)
x = 1.036  # module width (x = E/W)
min_slope = 0.25 / 12  # IBC minimum slope for proper rainwater runoff
min_tilt = math.ceil(math.degrees(math.atan(min_slope)))
tilt = max(round(abs(lat)), min_tilt)  # should ideally be close to latitude, but allow for rainwater runoff
rad_tilt = math.radians(tilt)
min_solar_angle = 90 - round(
    abs(lat)) - 23.5  # minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
rad_min_solar_angle = math.radians(min_solar_angle)
min_ygap = y * np.sin(rad_tilt) / np.tan(
    rad_min_solar_angle)  # minimum pitch to prevent the panels from shading each other
pitch = round(y + 1.5 * min_ygap, 2)  # pitch is module length + 1.5 times minimum ygap   ## TO BE OPTIMIZED

# iteration results from bifacial radiance (George Town)
xgaps = [0, 1, 2, 3, 4, 5]  # [m]
fshadings = [0.220319439, 0.565189071, 0.688755063, 0.760388298, 0.796953448, 0.825899627]  # [-]
fbifacials = [0.078295417, 0.12392022, 0.148550429, 0.160079754, 0.167985713, 0.172557357]  # [-]

for i in range(len(xgaps)):
    ler_check = x / (xgaps[i] + x) + fshadings[i]
    print(ler_check)

# Decision variable: xgap
model.xgap = Var(bounds=(xgaps[0], xgaps[-1]))

# Setting up the Piecewise functions for shading and bifaciality factors
model.fshading = Var()
model.fshading_pieces = Piecewise(model.fshading, model.xgap,
                                  pw_pts=xgaps,
                                  f_rule=fshadings,
                                  pw_constr_type='EQ')

model.fbifacial = Var()
model.fbifacial_pieces = Piecewise(model.fbifacial, model.xgap,
                                   pw_pts=xgaps,
                                   f_rule=fbifacials,
                                   pw_constr_type='EQ')


# Objective: Maximize LER
def objective_rule(model):
    return 2 + ((1 + model.fbifacial) * model.xgap) / ((1 + fbifacials[0]) * x) - model.fshading


model.objective = Objective(rule=objective_rule, sense=minimize)

# Solver
solver = SolverFactory('cbc')  # use CBC solver
result = solver.solve(model)

# Output results
xgap_optimal = model.xgap.value
fshading_optimal = model.fshading.value
fbifacial_optimal = model.fbifacial.value
area_pv = x * pitch * (1 + fbifacials[0])
area_apv_optimal = (x + xgap_optimal) * pitch * (1 + fbifacial_optimal)
ler_optimal = area_pv / area_apv_optimal + fshading_optimal

print(f"Optimal xgap: {xgap_optimal}")
print(f"Optimal Shading Factor: {fshading_optimal}")
print(f"Optimal Bifaciality Factor: {fbifacial_optimal}")
print(f"Normal PV area: {area_pv}")
print(f"Optimal APV area: {area_apv_optimal}")
print(f"Optimal LER: {ler_optimal}")
