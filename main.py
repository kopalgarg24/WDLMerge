#!/usr/bin/env python3
import os
import sys
import WDL
from WDL.Tree import WorkflowSection
import graphviz

def reconstruct_wdl(tasks, workflows):
    wdl_code = ""

    # Reconstruct tasks
    for task in tasks:
        task_name = task['name']
        task_code = f"task {task_name} {{\n"
        if task['inputs']:
            task_code += "    input {\n"
            for input_var in task['inputs']:
                task_code += f"        {input_var}\n"
            task_code += "    }\n"
        task_code += f"    command {{\n        {task['command']}\n    }}\n"
        if task['outputs']:
            task_code += "    output {\n"
            for output_var in task['outputs']:
                task_code += f"        {output_var}\n"
            task_code += "    }\n"
        task_code += "}\n\n"
        if task['runtime']:
            task_code += "    runtime {\n"
            for key, value in task['runtime'].items():
                task_code += f"        {key} = {value}\n"
            task_code += "    }\n"
        task_code += "}\n\n"

        wdl_code += task_code

    # Combine workflows
    if workflows:
        combined_workflow = workflows[0]
        combined_workflow_name = "CombinedWorkflow"
        combined_workflow_inputs = []
        combined_workflow_outputs = []
        combined_workflow_body = []

        for workflow in workflows:
            combined_workflow_inputs.extend(workflow['inputs'])
            combined_workflow_outputs.extend(workflow['outputs'])
            combined_workflow_body.extend(workflow['body'])

        wdl_code += f"workflow {combined_workflow_name} {{\n"
        if combined_workflow_inputs:
            wdl_code += "    input {\n"
            for input_var in combined_workflow_inputs:
                wdl_code += f"        {input_var}\n"
            wdl_code += "    }\n"
        if combined_workflow_outputs:
            wdl_code += "    output {\n"
            for output_var in combined_workflow_outputs:
                wdl_code += f"        {output_var}\n"
            wdl_code += "    }\n"
        for element in combined_workflow_body:
            if isinstance(element, WDL.Tree.Call):
                input_mappings = []
                for input_name, input_expr in element.inputs.items():
                    input_mappings.append(f"{input_name} = {input_expr}")

                wdl_code += f"    call {element.callee_id[0]} {{\n"
                if input_mappings:
                    wdl_code += "        input:\n"
                    for input_mapping in input_mappings:
                        wdl_code += f"            {input_mapping}\n"
                wdl_code += "    }\n"

        wdl_code += "}\n"

    return wdl_code




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
