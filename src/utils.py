import bpy
from mathutils import Vector
from . import properties as p



def CLOTHDROP_bake(context):
    scene = context.scene
    obj = context.object

    bakeframe = max(1, obj.clothdrop.bakeframe)

    cloth = obj.modifiers.get("CLOTHDROP")

    if cloth is None:
        scene.frame_set(1)
        return

    pc = cloth.point_cache
    pc.frame_start = 1
    pc.frame_end = bakeframe
    
    with context.temp_override(object=obj, active_object=obj, point_cache=pc):
        bpy.ops.ptcache.bake(bake=True)

    scene.frame_set(bakeframe)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)

    frozen = bpy.data.meshes.new_from_object(eval_obj, preserve_all_data_layers=True, depsgraph=dg)
    obj.data = frozen

    with context.temp_override(object=obj, active_object=obj, point_cache=pc):
        bpy.ops.ptcache.free_bake()

    CLOTHDROP_add_wrinkles(obj, obj.clothdrop.wrinkles)

    for name in ["CLOTHDROP", "Subsurf", "ClothWrinkles"]:
        mod = obj.modifiers.get(name)
        if mod:
            obj.modifiers.remove(mod)

    scene.frame_set(1)
    bpy.context.view_layer.update()




def CLOTHDROP_preset_update(self, context):
    obj = context.object
    settings = p.preset_values[context.scene.clothdrop.presets]
    obj.clothdrop.subdivision = settings['subdivision']
    obj.clothdrop.folds = settings['folds']
    obj.clothdrop.subsurf = settings['subsurf']
    obj.clothdrop.wrinkles = settings['wrinkles']
    obj.clothdrop.weight = settings['weight']



def CLOTHDROP_remove_collision(context):
    obj = context.object

    if obj.clothdrop.collision_pointer is not None:
        mod = obj.clothdrop.collision_pointer.modifiers.get('Clothdrop_Collision')

        if mod:
            obj.clothdrop.collision_pointer.modifiers.remove(mod)        
        
    
def CLOTHDROP_store_base(obj):
    if obj.clothdrop.active:
        return

    if obj.clothdrop.base_mesh is None:
        
        stored_name = getattr(obj.clothdrop, "base_mesh_name", "")
        if stored_name and bpy.data.meshes.get(stored_name):
            obj.clothdrop.base_mesh = bpy.data.meshes.get(stored_name)
            return

        copy = obj.data.copy()
        copy.name = f"{obj.name}_clothdrop_base"
        copy.use_fake_user = True
        obj.clothdrop.base_mesh = copy
        obj.clothdrop.base_mesh_name = copy.name 
 


def CLOTHDROP_restore_base(obj, clear_cache=True):
    cached = obj.clothdrop.base_mesh
  
    if cached is None:
        stored_name = getattr(obj, "base_mesh_name", "")
        if stored_name:
            cached = bpy.data.meshes.get(stored_name)
  
    if cached is None:
        cached = bpy.data.meshes.get(f"{obj.name}_clothdrop_base")
  
    if cached is None:
        return
  
    old = obj.data
    obj.data = cached.copy()
    obj.data.name = obj.name
  
    if clear_cache:
        obj.clothdrop.base_mesh = None
        obj.clothdrop.base_mesh_name = ""
      
        cached.use_fake_user = False
        bpy.data.meshes.remove(cached)
  
    if old.users == 0:
        bpy.data.meshes.remove(old)
         


def CLOTHDROP_add_wrinkles(obj, wrinkles_value):
    if wrinkles_value <= 0:
        return
    
    tex_name = f"ClothDrop_Wrinkles_{obj.name}"
    tex = bpy.data.textures.new(name=tex_name, type='CLOUDS')
    
    tex.noise_scale = 0.8
    tex.noise_depth = 4
    tex.noise_basis = 'BLENDER_ORIGINAL'
    tex.contrast = 1.2

    disp = obj.modifiers.new(name="ClothWrinkles", type='DISPLACE')
    disp.texture = tex
    disp.texture_coords = 'UV'
    disp.direction = 'NORMAL'
    disp.strength = 0.04 + (wrinkles_value / 8000.0)

    disp.mid_level = 0.3

    bpy.ops.object.modifier_apply(modifier=disp.name)

    if tex_name in bpy.data.textures:
        bpy.data.textures.remove(tex)



def CLOTHDROP_validate_selected(context):
    obj = context.object

    if obj is None:
        return False, "Mesh not selected"

    if obj.type != 'MESH':
        return False, "Selected object is not a Mesh"
       
    return True, ""    



