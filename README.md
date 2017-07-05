# code-classifier-dataset
This repo contains dataset for code classifier to be implemented in oppia-ml.

The dataset is raw and hasn't been tagged yet. These programs are extracted from answer history
of [euler exploration](https://www.oppia.org/explore/1) from [Oppia.org](https://www.oppia.org).

* dataset.json: contains all the programs which were extracted from euler exploration from Oppia (~11000 programs).
* syntax_dataset.json: contains all programs which are syntactically correct (7092).
* compiled_dataset.json contains all programs which are getting ecompiled (7061).
* execd_dataset.json: contains all programs which are getting executed and don’t raise exception during execution (63).
