# qgis-next-feature-helper.py
# Helper script to go through non-hidden polygon features

def GetFIDList(lyr):
    # Filtering expression, we only want visible features
    expr = QgsExpression("hidden != 1")
    feats = lyr.getFeatures(QgsFeatureRequest(expr))
    # FIDs of visible features
    return [f.id() for f in feats]

def SelectFID(fid):
    # Clear selection
    lyr.removeSelection()
    # Make new selection
    lyr.select(fid)

def SelectNext(indexDir):
    global currFID
    # Get the FID value + index direction away
    currFID = fidList[fidList.index(currFID) + indexDir]
    # Select the new FID value
    SelectFID(currFID)

def PanToNextFeature(indexDir):
    try:
        SelectNext(indexDir)
        canvas.panToSelected(lyr)
    except:
        print("Action failed")

# Get the current canvas
canvas = iface.mapCanvas()
try:
    # Get the current layer. Needs to be a vector!
    lyr = iface.activeLayer()
    fidList = GetFIDList(lyr)
    currFID = fidList[0]
    SelectFID(currFID)
    canvas.panToSelected(lyr)
except:
    print("Initialization failed.")

