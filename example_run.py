
from src.WDLMerge import *
from os.path import basename, splitext

def merge_wdls_and_validate(*wdls):
    merged_wdl = None
    merged_wdl_path = None
    
    try:
        # Upgrade and validate each WDL
        for wdl in wdls:
            upgrade_wdl(wdl)
            validate_wdl(wdl)
        
        # Merge WDLs
        merged_wdl = merge_wdls(WDLs=wdls, tasks_order=['run_QC', 'detect_doublets'])
        # Create a merged WDL file path
        wdl_names = [splitext(basename(wdl))[0] for wdl in wdls]
        merged_wdl_path = f"examples/{'_'.join(wdl_names)}_merged.wdl"
        
        # Write merged WDL to file
        with open(merged_wdl_path, 'w') as file:
            file.write(merged_wdl)
        print(f"Merged WDL file created at: {merged_wdl_path}")
        print('Manually resolve any validation errors in the merged WDL.')
        # Validate merged WDL
        validate_wdl(merged_wdl_path)
        
    except Exception as e:
        print(f"Error occurred during WDL merging and validation: {str(e)}")
        if merged_wdl_path is not None:
            os.remove(merged_wdl_path)
    
    return merged_wdl_path

# Example usage
wdl1='examples/Cartography_QC_h5_R_12.wdl'
wdl2='examples/Cartography_scrublet_9.wdl'

merged_wdl_path = merge_wdls_and_validate(wdl1, wdl2)

if merged_wdl_path is not None:
    print('Done')
else:
    print('Error occurred during WDL merging and validation.')
