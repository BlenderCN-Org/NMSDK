bl_info = {  
 "name": "NMS Exporter",  
 "author": "gregkwaste / monkeyman192",  
 "version": (0, 7),  
 "blender": (2, 7, 0),  
 "location": "File > Export",  
 "description": "Exports to NMS File format",  
 "warning": "",  
 "wiki_url": "",  
 "tracker_url": "",  
 "category": "Export"} 
 
import bpy
import bmesh
import os
import sys
from math import radians, degrees
from mathutils import Matrix,Vector

# Add script path to sys.path
#scriptpath = bpy.context.space_data.text.filepath
scriptpath = "J:\\Projects\\NMS_Model_Importer\\blender_script.py"
proj_path = os.path.dirname(scriptpath)
#proj_path = bpy.path.abspath('//')
print(proj_path)

if not proj_path in sys.path:
    sys.path.append(proj_path)
    #print(sys.path)
    
    
from main import Create_Data
from classes import TkMaterialData, TkMaterialFlags, TkMaterialUniform, TkMaterialSampler, TkTransformData
from classes import List, Vector4f, Collision
#Import Object Classes
from classes.Object import Model, Mesh, Locator, Reference
from LOOKUPS import MATERIALFLAGS


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World %s" % use_some_setting)
    f.close()

    return {'FINISHED'}


def parse_material(ob):
    # This function returns a tkmaterialdata object with all necessary material information
    
    #Get Material stuff

    slot = ob.material_slots[0]
    mat = slot.material
    print(mat.name)
    
    #Create the material
    matflags = List()
    matsamplers = List()
    matuniforms = List()
    
    tslots = mat.texture_slots
    
    #Fetch Uniforms
    matuniforms.append(TkMaterialUniform(Name="gMaterialColourVec4",
                                         Values=Vector4f(x=mat.diffuse_color.r,
                                                         y=mat.diffuse_color.g,
                                                         z=mat.diffuse_color.b,
                                                         t=1.0)))
    matuniforms.append(TkMaterialUniform(Name="gMaterialParamsVec4",
                                         Values=Vector4f(x=0.0,
                                                         y=0.0,
                                                         z=0.0,
                                                         t=0.0)))
    matuniforms.append(TkMaterialUniform(Name="gMaterialSFXVec4",
                                         Values=Vector4f(x=0.0,
                                                         y=0.0,
                                                         z=0.0,
                                                         t=0.0)))
    matuniforms.append(TkMaterialUniform(Name="gMaterialSFXColVec4",
                                         Values=Vector4f(x=0.0,
                                                         y=0.0,
                                                         z=0.0,
                                                         t=0.0)))
    #Fetch Diffuse
    texpath = ""
    if tslots[0]:
        #Set _F01_DIFFUSEMAP
        matflags.append(TkMaterialFlags(MaterialFlag=MATERIALFLAGS[0]))
        #Create gDiffuseMap Sampler
        
        tex = tslots[0].texture
        #Check if there is no texture loaded
        if not tex.type=='IMAGE':
            raise Exception("Missing Image in Texture: " + tex.name)
        
        texpath = os.path.join(proj_path, tex.image.filepath[2:])
    print(texpath)
    sampl = TkMaterialSampler(Name="gDiffuseMap", Map=texpath, IsSRGB=True)
    matsamplers.append(sampl)
    
    #Check shadeless status
    if (mat.use_shadeless):
        #Set _F07_UNLIT
        matflags.append(TkMaterialFlags(MaterialFlag=MATERIALFLAGS[6]))    
    
    #Fetch Mask
    texpath = ""
    if tslots[1]:
        #Set _F24_AOMAP
        matflags.append(TkMaterialFlags(MaterialFlag=MATERIALFLAGS[23]))
        #Create gMaskMap Sampler
        
        tex = tslots[1].texture
        #Check if there is no texture loaded
        if not tex.type=='IMAGE':
            raise Exception("Missing Image in Texture: " + tex.name)
        
        texpath = os.path.join(proj_path, tex.image.filepath[2:])
    
    sampl = TkMaterialSampler(Name="gMaskMap", Map=texpath, IsSRGB=False)
    matsamplers.append(sampl)
    
    #Fetch Normal Map
    texpath = ""
    if tslots[2]:
        #Set _F03_NORMALMAP
        matflags.append(TkMaterialFlags(MaterialFlag=MATERIALFLAGS[2]))
        #Create gNormalMap Sampler
        
        tex = tslots[2].texture
        #Check if there is no texture loaded
        if not tex.type=='IMAGE':
            raise Exception("Missing Image in Texture: " + tex.name)
        
        texpath = os.path.join(proj_path, tex.image.filepath[2:])
    
    sampl = TkMaterialSampler(Name="gNormalMap", Map=texpath, IsSRGB=False)
    matsamplers.append(sampl)
    
    #Create materialdata struct
    tkmatdata = TkMaterialData(Name=mat.name,
                               Class='Opaque',
                               Flags=matflags,
                               Uniforms=matuniforms,
                               Samplers=matsamplers)
        
    return tkmatdata

