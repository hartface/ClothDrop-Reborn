import bpy
from . import utils



preset_values =  {
        "Heavy Cotton":
        {
            "subdivision": 32,
            "subsurf": 2,
            "wrinkles": 60,
            "folds": 50,
            "weight": 2.00,
        },

        "Leather":
        {
            "subdivision": 32,
            "subsurf": 2,
            "wrinkles": 0,
            "folds": 14,
            "weight": 8.00,
        },
        "Tablecloth":
        {
            "subdivision": 32,
            "subsurf": 2,
            "wrinkles": 2,
            "folds": 35,
            "weight": 1.00,
        },
        "Paper":
        {
            "subdivision": 14,
            "subsurf": 2,
            "wrinkles": 0,
            "folds": 1,
            "weight": 0.60,
        },
    }
    

    
preset_types = [
    ('Heavy Cotton', 'Heavy Cotton', 'desc'),
    ('Leather', 'Leather', 'desc'),
    ('Tablecloth', 'Tablecloth', 'desc'),
    ('Paper', 'Paper', 'desc'),
]



class CLOTHDROP_Properties(bpy.types.PropertyGroup):

    active : bpy.props.BoolProperty(name="Active",default=False)
    subdivision : bpy.props.IntProperty(name="Detail", description="Adjust geometric subdivision levels", min=1, default=preset_values["Heavy Cotton"]["subdivision"], max=200)
    subsurf : bpy.props.IntProperty(name="Smoothness", description="Adjust subdivision modifier levels", min=1, default=preset_values["Heavy Cotton"]["subsurf"], max=10)
    wrinkles : bpy.props.IntProperty(name="Wrinkles", description="Adjust wrinkle levels", min=0, default=preset_values["Heavy Cotton"]["wrinkles"], max=100)
    folds : bpy.props.IntProperty(name="Folds", description="Adjust folding level", min=0, max=100, default=preset_values["Heavy Cotton"]["folds"])
    weight : bpy.props.FloatProperty(name="Weight", description="Adjust weight", min=0.1, max=10.0, default=preset_values["Heavy Cotton"]["weight"])
    bakeframe : bpy.props.IntProperty(name="Bake Frame", description="Adjust the amount of frames to bake", min=0, default=120, max=250)
    high_friction : bpy.props.BoolProperty(name="High Friction", description="Helps prevent sliding off surface", default=True)
    presets : bpy.props.EnumProperty(name="Presets", description="Useful quick presets", items=preset_types, default='Heavy Cotton', update=utils.CLOTHDROP_preset_update)
    pointer : bpy.props.PointerProperty(name="Collision Pointer", type=bpy.types.Object)
    base_mesh : bpy.props.PointerProperty(name="Base Mesh", type=bpy.types.Mesh)
    base_mesh_name : bpy.props.StringProperty(name="Base Mesh Name", description="Fallback name reference for base mesh across sessions", default="")



classes = [
    CLOTHDROP_Properties
]
