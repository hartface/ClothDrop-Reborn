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



def register_properties():

    bpy.types.Object.clothdrop_active = bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    bpy.types.Object.clothdrop_subdivision = bpy.props.IntProperty(
        name="Detail",
        description="Adjust geometric subdivision levels",
        min=1,
        default=preset_values["Heavy Cotton"]["subdivision"],
        max=200,
    )

    bpy.types.Object.clothdrop_subsurf = bpy.props.IntProperty(
        name="Smoothness",
        description="Adjust subdivision modifier levels",
        min=1,
        default=preset_values["Heavy Cotton"]["subsurf"],
        max=10,
    )

    bpy.types.Object.clothdrop_wrinkles = bpy.props.IntProperty(
        name="Wrinkles",
        description="Adjust wrinkle levels",
        min=0,
        default=preset_values["Heavy Cotton"]["wrinkles"],
        max=100,
    )

    bpy.types.Object.clothdrop_folds = bpy.props.IntProperty(
        name="Folds",
        description="Adjust folding level",
        min=0,
        max=100,
        default=preset_values["Heavy Cotton"]["folds"],
    )

    bpy.types.Object.clothdrop_weight = bpy.props.FloatProperty(
        name="Weight",
        description="Adjust weight",
        min=0.1,
        max=10.0,
        default=preset_values["Heavy Cotton"]["weight"],
    )
    
    bpy.types.Object.clothdrop_bakeframe = bpy.props.IntProperty(
        name="Bake Frame",
        description="Adjust the amount of frames to bake",
        min=0,
        default=120,
        max=250                
    )

    bpy.types.Object.clothdrop_high_friction = bpy.props.BoolProperty(
        name="High Friction",
        description="Helps prevent sliding off surface",
        default=True,
    )
   
    bpy.types.Object.clothdrop_presets = bpy.props.EnumProperty(
        name="Presets",
        description="Useful quick presets",
        items=preset_types,
        default='Heavy Cotton',
        update=utils.CLOTHDROP_preset_update
    )

    bpy.types.Object.clothdrop_collision_pointer = bpy.props.PointerProperty(
        name="Collision Pointer",
        type=bpy.types.Object
    )


    bpy.types.Object.clothdrop_base_mesh = bpy.props.PointerProperty(
        name="Base Mesh",
        type=bpy.types.Mesh
    )

    bpy.types.Object.clothdrop_base_mesh_name = bpy.props.StringProperty(
        name="Base Mesh Name",
        description="Fallback name reference for base mesh across sessions",
        default=""
    )

def unregister_properties():
    del bpy.types.Object.clothdrop_active
    del bpy.types.Object.clothdrop_subdivision
    del bpy.types.Object.clothdrop_subsurf
    del bpy.types.Object.clothdrop_wrinkles
    del bpy.types.Object.clothdrop_folds
    del bpy.types.Object.clothdrop_weight
    del bpy.types.Object.clothdrop_bakeframe
    del bpy.types.Object.clothdrop_high_friction
    del bpy.types.Object.clothdrop_presets
    del bpy.types.Object.clothdrop_collision_pointer
    del bpy.types.Object.clothdrop_base_mesh
    del bpy.types.Object.clothdrop_base_mesh_name
