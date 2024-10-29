from pyomo.environ import ConcreteModel, Var, Objective, maximize, SolverFactory, Constraint, Piecewise

# iteration results for Timbutu (EPW file created for Accra!)
xgaps = [0, 1, 2, 3, 4]
ygaps = [0.43, 1.43, 2.43, 3.43, 4.43]
fbifacials = [[0.07315816297197425, 0.12438797038025352, 0.15162880895663333, 0.16778144976103446, 0.17743087325990717],
              [0.14102054921236892, 0.17128667336464343, 0.1866175816092834, 0.19615131378465925, 0.20231735040165422],
              [0.17124074216997903, 0.19216015518772228, 0.20271543329247482, 0.20818353255623506, 0.21218554550428725],
              [0.18624505956788184, 0.20304212905505076, 0.21078686053306597, 0.2151103326939779, 0.21883739693756268],
              [0.19528478843014338, 0.20942269090218532, 0.2170744268611935, 0.21921349472118656, 0.2219012079593967]]
fshadings = [[0.23573326662682556, 0.4692011507136313, 0.5954538794124272, 0.6729192817850619, 0.7212096998365392],
             [0.5894223381703464, 0.7127490377753292, 0.7854884809957661, 0.8251223635413244, 0.8514350320987707],
             [0.7215416956991182, 0.8112725470721311, 0.8557295738572378, 0.8820613154825734, 0.8997511165076453],
             [0.7891339107648374, 0.8549814886803768, 0.891411364826752, 0.9103608480974668, 0.9236925586024758],
             [0.8305577553699706, 0.8817206797734228, 0.9120468471680767, 0.9254646132877465, 0.9357765497263257]]

# Initialize the model
model = ConcreteModel()

# Decision variables
model.xgap = Var(bounds=(min(xgaps), max(xgaps)))
model.ygap = Var(bounds=(min(ygaps), max(ygaps)))

# Variable for the interpolated fshading value
model.fshading = Var()

# Interpolation variables along xgap for each fixed ygap
model.fshading_x = Var(range(len(ygaps)))

# First interpolation along xgap for each ygap
for j in range(len(ygaps)):
    x_points = xgaps
    f_values = [fshadings[i][j] for i in range(len(xgaps))]
    model.add_component(f'Piecewise_fshading_x_{j}',
                        Piecewise(model.fshading_x[j], model.xgap,
                                  pw_pts=x_points,
                                  f_rule=f_values,
                                  pw_constr_type='EQ'))

# Second interpolation along ygap at the resulting fshading_x
model.add_component('Piecewise_fshading',
                    Piecewise(model.fshading, model.ygap,
                              pw_pts=ygaps,
                              f_rule={j: model.fshading_x[j] for j in range(len(ygaps))},
                              pw_constr_type='EQ'))

# Objective and constraints
model.objective = Objective(expr=model.fshading, sense=maximize)

# Solver
solver = SolverFactory('cbc')
solver.solve(model)

# Output the results
print("Optimal xgap:", model.xgap.value)
print("Optimal ygap:", model.ygap.value)
print("Optimal fshading:", model.fshading.value)