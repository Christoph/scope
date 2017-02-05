import numpy as np
import pandas as pd

import research.compare_workflow_functions as funcs

# always reload other scripts
reload(funcs)

data = funcs.preprocess(False)

similarities = funcs.semantic_analysis(data, 20)

articles = funcs.compute_clusterings(similarities["custom"][0], data)
