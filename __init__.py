bl_info = {
    "name": "NFS Ultimate Conversion Tools",
    "author": "RSDT",
    "version": (1, 4, 2),
    "blender": (4, 0, 0),
    "location": "View3D > N Panel",
    "description": "A tool to simplify the process of creating cars in NFS Black Box games",
    "category": "NFS",
}

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, PointerProperty
import os

# Shaders (only Most Wanted for now) Also u can add your own shaders here and it should work (not tested)
SHADERS_MW = [
    "ALUMINUM", "BOTTOM", "BRAKEDISC", "BRAKELIGHT", "BRAKELIGHTGLASS", "CALIPER",
    "CALIPERDECAL", "CALLIPER", "CARBONFIBER", "CARBONFIBER2", "CARSKIN", "CHROME",
    "CLEARPLASTIC", "DECAL", "DIABLOHP", "DRIVER", "DULLPLASTIC", "GOLDROTOR",
    "GRILL", "HEADLIGHTGLASS", "HEADLIGHTREFLECTOR", "HOSES", "INTERIOR",
    "LICENSEPLATE", "MAGCHROME", "MAGGUNMETAL", "MAGSILVER", "MOLDINGS",
    "PLAINNOTHING", "RAD", "RUBBER", "TRAFFICWINDOWS", "WINDOWMASK", "WINDSHIELD"
]

class NFSProjectProperties(bpy.types.PropertyGroup):
    xname: StringProperty(name="XNAME", default="")
    game: EnumProperty(name="Game", items=[('MW', "Most Wanted 2005", "")], default='MW')
    project_initialized: BoolProperty(default=False)
    project_folder: StringProperty(name="Project Folder", subtype='DIR_PATH', default="")

class NFSMaterialProps(bpy.types.PropertyGroup):
    shader: EnumProperty(name="Shader", items=[(s, s, "") for s in SHADERS_MW])
    texture: StringProperty(name="Texture", default="")
    is_global: BoolProperty(name="Global Texture", default=True)

class NFS_PT_MainPanel(bpy.types.Panel):
    bl_label = "NFS UCCT"
    bl_idname = "NFS_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NFS Tools"

    def draw(self, context):
        layout = self.layout
        props = context.scene.nfs_project

        if not props.project_initialized:
            layout.operator("nfs.create_new_car", text="Create New Car", icon='FILE_NEW')
            layout.label(text="Open an existing project or create a new one", icon='INFO')
        else:
            layout.label(text=f"Active Project: {props.xname}", icon='CHECKMARK')
            layout.prop(props, "project_folder")

            layout.separator()
            layout.operator("nfs.generate_files", text="Generate Files (_CONFIG & _VLT)", icon='FILE_TEXT')
            layout.operator("nfs.reset_project", text="Reset Project", icon='X')

class NFS_PT_MaterialPanel(bpy.types.Panel):
    bl_label = "NFS Materials"
    bl_idname = "NFS_PT_MaterialPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NFS Tools"
    bl_parent_id = "NFS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj and obj.type == 'MESH' and obj.active_material:
            mat = obj.active_material
            nfs = mat.nfs
            layout.label(text=f"Material: {mat.name}", icon='MATERIAL')
            layout.prop(nfs, "shader")
            layout.prop(nfs, "texture")
            layout.prop(nfs, "is_global")
        else:
            layout.label(text="Select an object with a material", icon='INFO')

class NFS_OT_CreateNewCar(bpy.types.Operator):
    bl_idname = "nfs.create_new_car"
    bl_label = "Create New Car"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        props = context.scene.nfs_project
        layout.prop(props, "xname")
        layout.prop(props, "game")

    def execute(self, context):
        props = context.scene.nfs_project
        if not props.xname.strip():
            self.report({'ERROR'}, "You must enter an XNAME")
            return {'CANCELLED'}

        props.xname = props.xname.strip().upper()
        props.project_initialized = True
        self.report({'INFO'}, f"Project {props.xname} created and saved")
        return {'FINISHED'}


