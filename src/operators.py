import bpy
from . import utils
from . import graphics
import mathutils
from mathutils import Matrix



class CLOTHDROP_OT_draw_rectangle(bpy.types.Operator):
    bl_idname = "clothdrop.draw_rectangle"
    bl_label = "Draw Cloth"
    text = "Draw Cloth"
    bl_description = "Draw cloth manually."
        

    def finish(self, context, origin, direction):
        from mathutils import Vector
        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

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
        br = project_to_depth((self.end[0], self.end[1]))

        width = (tr - tl).length
        height = (bl - tl).length

        min_x = min(tl.x, tr.x, bl.x, br.x)
        max_x = max(tl.x, tr.x, bl.x, br.x)
        min_y = min(tl.y, tr.y, bl.y, br.y)
        max_y = max(tl.y, tr.y, bl.y, br.y)
        start_z = origin.z 

        steps = 10
        best_hit_z = None
        best_location = None
        hit_obj = None

        down = Vector((0, 0, -1))

        for i in range(steps):
            for j in range(steps):
                x = min_x + (max_x - min_x) * (i / (steps - 1))
                y = min_y + (max_y - min_y) * (j / (steps - 1))
                o = Vector((x, y, start_z))

                while True:
                    hit, loc, norm, idx, current_hit, mat = context.scene.ray_cast(depsgraph, o, down)
                    if not hit:
                        break
                    if best_hit_z is None or loc.z > best_hit_z:
                        best_hit_z = loc.z
                        best_location = loc.copy()
                        hit_obj = current_hit
                    break

        if hit_obj is None:
            self.report({'ERROR'}, "No object underneath!")
            return

        spawn_location = Vector((
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            best_hit_z + 0.001
        ))

        bpy.ops.mesh.primitive_plane_add(location=spawn_location, rotation=rotation)

        plane = context.active_object
        plane.data.transform(Matrix.Diagonal((width / 2, height / 2, 1, 1)))
        plane.data.update()

        if context.scene.clothdrop.lock_rotation:
            plane.rotation_euler = (0, 0, plane.rotation_euler.z)

        plane.clothdrop.is_drawn = True

        col = hit_obj.modifiers.get("Clothdrop_Collision")
        if not col:
            col = hit_obj.modifiers.new(name="Clothdrop_Collision", type='COLLISION')
  
        
        plane.clothdrop.collision_pointer = hit_obj

        f_val = 80.0 if plane.clothdrop.high_friction else 1.0
        col.settings.cloth_friction = f_val
        col.settings.damping = 1.0 if plane.clothdrop.high_friction else 0.1
        col.settings.thickness_outer = 0.001

        bpy.ops.clothdrop.apply()


        
    def invoke(self, context, event):
        self.action = False
        self._handle = None
        context.window.cursor_modal_set('CROSSHAIR')
        CLOTHDROP_OT_draw_rectangle.text = "ESC to cancel."
        context.area.tag_redraw()
        self.report({'INFO'}, "ESC to cancel drawing.")
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
        context.window.cursor_set('WAIT')
        utils.CLOTHDROP_subdivision(self, context)
        context.window.cursor_set('DEFAULT')

        return {'FINISHED'}



class CLOTHDROP_OT_adjust_value(bpy.types.Operator):
    bl_idname = "clothdrop.adjust_value"
    bl_label = "Adjust value"
    bl_description = "Update value"

    prop: bpy.props.StringProperty()
    delta: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.object
        current = getattr(obj.clothdrop, self.prop)
        setattr(obj.clothdrop, self.prop, current + self.delta)
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

        context.window.cursor_set('WAIT')
        
        hit_obj, best_location = utils.CLOTHDROP_auto_collision(obj, context)
    
        if hit_obj is None:
            self.report({'ERROR'}, "No object underneath! Place something below for the cloth to land on.")
            return {'CANCELLED'}

        obj.location.z = best_location.z + 0.001
               
        utils.CLOTHDROP_store_base(obj)
        utils.CLOTHDROP_subdivision(self, context)
        obj.clothdrop.active = True
        context.window.cursor_set('DEFAULT')
        return {'FINISHED'}


class CLOTHDROP_OT_remove(bpy.types.Operator):
    bl_idname = "clothdrop.remove"
    bl_label = "Remove"
    bl_description = "Remove the effect"
    

    def invoke(self, context, event):
        if context.object and context.object.clothdrop.is_drawn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)


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

        if obj.clothdrop.is_drawn:
            bpy.data.objects.remove(obj)
        
        return {'FINISHED'}



classes = [
    CLOTHDROP_OT_draw_rectangle,
    CLOTHDROP_OT_apply,
    CLOTHDROP_OT_remove,
    CLOTHDROP_OT_adjust_value,
    CLOTHDROP_OT_update,
]
