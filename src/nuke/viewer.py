#viewer.py
#this script controls viewerNode

import nuke
 
def get_active_viewer_node():
    '''Return the current Viewer node.'''
    viewer = nuke.activeViewer()
    if viewer:
        return viewer.node()
 
 
def get_all_viewers(recurseGroups=True):
    '''Return the list of all Viewer nodes in the current script.
 
    :param recurseGroups: If True, will also return all child nodes within any group nodes.
        This is done recursively and defaults to True.
    '''
    return [n for n in nuke.allNodes(recurseGroups=recurseGroups) if n.Class() == 'Viewer']
 
 
def delete_groups_viewers():
    '''Find viewers in groups and delete them.'''
    all_viewers = set(get_all_viewers())
    root_viewers = set(get_all_viewers(recurseGroups=False))
    group_viewers = all_viewers - root_viewers
 
    for viewer in group_viewers:
        nuke.delete(viewer)
 
    if nuke.GUI:
        nuke.message('Deleted %d viewer(s).\n%d viewer(s) remaining in main comp window.' %
                     (len(group_viewers), len(root_viewers)))
 
 
def delete_all_viewers():
    '''Find all viewers and delete them.'''
    all_viewers = get_all_viewers()
 
    for viewer in all_viewers:
        nuke.delete(viewer)
 
    if nuke.GUI:
        nuke.message('Deleted %d viewer(s).' % len(all_viewers))
 
 
######################################################################################
# Viewer toggles
 
def toggle_clip_warning():
    '''Toggle on/off the exposure clip warning on the active viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    if viewer['clip_warning'].value() != 'exposure':
        viewer['clip_warning'].setValue('exposure')
    else:
        viewer['clip_warning'].setValue('no warnings')
 
 
def toggle_zdepth():
    '''Toggle between rgba and Z.depth channel on the active viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    if viewer['channels'].value() != 'depth':
        viewer['channels'].setValue('depth.Z')
    else:
        viewer['channels'].setValue('rgba')
 
 
def toggle_lut():
    '''Toggle between shot lut Viewer and sRGB on the active viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    default_viewer_process = nuke.knobDefault('Viewer.viewerProcess')
 
    srgb_process = [p for p in nuke.ViewerProcess.registeredNames() if p.startswith('Output - K1S1-like - Rec.709 (FS)')]
    if not srgb_process:
        srgb_process = [p for p in nuke.ViewerProcess.registeredNames() if p.startswith('Show Look Graded (FS)')]
 
    if srgb_process and viewer['viewerProcess'].value() != srgb_process[0]:
        viewer['viewerProcess'].setValue(srgb_process[0])
    else:
        viewer['viewerProcess'].setValue(default_viewer_process)
 
    ###############################################WL#    
 
    
def ViewerGainToggle():
    '''Toggle between gain on the active viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    if viewer['gain'].value() != 1:
        viewer['gain'].setValue( 1 )
 
    ###############################################WL#    
 
 
def toggle_crop_preview():
    '''Toggle the crop preview in the viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    process_node = nuke.ViewerProcess.node()
    if 'crop_preview' in process_node.knobs():
        old_value = process_node['crop_preview'].value()
        process_node['crop_preview'].setValue(not old_value)
 
 
def toggle_reverse_neutralgrade():
    '''Toggle the reverse neutralgrade in the viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    process_node = nuke.ViewerProcess.node()
    if 'reverse_neutralgrade' in process_node.knobs():
        old_value = process_node['reverse_neutralgrade'].value()
        process_node['reverse_neutralgrade'].setValue(not old_value)
 
 
def _ask_sat_exp_value(attribute, default):
    '''Ask the user for a float value for the saturation or exposure.'''
    panel = nuke.Panel('Viewer %s' % attribute.replace('_', ' ').capitalize())
    panel.addSingleLineInput('Enter a value', str(default))
 
    if panel.show():
        value = panel.value('Enter a value')
        try:
            value = float(value)
        except ValueError:
            nuke.warning('Invalid value ! Ignoring...')
        else:
            return value
 
 
def _create_sat_exp_node(attribute, value):
    '''Safely create the 'viewer_exposure_saturation' node, resetting the OCIO Display node.'''
    lin_space = nuke.knobDefault('Root.workingSpaceLUT')
    display = nuke.knobDefault('OCIODisplay.display')
    view = nuke.knobDefault('OCIODisplay.view')
    tcl_attrs = '%s "%s" colorspace_1 "%s" display "%s" view "%s"' % \
                (attribute, value, lin_space, display, view)
    return nuke.createNode('viewer_exposure_saturation')
 
def _toggle_sat_exp(attribute):
    '''Toggle/set exposure or saturation in viewer.'''
    viewer = get_active_viewer_node()
    if not viewer:
        return
 
    default_values = {'exposure_stop': 0.0,
                      'saturation': 1.0}
    if not attribute in default_values:
        return
 
    other_attr = [k for k in default_values if k != attribute][0]
    default_process = nuke.knobDefault('Viewer.viewerProcess')
    process_node = nuke.ViewerProcess.node()
 
    if viewer['viewerProcess'].value() == other_attr:
        if process_node[attribute].getValue() != default_values[attribute]:
            viewer['viewerProcess'].setValue(default_process)
            #nuke.ViewerProcess.unregister(other_attr)
 
        else:
            value = _ask_sat_exp_value(attribute, default_values[attribute])
            if value is not None:
                process_node[attribute].setValue(float(value))
 
    elif viewer['viewerProcess'].value() == attribute:
        #process_node[other_attr].setValue(default_values[other_attr])
        viewer['viewerProcess'].setValue(default_process)
        nuke.ViewerProcess.unregister(attribute)
 
    else:
        value = _ask_sat_exp_value(attribute, default_values[attribute])
        if value is not None:
            nuke.ViewerProcess.unregister(attribute)
            nuke.ViewerProcess.register(
                name=attribute,
                call=_create_sat_exp_node,
                args=(attribute, value))
            viewer['viewerProcess'].setValue(attribute)
            nuke.ViewerProcess.node()[attribute].setValue(float(value))
 
 
def toggle_saturation():
    '''Toggle/set saturation in viewer.'''
    _toggle_sat_exp('saturation')
 
 
def toggle_exposure():
    '''Toggle/set exposure in viewer by stop.'''
    _toggle_sat_exp('exposure_stop')
 
##################################################################################


