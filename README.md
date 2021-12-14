# levy-api

test: https://levy-test.mse.jhu.edu

prod: https://levysheetmusic.mse.jhu.edu/


Drupal JSON:API module: https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/api-overview

## Entities in Levy Sheet Music:

### Nodes
- levy_collection_item
- levy_collection_names

### Paragraphs
 - collection_duplicate_reference
 - collection_item_image
 - collection_name

### Taxonomies
 - c
 - composition_metadata
 - creator_r
 - instrumentation_metadata
 - publishers
 - subjects

## To upload new items:

### Prep data
1. Get existing taxonomy terms from Drupal
    - script: [`get/getTaxonomyIdentifiers.py`](https://github.com/mjanowiecki/levy-api/blob/main/get/getTaxonomiesIdentifiers.py)
    - outputs: `levy-api/taxonomies` (spreadsheets containing all existing taxonomy terms)
2. Get existing levy_collection_names from Drupal
    - script: [`get/getNode_levy_collection_names.py`](https://github.com/mjanowiecki/levy-api/blob/main/get/getNode_levy_collection_names.py)
    - output: `allCollectionNames.csv` (spreadsheet containing all existing levy_collection_names)
3. Get list taxonomy terms and names from spreadsheet of new data
    - input:
        - `allCollectionNames.csv` (spreadsheet containing all existing levy_collection_names)
        - `levy-api/taxonomies` (spreadsheets containing all existing taxonomy terms)
        - spreadsheet of new data
    - script: [`explodeTaxonomiesAndNames.py`](https://github.com/mjanowiecki/levy-api/blob/main/explodeTaxonomiesAndNames.py)
    - output:
        - `levy-api/aggregated` (spreadsheet of taxonomy terms aggregated by taxonomy name)
        - `levy-api/aggregated-role` (spreadsheets of levy_collection_names grouped by role and aggregated by title)
4. Compare new taxonomy terms to existing terms in Drupal
    - input:
        - `levy-api/taxonomies`
        - `levy-api/aggregated`
    - script: [`findExistingTaxTermsAndTermsToCreate.py`](https://github.com/mjanowiecki/levy-api/blob/main/findExistingTaxTermsAndTermsToCreate.py)
    - output:
        - `levy-api/merged` (spreadsheets of taxonomy terms merged with Drupal identifiers, if they exist)
        - `taxonomyTermsDone.csv` (list of taxonomy terms that already exist in Drupal)
        - `taxonomyTermsToCreate.csv` (list of taxonomy that DO NOT exist in Drupal and need to be created)

5. Compare new levy_collection_names to existing terms in Drupal
    - input:
        - `allCollectionNames.csv` (spreadsheet containing all existing levy_collection_names)
        - `levy-api/aggregated-role` (spreadsheets of levy_collection_names grouped by role and aggregated by title)
    - script: [`findExistingCollNamesAndNamesToCreate.py`](https://github.com/mjanowiecki/levy-api/blob/main/findExistingCollNamesAndNamesToCreate.py)
    - output:
        - `mergedCollectioinNames.csv`
        - `levy_collection_namesDone.csv`
        - `levy_collection_namesToCreate.csv`

### Post data
1. Post new taxonomy terms, record identifiers
    - script: `postTaxonomyTerms.py`
    - results: `logOfTaxonomyTermsAdded.csv`
2. Post new levy_collection_names, record identifiers
    - script: `postNode_levy_collection_names.py`
    - results: `logOfLevyCollectionNamesAdded.csv`
3. Create spreadsheet for collection_name paragraphs for each `field_people` field, using levy_collection_names and creator_r identifiers.
4. Post new collection_name paragraphs, record identifiers
    - script: `postParagraph_collection_name.py`
    - results: `logofParagraphCollectionNames.csv`
5. Post new files to Drupal site & create associated collection_item_images paragraphs, record identifiers
    - script: `postFilesAndParagraph_collection_item_images.py`
    - results: `logofParagraphCollectionItemImages.csv`
6. Construct levy_collection_items json using taxonomy, collection_name, and collection_item_images identifiers
7. Post levy_collection_items
    - Update `parent_id` in collection_name paragraphs with `drupal_internal__nid` from `levy_collection_items`, record `drupal_internal__revision_id`
    - Update `parent_id` in collection_item_image paragraphs with `drupal_internal__nid` from levy_collection_items
    - Update `field_people` with `type`, `id`, and `target_revision_id` from collection_name
    - Update `field_images` with `type`, `id`, and `target_revision_id` from collection_item_image
