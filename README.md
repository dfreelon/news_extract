# news_extract
 Python module to extract articles from NexisUni and Factiva.
 
## Requirements

pandas

## Installation

```pip install news_extract```

## Overview

```news_extract``` allows the output of the NexisUni and Factiva databases to be imported into Python. **Note, you must export your documents manually first! This module does not scrape the databases directly; rather, it extracts articles and associated metadata from pre-exported output files.** To use it, you must subscribe to at least one of these databases and use the following instructions to export your articles from each database:

### NexisUni export instructions

1. Make sure you are exporting full documents with no attachments, not just the results list.
2. Export in RTF format.
3. Save documents in a single file.
4. Uncheck all options on the "Formatting Options" tab.

### Factiva export instructions

1. For Factiva, you must export your documents using the Firefox browser.
2. After conducting your search, click the "View Selected Articles" button that looks like an eye.
3. On the right, click the "Display Options" text and select "Full Article/Report plus Indexing."
4. Click the "Format for Saving" button that looks like a 3.5" floppy disk and select "Article Format."
5. On the resulting page, select "Save Page As..." from the Firefox menu.
6. In the "Save as type" dropdown, select "Text Files" and save your file.

Once you've exported your file(s), you can do the following:

```python
import news_extract as ne
nu_file = 'results1.rtf' #file exported from NexisUni
fc_file = 'results2.txt' #file exported from Factiva
nu_data = ne.nexis_rtf_extract(nu_file)
fc_data = ne.factiva_extract(fc_file)

print(nu_data[0].keys()) #view field names for NexisUni articles
print(fc_data[0].keys()) #view field names for first Factiva article

for i in nu_data:
    print(i['HEADLINE']) #show all NexisUni headlines
for i in fc_data:
    print(i['HD']) #show all Factiva headlines
```

## Output

Both ```nexis_rtf_extract``` and ```factiva_extract``` return lists of dicts wherein each dict corresponds to an article. The dict keys are field names, while the dict values are the metadata. One major difference between the two functions is that ```nexis_rtf_extract``` outputs the same set of metadata for all articles, while ```factiva_extract``` auto-extracts the specific field names and values attached to each article. This is due to differences in how the two types of files are formatted.

## Combining Factiva and NexisUni output

### Converting fieldnames

You can use the function ```fix_fac_fieldnames``` to convert Factiva fieldnames to their longer and more descriptive NexisUni equivalents like so:

```python
fc_converted = ne.fix_fac_fieldnames(fc_data) #note that this will only convert eight common field names, leaving the rest intact
```

### Merging Factiva and NexisUni data into a single Pandas variable

If you want to analyze data from NexisUni and Factiva in the same project, here's how to do it:

```python
nu_plus_fc = nu_data + fc_converted
combined = ne.news_export(nu_plus_fc)
```

The ```news_export``` function performs several operations, including removing duplicates (using a custom algorithm based on the Jaccard coefficient and time of publication) and resolving conflicts between articles with different metadata fields. For the latter, the function attempts to export all fields included in at least half the articles. This proportion can be adjusted using the ```field_threshold``` parameter.

By default, ```news_export``` returns a Pandas DataFrame containing the output data. You can save individual JSON files to disk (i.e. one article per file) by setting the ```to_pandas``` parameter to ```False```.