def CLOTHDROP_has_modifier(obj):
    try:
        if obj.clothdrop.active == True:
            return True
        else:
            return False
    except:
        return False        



def CLOTHDROP_subdivision_remove(context):
    obj = context.object

    subd = obj.modifiers.get("Subsurf")

    if not subd:
        return

    obj.modifiers.remove(subd)


        
def CLOTHDROP_update_collision_friction(context):
    obj = context.object
    collision_obj = getattr(obj.clothdrop, "collision_pointer", None)

    if not collision_obj:
        return

    mod = collision_obj.modifiers.get("Clothdrop_Collision")

    if mod and hasattr(mod, "settings"):
        f_val = 80.0 if getattr(obj.clothdrop, "high_friction", True) else 1.0

        mod.settings.cloth_friction = f_val
        mod.settings.damping = 1.0 if getattr(obj.clothdrop, "high_friction", True) else 0.1
        mod.settings.thickness_outer = 0.001
        mod.settings.thickness_inner = 0.001



def CLOTHDROP_auto_collision(obj, context):
    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get()
    direction = Vector((0, 0, -1))
    hit_obj = None
    best_hit_z = None
    best_location = None

    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    start_z = max(v.z for v in bbox) + 100.0

    steps = 10

    for i in range(steps):
        for j in range(steps):
            x = min_x + (max_x - min_x) * (i / (steps - 1))
            y = min_y + (max_y - min_y) * (j / (steps - 1))
            o = Vector((x, y, start_z))

            while True:
                hit, location, normal, index, current_hit, matrix = scene.ray_cast(
                    depsgraph, o, direction
                )
                if not hit:
                    break
                if current_hit == obj:
                    o = location + Vector((0, 0, -0.001))
                    continue
                if best_hit_z is None or location.z > best_hit_z:
                    best_hit_z = location.z
                    best_location = location.copy()
                    hit_obj = current_hit
                break

    if hit_obj is None or best_location is None:
        return None, None

    col = hit_obj.modifiers.get("Clothdrop_Collision")
    if not col:
        col = hit_obj.modifiers.new(name="Clothdrop_Collision", type='COLLISION')

    obj.clothdrop.collision_pointer = hit_obj

    f_val = 80.0 if obj.clothdrop.high_friction else 1.0
    col.settings.cloth_friction = f_val
    col.settings.damping = 1.0 if obj.clothdrop.high_friction else 0.1
    col.settings.thickness_outer = 0.001

    return hit_obj, best_location




def CLOTHDROP_subdivision(self, context):
    obj = context.object
    
    valid, msg = CLOTHDROP_validate_selected(context)

    if not valid:
        return

    CLOTHDROP_restore_base(obj, clear_cache=False)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=obj.clothdrop.subdivision)
    bpy.ops.object.mode_set(mode='OBJECT')

    cloth = obj.modifiers.get("CLOTHDROP")

    if cloth is None:
        cloth = obj.modifiers.new(type='CLOTH', name='CLOTHDROP')

    cs = cloth.settings
    collision = cloth.collision_settings
    is_high_friction = getattr(obj.clothdrop, "high_friction", True)
    f_val = 80.0 if is_high_friction else 5.0

    fold_pwr = (obj.clothdrop.folds / 10.0) ** 2

    cs.tension_stiffness = max(0.5, 150.0 / (fold_pwr + 1))
    cs.compression_stiffness = max(0.5, 150.0 / (fold_pwr + 1))
    cs.shear_stiffness = max(0.5, 150.0 / (fold_pwr + 1))

    cs.bending_stiffness = max(0.01, 1.0 / (fold_pwr + 0.1))
    
    cs.bending_model = 'ANGULAR'
    cs.mass = obj.clothdrop.weight
    cs.air_damping = 10.0 if is_high_friction else 1.0
    cs.quality = 12
    cs.mass = obj.clothdrop.weight

    collision.use_self_collision = True
    collision.self_distance_min = 0.001
    collision.collision_quality = 5

    collision.friction = f_val
    collision.self_friction = f_val
    cs.bending_damping = 1.0

    subd = obj.modifiers.get("Subsurf")
    if subd is None:
        subd = obj.modifiers.new(name="Subsurf", type='SUBSURF')

    subd.levels = obj.clothdrop.subsurf
    bpy.ops.object.shade_smooth()

    CLOTHDROP_update_collision_friction(context)

    CLOTHDROP_bake(context)
