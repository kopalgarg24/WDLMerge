# WDLMerge
Merge WDLs
## Installation
Install WDLMerge with pip
```bash
  pip install -i https://test.pypi.org/simple/ WDLMerge==0.0.9
  pip install miniwdl
```
## Requirements
* miniwdl

## To run in Google Colab
```python
from WDLMerge import *
import WDL
import asyncio
import nest_asyncio
import WDL

# Allow nested event loops in Jupyter notebook
nest_asyncio.apply()
```

## Examples

### Merge WDLs
```python
wdl=merge_wdls(WDLs=["WDL_1.wdl", "WDL_2.wdl"])
```

### Upgrade WDL
```python
validate_wdl('WDL_1.wdl')
```

### Validate WDL
```python
# Get a WDL written in one of the older versions
!wget https://raw.githubusercontent.com/gatk-workflows/gatk4-germline-snps-indels/1.1.2/joint-discovery-gatk4-local.wdl
upgrade_wdl('joint-discovery-gatk4-local.wdl')
```
