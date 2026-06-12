import bpy
from . import utils



def CLOTHDROP_main_box(layout, scene, context):
    obj = context.object

    if utils.CLOTHDROP_has_modifier(context.object):
        row = layout.split(factor=0.5)
        row.operator("clothdrop.remove", icon='REMOVE')
        row.operator("clothdrop.update", icon="MOD_CLOTH")

        layout.prop(obj, "clothdrop_presets")
    else:
        layout.operator("clothdrop.apply", icon='MOD_CLOTH')
        layout.prop(obj, "clothdrop_presets")
        return

    layout.separator()

    subdivision_row = layout.row(align=True)
    subdivision_minus_col = subdivision_row.row(align=True)
    subdivision_minus_col.scale_x = 0.3
    subdivision_minus = subdivision_minus_col.operator("clothdrop.adjust_value", text="-")
    subdivision_minus.prop = "clothdrop_subdivision"
    subdivision_minus.delta = -1
    subdivision_row.prop(obj, "clothdrop_subdivision", slider=True)
    subdivision_plus_col = subdivision_row.row(align=True)
    subdivision_plus_col.scale_x = 0.3
    subdivision_plus = subdivision_plus_col.operator("clothdrop.adjust_value", text="+")
    subdivision_plus.prop = "clothdrop_subdivision"
    subdivision_plus.delta = 1

    subsurf_row = layout.row(align=True)
    subsurf_minus_col = subsurf_row.row(align=True)
    subsurf_minus_col.scale_x = 0.3
    subsurf_minus = subsurf_minus_col.operator("clothdrop.adjust_value", text="-")
    subsurf_minus.prop = "clothdrop_subsurf"
    subsurf_minus.delta = -1
    subsurf_row.prop(obj, "clothdrop_subsurf", slider=True)
    subsurf_plus_col = subsurf_row.row(align=True)
    subsurf_plus_col.scale_x = 0.3
    subsurf_plus = subsurf_plus_col.operator("clothdrop.adjust_value", text="+")
    subsurf_plus.prop = "clothdrop_subsurf"
    subsurf_plus.delta = 1

    wrinkles_row = layout.row(align=True)
    wrinkles_minus_col = wrinkles_row.row(align=True)
    wrinkles_minus_col.scale_x = 0.3
    wrinkles_minus = wrinkles_minus_col.operator("clothdrop.adjust_value", text="-")
    wrinkles_minus.prop = "clothdrop_wrinkles"
    wrinkles_minus.delta = -1
    wrinkles_row.prop(obj, "clothdrop_wrinkles", slider=True)
    wrinkles_plus_col = wrinkles_row.row(align=True)
    wrinkles_plus_col.scale_x = 0.3
    wrinkles_plus = wrinkles_plus_col.operator("clothdrop.adjust_value", text="+")
    wrinkles_plus.prop = "clothdrop_wrinkles"
    wrinkles_plus.delta = 1

    folds_row = layout.row(align=True)
    folds_minus_col = folds_row.row(align=True)
    folds_minus_col.scale_x = 0.3
    folds_minus = folds_minus_col.operator("clothdrop.adjust_value", text="-")
    folds_minus.prop = "clothdrop_folds"
    folds_minus.delta = -1
    folds_row.prop(obj, "clothdrop_folds", slider=True)
    folds_plus_col = folds_row.row(align=True)
    folds_plus_col.scale_x = 0.3
    folds_plus = folds_plus_col.operator("clothdrop.adjust_value", text="+")
    folds_plus.prop = "clothdrop_folds"
    folds_plus.delta = 1

    bakeframe_row = layout.row(align=True)
    bakeframe_minus_col = bakeframe_row.row(align=True)
    bakeframe_minus_col.scale_x = 0.3
    bakeframe_minus = bakeframe_minus_col.operator("clothdrop.adjust_value", text="-")
    bakeframe_minus.prop = "clothdrop_bakeframe"
    bakeframe_minus.delta = -1
    bakeframe_row.prop(obj, "clothdrop_bakeframe", slider=True)
    bakeframe_plus_col = bakeframe_row.row(align=True)
    bakeframe_plus_col.scale_x = 0.3
    bakeframe_plus = bakeframe_plus_col.operator("clothdrop.adjust_value", text="+")
    bakeframe_plus.prop = "clothdrop_bakeframe"
    bakeframe_plus.delta = 1

    weight_row = layout.row(align=True)
    weight_minus_col = weight_row.row(align=True)
    weight_minus_col.scale_x = 0.3
    weight_minus = weight_minus_col.operator("clothdrop.adjust_value", text="-")
    weight_minus.prop = "clothdrop_weight"
    weight_minus.delta = -1
    weight_row.prop(obj, "clothdrop_weight", slider=True)
    weight_plus_col = weight_row.row(align=True)
    weight_plus_col.scale_x = 0.3
    weight_plus = weight_plus_col.operator("clothdrop.adjust_value", text="+")
    weight_plus.prop = "clothdrop_weight"
    weight_plus.delta = 1

    layout.separator()
    layout.prop(obj, "clothdrop_high_friction")

          
            
class CLOTHDROP_PT_panel(bpy.types.Panel):
    bl_idname = "CLOTHDROP_PT_panel"
    bl_label = "ClothDrop"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ClothDrop"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object       

        valid, msg = utils.CLOTHDROP_validate_selected(context)
        if not valid:
            layout.label(text=msg, icon='ERROR')
            return
        
        CLOTHDROP_main_box(layout, scene, context)

        if not utils.CLOTHDROP_has_modifier(context.object):
            return

        

classes = [
    CLOTHDROP_PT_panel
]
