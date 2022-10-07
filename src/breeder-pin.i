[Mesh]
  type = FileMesh
  file = 'breeder_pin.msh'
  second_order = true
[]

[Variables]
  [./velocity]
    order = SECOND
    family = LAGRANGE_VEC
    block = 'fluid'
  [../]
  [p]
    order = FIRST
    family = LAGRANGE
    block = 'fluid'
  []
[]

[Kernels]
  [./mass]
    type = INSADMass
    variable = p
    block = 'fluid'
  [../]
  [./momentum_advection] #udu
    type = INSADMomentumAdvection
    variable = velocity
    block = 'fluid'
  [../]
  [./momentum_pressure] #dp
    type = INSADMomentumPressure
    variable = velocity
    block = 'fluid'
    p = p
    integrate_p_by_parts = false
  [../]
  [./momentum_viscous] #mud^2u
    type = INSADMomentumViscous
    variable = velocity
    block = 'fluid'
  [../]
[]

[AuxVariables]
  [velocity_magnitude]
    order = SECOND
    family = LAGRANGE
    block = 'fluid'
  []
[]

[AuxKernels]
  [velocity_magnitude]
    type = VectorVariableMagnitudeAux
    vector_variable = velocity
    variable = velocity_magnitude
    block = 'fluid'
  []
[]

[Postprocessors]
  [p_drop]
    type = ElementExtremeValue
    variable = p
    block = 'fluid'
  []
  [ave_v_out]
    type = SideAverageValue
    variable = velocity_magnitude
    boundary = 'outlet'
  [../]
  [ave_p_in]
    type = SideAverageValue
    variable = p
    boundary = 'inlet'
  [../]
  [breeder_area]
    type = VolumePostprocessor
    block = 'breeder'
  []
[]
  
[ICs]
  [./velocity_init]
    type = VectorConstantIC
    x_value = 1e-15
    y_value = 1e-15
    z_value = 0
    variable = velocity
  [../]
[]

[BCs]
  [./NoSlip]
    type = VectorDirichletBC
    variable = velocity
    boundary = 'noslip'
    values = '0.0 0.0 0.0'
  [../]
  [inlet]
    type = VectorDirichletBC
    variable = velocity
    boundary = 'inlet'
    values = '0 10.0 0.0'
  []
  [outlet]
    type = DirichletBC
    variable = p
    boundary = 'outlet'
    value = 0.0
  []
[]

[Materials]
  [./fuel]
    type = ADGenericConstantMaterial
    block = 'fluid'
    prop_names =  'mu        rho  '
    prop_values = '1  1' # Ns/m^2 kg/m^3 W/m^2K W/mK J/kgK
  [../]
  [./ins_mat]
    type = INSADMaterial
    velocity = velocity
    pressure = p
    block = 'fluid'
  [../]
[]

[Problem]
  type = FEProblem
  kernel_coverage_check = false
  material_coverage_check = false
[]

[Preconditioning]
  [./SMP_PJFNK]
    type = SMP
    full = true
    petsc_options_iname = '-ksp_gmres_restart -pc_type -sub_pc_type -sub_pc_factor_levels'
    petsc_options_value = '200                bjacobi       ilu          4'
  [../]
[]

[Executioner]
  type = Steady
  solve_type = 'NEWTON'
  line_search = none
  nl_rel_tol = 1e-8
  nl_max_its = 20
  l_tol = 1e-6
  l_max_its = 200
[]

[Outputs]
  csv = true
  exodus = true
[]

