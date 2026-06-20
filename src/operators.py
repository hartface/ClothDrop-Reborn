import bpy
from . import utils
from . import graphics


class CLOTHDROP_OT_draw_rectangle(bpy.types.Operator):
    bl_idname = "clothdrop.draw_rectangle"
    bl_label = "Draw Cloth"
    text = "Draw Cloth"    
        
    action = False
    _handle = None
    

    def invoke(self, context, event):
        context.window.cursor_modal_set('CROSSHAIR')
        CLOTHDROP_OT_draw_rectangle.text = "Cancel Drawing"
        context.area.tag_redraw()
        self.report({'INFO'}, "Start drawing in the area")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            if self.action == True:
                self.end = (event.mouse_region_x, event.mouse_region_y)
                context.area.tag_redraw()


        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.action = True
            self.start = (event.mouse_region_x, event.mouse_region_y)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(graphics.draw_rect, (self, context), 'WINDOW', 'POST_PIXEL')
         
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.action == True:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                CLOTHDROP_OT_draw_rectangle.text = "Draw Cloth"
                context.window.cursor_modal_restore()
                context.area.tag_redraw()
                return {'FINISHED'}

            context.area.tag_redraw()

            return {'FINISHED'}

        elif event.type in {'ESC', 'RIGHTMOUSE'}:

            context.window.cursor_modal_restore()
            CLOTHDROP_OT_draw_rectangle.text = "Draw Cloth"
            self.report({'INFO'}, "Cancelled Drawing.")
            if self.action == True:        
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            context.area.tag_redraw()

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


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
    CLOTHDROP_OT_draw_rectangle,
    CLOTHDROP_OT_apply,
    CLOTHDROP_OT_remove,
    CLOTHDROP_OT_adjust_value,
    CLOTHDROP_OT_update,
]
