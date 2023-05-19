from src.WDLMerge import *
from os.path import basename, splitext

wdl1='examples/Cartography_QC_h5_R_12.wdl'
wdl2='examples/Cartography_scrublet_9.wdl'

wdl_1_name = splitext(basename(wdl1))[0]
wdl_2_name = splitext(basename(wdl2))[0]

merged_wdl_1 = f"examples/{wdl_1_name}_{wdl_2_name}_merged.wdl"

# Upgrade WDL
upgrade_wdl(wdl1)
upgrade_wdl(wdl1)

# Validate WDL
validate_wdl(wdl1)
validate_wdl(wdl2)

# Merge WDLs
merged_wdl=merge_wdls(WDLs=[wdl2, wdl1])

with open(merged_wdl_1, 'w') as file:
    file.write(merged_wdl)

#upgrade_wdl(merged_wdl_1)
print('Manually resolve the following errors:\n')

validate_wdl(merged_wdl_1)


# in runtime replace = with :
# add a version 1.0 at top
# move workflow at top
# specify the order 
# calls in workflow should have , after inputs 