class NFS_OT_ResetProject(bpy.types.Operator):
    bl_idname = "nfs.reset_project"
    bl_label = "Reset Project"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.nfs_project
        props.project_initialized = False
        props.xname = ""
        props.project_folder = ""
        self.report({'INFO'}, "Project reset. Create a new one.")
        return {'FINISHED'}


class NFS_OT_GenerateFiles(bpy.types.Operator):
    bl_idname = "nfs.generate_files"
    bl_label = "Generate Files"

    def execute(self, context):
        props = context.scene.nfs_project
        if not props.project_initialized or not props.project_folder:
            self.report({'ERROR'}, "Missing XNAME or project folder")
            return {'CANCELLED'}

        xname = props.xname
        xname_lower = xname.lower()
        folder = props.project_folder
        game = props.game

        config_path = os.path.join(folder, f"{xname}_CONFIG.txt")
        vlt_path = os.path.join(folder, f"{xname}_VLT.txt")

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(f"# NFS CONFIG FILE - {xname}\n")
                f.write("# Generated with NFS Ultimate Conversion Tools\n\n")

                f.write("# === PARTS ===\n")
                for obj in bpy.data.objects:
                    if obj.type == 'MESH':
                        f.write(f"PART {game} {obj.name}\n")

                f.write("\n# === MATERIALS ===\n")
                written = set()
                for obj in bpy.data.objects:
                    if obj.type == 'MESH' and obj.active_material:
                        mat = obj.active_material
                        if mat.name in written: continue
                        written.add(mat.name)

                        nfs = mat.nfs
                        texture = nfs.texture.strip()
                        if texture and not nfs.is_global and not texture.startswith("%_"):
                            texture = "%_" + texture

                        shader = nfs.shader if nfs.shader else "DULLPLASTIC"
                        f.write(f"MATERIAL {game} {mat.name} {shader} {texture or 'NONE'}\n")

            # Vlt Template, make sure you change properly Frontend part
            with open(vlt_path, "w", encoding="utf-8") as f:
                f.write(f"# VLT SCRIPT - {xname}\n")
                f.write("# Generated automatically\n\n")
                
                f.write(f"copy_node brakes {xname_lower} default {xname_lower}\n")
                f.write(f"copy_node brakes {xname_lower}_top {xname_lower} {xname_lower}_top\n")
                f.write(f"copy_node chassis {xname_lower} default {xname_lower}\n")
                f.write(f"copy_node chassis {xname_lower}_top {xname_lower} {xname_lower}_top\n")
                f.write(f"copy_node ecar {xname_lower} racers {xname_lower}\n")
                f.write(f"copy_node engine {xname_lower} default {xname_lower}\n")
                f.write(f"copy_node frontend {xname_lower}_car {xname_lower} {xname_lower}\n")
                f.write(f"copy_node tires {xname_lower} default {xname_lower}\n")
                f.write(f"copy_node pvehicle {xname_lower} racers {xname_lower}\n\n")

                f.write(f"update_field pvehicle {xname_lower} MODEL Collision64 {xname}\n")
                f.write(f"update_field pvehicle {xname_lower} MODEL Collision {xname}\n")
                f.write(f"update_field pvehicle {xname_lower} MODEL Visual {xname}\n")

            self.report({'INFO'}, f"Files generated successfully in:\n{folder}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


classes = [
    NFSProjectProperties,
    NFSMaterialProps,
    NFS_PT_MainPanel,
    NFS_PT_MaterialPanel,
    NFS_OT_CreateNewCar,
    NFS_OT_ResetProject,
    NFS_OT_GenerateFiles,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.nfs_project = PointerProperty(type=NFSProjectProperties)
    bpy.types.Material.nfs = PointerProperty(type=NFSMaterialProps)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nfs_project
    del bpy.types.Material.nfs

if __name__ == "__main__":
    register()