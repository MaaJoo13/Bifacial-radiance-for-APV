from pyomo.environ import ConcreteModel, Var, Objective, SolverFactory, Piecewise, Constraint, maximize
import numpy as np
import math

r"""
1-dimensional optimization incuding the bifaciality factor, shading factor and 
apv area requirement relative to normal pv area, 
non-linear functions are approximated as piecewise linear functions betweeen iteration results
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

print("*** fshading control sequence ***")
for i in fshadings:
    print(i)

print("*** fbifacials control sequence ***")
for i in fbifacials:
    print(i)

# Convert the non-linear term to a piecewise linear function 'farea'
fareas = [(1 + fbifacials[i]) * x / ((1 + fbifacials[0]) * (x + xgaps[i])) for i in range(len(xgaps))]
print("*** farea control sequence ***")
for i in fareas:
    print(i)

# Control sequence to calculate the LERs for the given results
print("*** LER control sequence ***")
for i in range(len(xgaps)):
    ler_check = (1 + fbifacials[i]) * x / ((1 + fbifacials[0]) * (x + xgaps[i])) + fshadings[i]
    print(ler_check)

# Decision variable: xgap
model.xgap = Var(bounds=(xgaps[0], xgaps[-1]))

# Setting up the Piecewise functions for shading and area terms
model.fshading = Var()
model.fshading_pieces = Piecewise(model.fshading, model.xgap,
                                  pw_pts=xgaps,
                                  f_rule=fshadings,
                                  pw_constr_type='EQ')

model.farea = Var()
model.farea_pieces = Piecewise(model.farea, model.xgap,
                               pw_pts=xgaps,
                               f_rule=fareas,
                               pw_constr_type='EQ')

# Minimum shading constraint
min_fshading = 0.5
model.min_shading_constraint = Constraint(expr=model.fshading >= min_fshading)


# Objective: Maximize LER
def objective_rule(model):
    return model.farea + model.fshading


model.objective = Objective(rule=objective_rule, sense=maximize)

# Solver
solver = SolverFactory('cbc')  # use CBC solver
result = solver.solve(model)

# Output results
xgap_optimal = model.xgap.value
fshading_optimal = model.fshading.value
farea_optimal = model.farea.value
fbifacial_optimal = ((farea_optimal * (1 + fbifacials[0]) * (xgap_optimal + x)) / x) - 1
ler_optimal = farea_optimal + fshading_optimal

print("*** general results ***")
print(f"Optimal xgap: {xgap_optimal}")
print(f"Optimal Shading Factor: {fshading_optimal}")
print(f"Optimal non-linear 'area' term: {farea_optimal}")
print(f"Optimal Bifaciality Factor: {fbifacial_optimal}")
print(f"Optimal LER: {ler_optimal}")
