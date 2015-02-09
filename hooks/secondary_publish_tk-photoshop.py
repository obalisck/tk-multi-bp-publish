# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import shutil
import photoshop

import tank
from tank import Hook
from tank import TankError


class PublishHook(Hook):
    """
    Single hook that implements publish functionality for secondary tasks
    """

    def execute(self, tasks, work_template, comment, thumbnail_path, sg_task, primary_task, primary_publish_path,
                progress_cb, **kwargs):
        """
        Main hook entry point
        :param tasks:                   List of secondary tasks to be published.  Each task is a 
                                        dictionary containing the following keys:
                                        {
                                            item:   Dictionary
                                                    This is the item returned by the scan hook 
                                                    {   
                                                        name:           String
                                                        description:    String
                                                        type:           String
                                                        other_params:   Dictionary
                                                    }
                                                   
                                            output: Dictionary
                                                    This is the output as defined in the configuration - the 
                                                    primary output will always be named 'primary' 
                                                    {
                                                        name:             String
                                                        publish_template: template
                                                        tank_type:        String
                                                    }
                                        }
                        
        :param work_template:           template
                                        This is the template defined in the config that
                                        represents the current work file
               
        :param comment:                 String
                                        The comment provided for the publish
                        
        :param thumbnail:               Path string
                                        The default thumbnail provided for the publish
                        
        :param sg_task:                 Dictionary (shotgun entity description)
                                        The shotgun task to use for the publish    
                        
        :param primary_publish_path:    Path string
                                        This is the path of the primary published file as returned
                                        by the primary publish hook
                        
        :param progress_cb:             Function
                                        A progress callback to log progress during pre-publish.  Call:
                                        
                                            progress_cb(percentage, msg)
                                             
                                        to report progress to the UI
                        
        :param primary_task:            The primary task that was published by the primary publish hook.  Passed
                                        in here for reference.  This is a dictionary in the same format as the
                                        secondary tasks above.
        
        :returns:                       A list of any tasks that had problems that need to be reported 
                                        in the UI.  Each item in the list should be a dictionary containing 
                                        the following keys:
                                        {
                                            task:   Dictionary
                                                    This is the task that was passed into the hook and
                                                    should not be modified
                                                    {
                                                        item:...
                                                        output:...
                                                    }
                                                    
                                            errors: List
                                                    A list of error messages (strings) to report    
                                        }
        """
        results = []

        # publish all tasks:
        for task in tasks:
            item = task["item"]
            output = task["output"]
            errors = []

            # report progress:
            progress_cb(0, "Publishing", task)

            # publish item here, e.g.
            if output["name"] == "jpeg_output":

                progress_cb(25, "Jpeg Output Readying ... ", task)

                # ** Start Export **
                import photoshop

                doc = photoshop.app.activeDocument

                if doc is None:
                    raise TankError("There is no currently active document!")

                # get scene path
                scene_path = doc.fullName.nativePath

                if not work_template.validate(scene_path):
                    raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_path)

                # use templates to convert to publish path:
                output = task["output"]
                fields = work_template.get_fields(scene_path)
                fields["TankType"] = output["tank_type"]
                publish_template = output["publish_template"]
                publish_path = publish_template.apply_fields(fields)

                publish_dir = os.path.dirname(publish_path)
                publish_name = os.path.basename(publish_path)

                publish_name = publish_name.replace(".psd", ".jpg")
                final_path = os.path.join(publish_dir, publish_name)
                progress_cb(25, "Outputing {0}".format(publish_name), task)

                if os.path.exists(final_path):
                    raise TankError("The published file named '%s' already exists!" % publish_path)

                jpeg_file = photoshop.RemoteObject('flash.filesystem::File', final_path)
                jpeg_options = photoshop.RemoteObject('com.adobe.photoshop::JPEGSaveOptions')
                jpeg_options.quality = 10

                # save a copy
                photoshop.app.activeDocument.saveAs(jpeg_file, jpeg_options, True)

                # ** End Export **

            else:
                pass
            # don't know how to publish this output types!
                errors.append("Don't know how to publish this item!")

            # if there is anything to report then add to result
            if len(errors) > 0:
                # add result:
                results.append({"task": task, "errors": errors})

            progress_cb(100)

        return results




        




