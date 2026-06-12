bl_info = {
    "name": "ClothDrop",
    "author": "Gustavs Tempelfelds",
    "version": (1, 0, 2),
    "blender": (4, 2, 0),
    "description": "Single Click Cloth Creator and Dropper",
    "location": "View3D > Sidebar > ClothDrop",
    "category": "Object"
}



import bpy
from . import operators
from . import panel
from . import properties



classes = []



for _class in operators.classes:
    classes.append(_class)
for _class in panel.classes:
    classes.append(_class)
for _class in properties.classes:
    classes.append(_class)


def register():
   
    for _class in classes:
        bpy.utils.register_class(_class)

    bpy.types.Object.clothdrop = bpy.props.PointerProperty(type=properties.CLOTHDROP_Properties)


def unregister():
    del bpy.types.Object.clothdrop
    for _class in reversed(classes):
        bpy.utils.unregister_class(_class)
