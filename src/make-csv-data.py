#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'IOSS Reader'
breederpin_oute = IOSSReader(registrationName='breeder-pin_out.e', FileName=['/home/adubas/git.hub/auto-breeder-pin/src/breeder-pin_out.e'])
breederpin_oute.ElementBlocks = ['fluid', 'breeder']
breederpin_oute.NodeBlockFields = ['p', 'velocity_', 'velocity_magnitude']
breederpin_oute.NodeSets = []
breederpin_oute.SideSets = []

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()
animationScene1.GoToLast()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# get layout
layout1 = GetLayout()

# split cell
layout1.SplitHorizontal(0, 0.5)

# set active view
SetActiveView(None)

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024

# assign view to a particular cell in the layout
AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=2)

# show data in view
breederpin_outeDisplay = Show(breederpin_oute, spreadSheetView1, 'SpreadSheetRepresentation')

# update the view to ensure updated data information
spreadSheetView1.Update()

# Properties modified on spreadSheetView1
spreadSheetView1.HiddenColumnLabels = ['Block Number', 'Block Name', 'Point ID', 'Points_Magnitude', 'ids', 'velocity__Magnitude', 'velocity_magnitude']

# export view
ExportView('/home/adubas/git.hub/auto-breeder-pin/src/breeder-pin_fields.csv', view=spreadSheetView1)
