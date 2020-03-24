# oot link coords <-> blender active object coords
# thinking moving a camera accordingly

bl_info = {
	"name": "OoT64 <-> Blender coordinates synchronization",
	"category": "3D View",
}

import bpy
import threading
import socket

run = False

# blender api stuff

class CoordSyncStart(bpy.types.Operator):
	"""Start synchronizing coordinates of active object and OoT Link"""
	bl_idname = "3dview.oot64coordsyncstart"
	bl_label = "Start synchronize coordinates OoT64 <-> Blender"
	bl_options = {'REGISTER'}

	fps = bpy.props.IntProperty(name="Updates per second", default=20)
	scale = bpy.props.FloatProperty(name="Scale",description="How much is 1 OoT unit in Blender units", default=1)

	# prevent execution with default parameters, ask first
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def execute(self, context):
		# initialize globals for timer threads
		global run
		if run:
			self.report({'ERROR'}, 'Already running')
			return {'CANCELLED'}
		run = True
		# object to sync coordinates with
		# must be a global, bpy.context.object apparently isn't accessible from timer thread
		global obj
		obj = bpy.context.object
		if obj is None:
			self.report({'ERROR_INVALID_INPUT'}, 'Select an object')
			return {'CANCELLED'}
		# refresh per second
		fps = self.fps
		global frameDuration
		frameDuration = 1/fps
		# initialize lastLocation, prevents teleporting link to initial object coordinates
		updateLastLocation()
		global scale
		scale = self.scale
		tick()
		return {'FINISHED'}

class CoordSyncStop(bpy.types.Operator):
	"""Stop synchronizing coordinates with OoT Link"""
	bl_idname = "3dview.oot64coordsyncstop"
	bl_label = "Stop synchronize coordinates OoT64 <-> Blender"
	bl_options = {'REGISTER'}

	def execute(self, context):
		global run
		run = False
		return {'FINISHED'}

def register():
    bpy.utils.register_class(CoordSyncStart)
    bpy.utils.register_class(CoordSyncStop)

def unregister():
    bpy.utils.register_class(CoordSyncStart)
    bpy.utils.register_class(CoordSyncStop)

if __name__ == "__main__":
    register()


# actual code start

# link coordinates -> blender object
def updatePosition(obj):
	socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket_.connect(('127.0.0.1', 80))

	# send data
	bin = bytearray()
	bin.append(1) # 1 for get
	i = 0
	while i < len(bin):
		i += socket_.send(bin)
	socket_.send(b'\r\n') # idk if necessary

	# get data
	# response looks like 'x y z rx ry rz ' (a string)
	r = socket_.recv(4096)
	# wait final space after 6th entry
	while r.count(b' ') < 6:
		print('waiting')
		rPart = socket_.recv(4096)
		print('done waiting')
		print(rPart)
		for c in rPart:
			r.append(c)

	socket_.close()

	# apply coordinates to object
	parts = r.decode().split(' ')
	x = float(parts[0])
	y = float(parts[1])
	z = float(parts[2])
	rx = int(parts[3])
	ry = int(parts[4])
	rz = int(parts[5])

	global scale
	f = scale # scale coordinates
	# oot x is blender x
	# oot y is blender z (vertical)
	# oot z is blender -y
	obj.location = (x*f, -z*f, y*f)

	# TODO rotation
	f = 180/(2**15) #? idk blender angle units, idk max z64 angle (s16), also blender (0,0,0) may not be game (0,0,0)
	obj.rotation_euler = (rx*f,ry*f,rz*f)

# blender object -> link position
def applyPosition(obj):
	socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket_.connect(('127.0.0.1', 80))

	global scale
	f = 1/scale
	# send data
	bin = bytearray()
	bin.append(2) # 2 for set
	# oot x is blender x
	bin.extend(str(f*obj.location[0]).encode())
	bin.extend(b' ')
	# oot y is blender z (vertical)
	bin.extend(str(f*obj.location[2]).encode())
	bin.extend(b' ')
	# oot z is blender -y
	bin.extend(str(-f*obj.location[1]).encode())
	bin.extend(b' ')
	i = 0
	while i < len(bin):
		i += socket_.send(bin)

	socket_.send(b'\r\n')
	
	socket_.close()

# lastLocation <- obj.location
# lastLocation stores where the blender object was last frame, so that user moving it can be detected
def updateLastLocation():
	global obj
	global lastLocation
	lastLocation = [obj.location[i] for i in range(3)]

# main function, called every frameDuration (plus processing duration)
def tick():
	global obj
	global lastLocation
	print('tick')
	locChanged = False
	for i in range(3):
		locChanged = locChanged or (obj.location[i] != lastLocation[i])
	# object was moved in blender outside of this script, apply coordinates to link
	if locChanged:
		print('blender -> oot')
		applyPosition(obj)
	# object was not moved by user, apply Link's coordinates to object
	else:
		print('oot -> blender')
		updatePosition(obj)
	updateLastLocation()
	# keep going
	global run
	if run:
		global frameDuration
		t = threading.Timer(frameDuration, tick)
		t.start()
