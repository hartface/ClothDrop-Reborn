import bpy
from . import utils



class CLOTHDROP_OT_update(bpy.types.Operator):
    bl_idname = "clothdrop.update"
    bl_label = "Update"
    bl_description = "Update the cloth"
        
    def execute(self, context):
        utils.CLOTHDROP_subdivision(self, context)

        return {'FINISHED'}



class CLOTHDROP_OT_adjust_value(bpy.types.Operator):
    bl_idname = "clothdrop.adjust_value"
    bl_label = "Adjust value"
    bl_description = "Update value"

    prop: bpy.props.StringProperty()
    delta: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.object
        current = getattr(obj, self.prop)
        setattr(obj, self.prop, current + self.delta)
        return {'FINISHED'}
    


class CLOTHDROP_OT_apply(bpy.types.Operator):
    bl_idname = "clothdrop.apply"
    bl_label = "Create and Drop Cloth"
    bl_description = "Apply effect"

    def execute(self, context):
        obj = context.object
        valid, msg = utils.CLOTHDROP_validate_selected(context)

        if not valid:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}
            
        if not utils.CLOTHDROP_auto_collision(obj, context):
            self.report({'ERROR'}, "No object underneath! Place something below for the cloth to land on.")
            return {'CANCELLED'}
                   
        scene = context.scene

        utils.CLOTHDROP_store_base(obj)
        utils.CLOTHDROP_subdivision(self, context)
        obj.clothdrop.active = True
            
        return {'FINISHED'}



class CLOTHDROP_OT_remove(bpy.types.Operator):
    bl_idname = "clothdrop.remove"
    bl_label = "Remove"
    bl_description = "Remove the effect"


    def execute(self, context):
        valid, msg = utils.CLOTHDROP_validate_selected(context)


        if not valid:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        
        utils.CLOTHDROP_restore_base(context.object)
        utils.CLOTHDROP_subdivision_remove(context)
        utils.CLOTHDROP_remove_collision(context)


        scene = context.scene
        obj = context.object


        for mod in obj.modifiers:
            if mod.name == 'CLOTHDROP':
                obj.modifiers.remove(mod)

            
        obj.clothdrop.active = False
        return {'FINISHED'}



classes = [
    CLOTHDROP_OT_apply,
    CLOTHDROP_OT_remove,
    CLOTHDROP_OT_adjust_value,
    CLOTHDROP_OT_update,
]
