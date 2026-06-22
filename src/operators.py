import bpy
from . import utils
from . import graphics
import mathutils
from mathutils import Matrix



class CLOTHDROP_OT_draw_rectangle(bpy.types.Operator):
    bl_idname = "clothdrop.draw_rectangle"
    bl_label = "Draw Cloth"
    text = "Draw Cloth"    
        
    action = False
    _handle = None
    

    def finish(self, context, origin, direction):
        import math
        from mathutils import Vector
        from bpy_extras.view3d_utils import (region_2d_to_origin_3d, region_2d_to_vector_3d,)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, origin, direction)

        if not result:
            return

        depth = (location - origin).length
    
        region = context.region
        rv3d = context.region_data

        rotation = rv3d.view_rotation.to_euler()

        def project_to_depth(screen_co):
            o = region_2d_to_origin_3d(region, rv3d, screen_co)
            d = region_2d_to_vector_3d(region, rv3d, screen_co)
            return o + d * depth

        tl = project_to_depth((self.start[0], self.start[1]))
        tr = project_to_depth((self.end[0], self.start[1]))
        bl = project_to_depth((self.start[0], self.end[1]))

        width = (tr - tl).length
        height = (bl - tl).length

        bpy.ops.mesh.primitive_plane_add(location=location, rotation=rotation)

        plane = context.active_object
        plane.data.transform(Matrix.Diagonal((width / 2, height / 2, 1, 1)))
        plane.data.update()

        up = plane.matrix_world.to_3x3() @ Vector((0, 0, 1))
        up.normalize()

        half_w = width / 2
        half_h = height / 2

        corners = [
            Vector((-half_w, -half_h, 0)),
            Vector(( half_w, -half_h, 0)),
            Vector(( half_w,  half_h, 0)),
            Vector((-half_w,  half_h, 0)),
        ]
    
        rot = plane.matrix_world.to_3x3()

        min_projection = min(
            (rot @ corner).dot(normal)
            for corner in corners
        )

        plane.location -= normal * min_projection
        plane.location += normal * 0.001

        if context.scene.clothdrop.lock_rotation:
            plane.rotation_euler = (0, 0, plane.rotation_euler.z)

        bpy.ops.clothdrop.apply()

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

                #inheriting from aiming helper
                coords = (
                    (self.start[0] + self.end[0]) / 2,
                    (self.start[1] + self.end[1]) / 2,
                )
                region = context.region
                rv3d = context.region_data

                from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d    

                origin = region_2d_to_origin_3d(region, rv3d, coords)
                direction = region_2d_to_vector_3d(region, rv3d, coords)    
        
                self.finish(context, origin, direction)

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
