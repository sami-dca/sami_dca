"""
Utility used to extract information from the source code of `./models.py`
for the "Database" section of the Sami Paper.
The processed document is output in the local file `models.md`.
"""

from pathlib import Path
from models import all_models
from numpydoc.docscrape import ClassDoc

output_file = Path(__file__).parent / 'models.md'

# Define templates

table_doc_template = """### `{table}`
{desc}
{cols}
"""

bullet_point_template = "- `{type}` `{name}` - {desc}\n"

# Parse the models

output = '## Database tables\n\n'
for model in all_models:
    doc = ClassDoc(model)

    cols = ''
    for parameter in doc['Attributes']:
        cols += bullet_point_template.format(
            type=parameter.type,
            name=parameter.name,
            desc=' '.join(parameter.desc)
        )

    output += table_doc_template.format(
        table=model.__tablename__,
        desc=' '.join(doc['Summary']),
        cols=cols,
    )

output_file.write_text(output)
