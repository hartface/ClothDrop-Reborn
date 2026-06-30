import bpy
from . import utils
from . import presets


class CLOTHDROP_Properties(bpy.types.PropertyGroup):

    active : bpy.props.BoolProperty(name="Active",default=False)
    subdivision : bpy.props.IntProperty(name="Detail", description="Adjust geometric subdivision levels", min=1, default=presets.preset_values["Heavy Cotton"]["subdivision"], max=200)
    subsurf : bpy.props.IntProperty(name="Smoothness", description="Adjust subdivision modifier levels", min=0, default=presets.preset_values["Heavy Cotton"]["subsurf"], max=10)
    wrinkles : bpy.props.IntProperty(name="Wrinkles", description="Adjust wrinkle levels", min=0, default=presets.preset_values["Heavy Cotton"]["wrinkles"], max=100)
    folds : bpy.props.IntProperty(name="Folds", description="Adjust folding level", min=0, max=100, default=presets.preset_values["Heavy Cotton"]["folds"])
    weight : bpy.props.FloatProperty(name="Weight", description="Adjust weight", min=0.1, max=10.0, default=presets.preset_values["Heavy Cotton"]["weight"])
    bakeframe : bpy.props.IntProperty(name="Bake Frame", description="Adjust the amount of frames to bake", min=0, default=120, max=250)
    high_friction : bpy.props.BoolProperty(name="High Friction", description="Helps prevent sliding off surface", default=True)
    collision_pointer : bpy.props.PointerProperty(name="Collision Pointer", type=bpy.types.Object)
    base_mesh : bpy.props.PointerProperty(name="Base Mesh", type=bpy.types.Mesh)
    base_mesh_name : bpy.props.StringProperty(name="Base Mesh Name", description="Fallback name reference for base mesh across sessions", default="")
    is_drawn : bpy.props.BoolProperty(name="Is drawn", description="True if object is drawn", default=False)
    base_location_z : bpy.props.FloatProperty(name="Base Location Z", default=0.0)


class CLOTHDROP_UI(bpy.types.PropertyGroup):
    presets : bpy.props.EnumProperty(name="Presets", description="Useful quick presets", items=presets.preset_types, default='Heavy Cotton', update=utils.CLOTHDROP_preset_update)
    lock_rotation : bpy.props.BoolProperty(name="Lock Rotation", description="Lock the draw rotation.", default=True)


classes = [
    CLOTHDROP_Properties,
    CLOTHDROP_UI
]