#Main Mesh parser
def mesh_parser(ob):
    #Lists
    verts = []
    norms = []
    luvs = []
    faces = []
    # Matrices
    object_matrix_wrld = ob.matrix_world
    rot_x_mat = Matrix.Rotation(radians(-90), 4, 'X')
    scale_mat = Matrix.Scale(1, 4)
    norm_mat = ob.matrix_world.inverted().transposed()
    
    data = ob.data
    #data.update(calc_tessface=True)  # convert ngons to tris
    data.calc_tessface()
    uvcount = len(data.uv_layers)
    #Raise exception if UV Map is missing
    if (uvcount <1):
        raise Exception("Missing UV Map")
    colcount = len(data.vertex_colors)
    id = 0
    for f in data.tessfaces:  # indices
        if len(f.vertices) == 4:
            faces.append((id, id + 1, id + 2))
            faces.append((id + 3, id, id + 2))
            id += 4
        else:
            faces.append((id, id + 1, id + 2))
            id += 3

        for vert in range(len(f.vertices)):
            co = scale_mat * rot_x_mat * object_matrix_wrld * \
                data.vertices[f.vertices[vert]].co
            norm = scale_mat * rot_x_mat * norm_mat * \
                10 * data.vertices[f.vertices[vert]].normal
            verts.append((co[0], co[1], co[2], 1.0))
            norms.append((norm[0], norm[1], norm[2], 0.0))

            #Get Uvs
            uv = getattr(data.tessface_uv_textures[0].data[f.index], 'uv'+str(vert + 1))
            luvs.append((uv.x, 1.0 - uv.y, 0.0, 0.0))
#            for k in range(colcount):
#                r = eval('data.tessface_vertex_colors[' + str(k) + '].data[' + str(
#                    f.index) + '].color' + str(vert + 1) + '[0]*1023')
#                g = eval('data.tessface_vertex_colors[' + str(k) + '].data[' + str(
#                    f.index) + '].color' + str(vert + 1) + '[1]*1023')
#                b = eval('data.tessface_vertex_colors[' + str(k) + '].data[' + str(
#                    f.index) + '].color' + str(vert + 1) + '[2]*1023')
#                eval('col_' + str(k) + '.append((r,g,b))')

    return verts,norms,luvs,faces

