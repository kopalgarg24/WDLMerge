#!/usr/bin/env python3
import os
import sys
import WDL
from WDL.Tree import WorkflowSection
import graphviz
from utils import *

def main(args):
    task_attributes = []
    task_names = set()  # Track unique task names
    workflow_attributes = []  # Track workflow attributes
    workflow_names = set()  # Track unique workflow names

    # Iterate over each WDL file
    for wdl_file in args:
        # Load WDL document from the current file
        document = WDL.load(wdl_file)
        workflows = document.workflow
        tasks = document.tasks

        # Extract task information
        for task in tasks:
            # Check if the task name is already used
            if task.name in task_names:
                print(f"Skipping task with duplicate name: {task.name}")
                continue
            task_names.add(task.name)

            task_info = {
                'name': task.name,
                'inputs': task.inputs or [],
                'command': str(task.command),
                'outputs': task.outputs or [],
                'parameter_meta': task.parameter_meta or {},
                'runtime': task.runtime or {},
            }
            task_attributes.append(task_info)

        # Extract workflow information
        if workflows:
            # Check if the workflow name is already used
            if workflows.name in workflow_names:
                print(f"Skipping workflow with duplicate name: {workflows.name}")
                continue
            workflow_names.add(workflows.name)

            workflow_info = {
                'name': workflows.name,
                'inputs': workflows.inputs or [],
                'outputs': workflows.outputs or [],
                'body': workflows.body or [],
            }
            workflow_attributes.append(workflow_info)

    # Pass the extracted attributes to the reconstruct_wdl function
    combined_dict = {
    'name': 'Workflow1',
    'inputs': [],
    'outputs': [],
    'body': []
      }

    for d in workflow_attributes:
      combined_dict['inputs'].extend(d['inputs'])
      combined_dict['outputs'].extend(d['outputs'])
      combined_dict['body'].extend(d['body'])
    
    reconstructed_wdl = reconstruct_wdl(task_attributes, [combined_dict])
    
    print(reconstructed_wdl)

if __name__ == "__main__":
    main(sys.argv[1:])
