# SmooSense Python SDK

SmooSense is a web-based application for exploring and analyzing large-scale multi-modal tabular data. It provides an intuitive interface for working with CSV, Parquet, and other data formats with powerful SQL querying capabilities.

This repo contains source code for "SmooSense Python SDK".

## Feature highlights
- Natively visualize multimodal data (images, videos, json, bbox, image mask, 3d assets etc)
- Effortlessly look at distribution. Automatic drill-through from statistics to random samples.
- Graphical and interactive slice-n-dice of your dataset.
- Large scale support for 100 million rows on your laptop.
- Easy to integrate; SmooSense directly work with table file (parquet, csv, jsonl, etc)
- Low cost. Free and open source to use on your laptop. Compute efficient when deployed.

Demo: <https://demo.smoosense.ai>

## How to use
### CLI
Install [uv](https://docs.astral.sh/uv/#highlights), and then
```bash
uv tool install -U smoosense
```
In terminal, `cd` into the folder containing your data files, and then run `sense`

### Jupyter Notebook
```bash
pip install -U "smoosense[jupyter]"
```
Inside Jupyter notebook:
```python
from smoosense.widget import Sense
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randn(500, 5), columns=["a", "b", "c", "d", "e"])

Sense(df)  # Displays automatically in Jupyter
```

## License

"SmooSense Python SDK" is licensed under **Apache 2.0 + Commons Clause**.

### The license permits

- ✅ **Running on localhost/127.0.0.1**: Development, testing, personal and commercial use on your local machine.
- ✅ **Creating derivative works**: Build upon SmooSense for your own projects. Read "Bundled Content" below.
- ✅ **Dependency**: You can include `smoosense` as a dependency of your open-source or commercial products. Your customers are free to use SmooSense on localhost, and it is their responsibility to acquire deployment license for production use.


### The license does not permit
- ❌ **SaaS offerings**: Providing SmooSense as a service to customers. 
    - License fee is required when deployment domain is not localhost/127.0.0.1.
- ❌ **Commercial redistribution**: Selling or licensing SmooSense to third parties.
    - Adding `smoosense` as a Python dependency is not considered as redistribution.


### Bundled Content

Files in `smoosense/statics` contain bundled TypeScript code licensed under Apache 2.0 + Commons Clause.
You are free to use the bundled code as-is, but it is not meant for modification.
Original source files are available under the Business Source License (BSL).

### Get a Commercial License

For commercial licensing questions, please contact SmooSense.

See the full [LICENSE](LICENSE) file for complete terms and conditions.
