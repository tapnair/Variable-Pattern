#Author-Patrick Rainsberry
#Description-Generates a helical curve

import adsk.core, adsk.fusion, traceback
import math


# global event handlers referenced for the duration of the command
handlers = []

commandName = 'Variable Pattern'
commandDescription = 'Create a Helix Curve'
command_id = 'cmd_vpattern'
menu_panel = 'SolidCreatePanel'
commandResources = './resources'

def patternMaker(inputs):
    ui = None
    
    try:
        # We need access to the inputs within a command during the execute.
        for input in inputs:
            if input.id == 'intialSpacing':
                initial = input.value
            elif input.id == 'increment':
                increment = input.value
            elif input.id == 'BodySelect':
                body = input.selection(0).entity
            elif input.id == 'direction':
                edge = adsk.fusion.BRepEdge.cast(input.selection(0).entity) 
            elif input.id == 'number':
                number = input.value
                    
        # Get Fusion Objects                    
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        
        # Get the root component of the active design.
        rootComp = design.rootComponent
        features = rootComp.features
        
        movement = initial
        
        (returnValue, startPoint, endPoint) = edge.geometry.evaluator.getEndPoints()              
                
        vector = adsk.core.Vector3D.create(endPoint.x - startPoint.x, endPoint.y - startPoint.y, endPoint.z - startPoint.z )
        
        for i in range (number-1):
                        
            newBody = body.copyToComponent(rootComp)
            
            
            # Create a collection of entities for move
            entities1 = adsk.core.ObjectCollection.create()
            entities1.add(newBody)            
            
            # Create Vector for direction
            vector.normalize()
            vector.scaleBy(movement)
            
            # Create a transform to do move
            transform = adsk.core.Matrix3D.create()
            transform.translation = vector
            
            # Create a move feature
            moveFeats = features.moveFeatures
            moveFeatureInput = moveFeats.createInput(entities1, transform)
            moveFeats.add(moveFeatureInput)
            
            # Increment Spacing Value
            movement += increment*(i+1)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
            
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Handle the input changed event.        
        class executePreviewHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                app = adsk.core.Application.get()
                ui  = app.userInterface
                try:
                    cmd = args.firingEvent.sender
                    inputs = cmd.commandInputs
                    
                    
                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'
                        .format(traceback.format_exc()))
                        
        # Handle the execute event.
        class CommandExecuteHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                try:  
                    # Get values from input form
                    cmd = args.firingEvent.sender
                    inputs = cmd.commandInputs
                    patternMaker(inputs)
                                        
                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'
                        .format(traceback.format_exc()))
        
        # Handle the execute event.
        class CommandCreatedEventHandlerPanel(adsk.core.CommandCreatedEventHandler):
            def __init__(self):
                super().__init__() 
            def notify(self, args):
                try:
                    product = app.activeProduct
                    design = adsk.fusion.Design.cast(product)
                    unitsMgr = design.unitsManager
                    
                    # Setup Handlers for update and execute                   
                    cmd = args.command
                    onExecute = CommandExecuteHandler()
                    cmd.execute.add(onExecute)
                    onUpdate = executePreviewHandler()
                    cmd.executePreview.add(onUpdate)
                    
                    # keep the handler referenced beyond this function
                    handlers.append(onExecute)
                    handlers.append(onUpdate)
                    
                    # Define UI Elements
                    commandInputs_ = cmd.commandInputs                
                  
                    # Add all parameters to the input form
                    # Create the Selection input to have a planar face or construction plane selected.                
                    selInput = commandInputs_.addSelectionInput('BodySelect', 'Body', 'Select body to pattern')
                    selInput.addSelectionFilter('Bodies')
                    selInput.setSelectionLimits(1,1)
                    
                    dirInput = commandInputs_.addSelectionInput('direction', 'Direction', 'Select direction for pattern')
                    dirInput.addSelectionFilter('LinearEdges')
                    dirInput.setSelectionLimits(1,1)
                    
                    initial_input = adsk.core.ValueInput.createByReal(2.54)
                    commandInputs_.addValueInput('intialSpacing', 'Initial Spacing', unitsMgr.defaultLengthUnits , initial_input)

                    increment_input = adsk.core.ValueInput.createByReal(2.54)
                    commandInputs_.addValueInput('increment', 'Increment', unitsMgr.defaultLengthUnits , increment_input)
                    
                    commandInputs_.addIntegerSpinnerCommandInput('number', 'Number', 2, 999, 1, 2)
                    
                                  
                except:
                    if ui:
                        ui.messageBox('Panel command created failed:\n{}'
                        .format(traceback.format_exc()))
                                       
        # Get the UserInterface object and the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
         
        # Create a basic button command definition.
        buttonDef = cmdDefs.addButtonDefinition(command_id, 
                                                commandName, 
                                                commandDescription, 
                                                commandResources)                                               
        # Setup Event Handler
        onCommandCreated = CommandCreatedEventHandlerPanel()
        buttonDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # Add the controls to the Inspect toolbar panel.
        modifyPanel = ui.allToolbarPanels.itemById(menu_panel)
        buttonControl = modifyPanel.controls.addCommand(buttonDef)
        buttonControl.isVisible = True
        

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        commandDef = ui.commandDefinitions.itemById(command_id)
        commandDef.deleteMe()

        panel = ui.allToolbarPanels.itemById(menu_panel)
        control = panel.controls.itemById(command_id)
        control.deleteMe()
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