def parse_object(ob):
    newob = None
    global material_dict
    # Main switch to identify meshes or locators/references
    if ob.type == 'MESH':
        if ob.name.startswith("COLLISION"):
            # COLLISION MESH
            print("Collision found: ", col.name)
            split = ob.name.split("_")
            colType = split[1]
            
            optdict = {}
            rot_x_mat = Matrix.Rotation(radians(-90), 4, 'X')
            trans, rot, scale = (rot_x_mat * ob.matrix_local).decompose()
            rot = rot.to_euler()
            print(trans)
            print(rot)
            print(scale)
            optdict['Transform'] = TkTransformData(TransX=trans[0],
                                                   TransY=trans[1],
                                                   TransZ=trans[2],
                                                   RotX=degrees(rot[0]),
                                                   RotY=degrees(rot[1]),
                                                   RotZ=degrees(rot[2]),
                                                   ScaleX=scale[0],
                                                   ScaleY=scale[1],
                                                   ScaleZ=scale[2])
            
            optdict['CollisionType'] = colType
            if (colType == "Mesh"):
                c_verts,c_norms,c_uvs,c_faces = mesh_parser(ob)
                
                #Reset Transforms on meshes
                optdict['Transform'] = TkTransformData(TransX=0.0, TransY=0.0, TransZ=0.0,
                                                   RotX=0.0, RotY=0.0, RotZ=0.0,
                                                   ScaleX=1.0, ScaleY=1.0, ScaleZ=1.0)
                optdict['Vertices'] = c_verts
                optdict['Indexes'] = c_faces
                optdict['UVs'] = c_uvs
                optdict['Normals'] = c_norms
            #HANDLE Primitives
            elif (colType == "Box"):
                optdict['Width']  = ob.dimensions[0]
                optdict['Depth']  = ob.dimensions[1]
                optdict['Height'] = ob.dimensions[2]
            elif (colType == "Sphere"):
                optdict['Radius'] = ob.dimensions[0] / 2.0
            elif (colType == "Cylinder"):
                optdict['Radius'] = ob.dimensions[0] / 2.0
                optdict['Height'] = ob.dimensions[2]
            else:
                raise Exception("Unsupported Collision")
            
            newob = Collision(**optdict)
        else:
            # ACTUAL MESH
            #Parse object Geometry
            verts,norms,luvs,faces = mesh_parser(ob)
            print("Object Count: ", len(verts), len(luvs), len(norms), len(faces))
            #Create Mesh Object
            newob = Mesh(ob.name, Vertices=verts, UVs=luvs, Normals=norms, Indexes=faces)
            
            #Try to parse material
            try:
                slot = ob.material_slots[0]
                mat = slot.material
                print(mat.name)
                if not mat.name in material_dict:
                    print("Parsing Material " + mat.name)
                    material_ob = parse_material(ob)
                    material_dict[mat.name] = material_ob
                else:
                    material_ob = material_dict[mat.name]
                
                #Attach material to Mesh
                newob.Material = material_ob
                
            except:
                raise Exception("Missing Material")
    
    #Parse children
    for child in ob.children:
        if not child.name.startswith('NMS'):
            continue
        child_ob = parse_object(child)
        newob.add_child(child_ob)
        
    return newob


def main_exporter(exportpath):
    scn = bpy.context.scene

    icounter = 0
    vcounter = 0
    vertices = []
    normals  = [] 
    indices  = []
    uvs      = []
    tangents = []

    materials = []
    collisions = []
    global material_dict
    material_dict = {}
    material_ids = []

    #Create main scene model
    scene = Model("")

    for ob in scn.objects:
        if not ob.name.startswith('NMS'):
            continue
        print('Located Object for export', ob.name)
        scene.add_child(parse_object(ob))
        

    print('Blender Script')
    print('Create Data Call')
    
    #Convert Paths
    directory = os.path.dirname(exportpath)
    mname = os.path.basename(exportpath)
    Create_Data(mname,
                "EXPORTS",
                scene)
                
    return {'FINISHED'}




class NMS_Export_Operator(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_mesh.nms"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export to NMS XML Format"

    # ExportHelper mixin class uses this
    filename_ext = ""

#    filter_glob = StringProperty(
#            default="*.txt",
#            options={'HIDDEN'},
#            maxlen=255,  # Max internal buffer length, longer would be clamped.
#            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
#    use_setting = BoolProperty(
#            name="Example Boolean",
#            description="Example Tooltip",
#            default=True,
#            )

#    type = EnumProperty(
#            name="Example Enum",
#            description="Choose between two items",
#            items=(('OPT_A', "First Option", "Description one"),
#                   ('OPT_B', "Second Option", "Description two")),
#            default='OPT_A',
#            )

    def execute(self, context):
        return main_exporter(self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(NMS_Export_Operator.bl_idname, text="Export to NMS XML Format ")


def register():
    bpy.utils.register_class(NMS_Export_Operator)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(NMS_Export_Operator)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_mesh.nms(filepath="JUMBO")