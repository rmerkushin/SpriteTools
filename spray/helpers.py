import bpy


def get_frames_info():
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end
    frame_count = frame_end - frame_start + 1
    return frame_start, frame_end, frame_count
