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
1. Post new taxonomy terms, record ids
2. Post new levy_collection_names, record ids
3. Post new collection_name paragraphs, record ids
4. Post new collection_item_images, get ids
5. Construct levy_collection_items json using ids
6. Post levy_collection_items
7. Update `parent_id` in collection_name paragraphs with `drupal_internal__nid` from `levy_collection_items`, record `drupal_internal__revision_id`
8. Update `field_people` with `type`, `id`, and `target_revision_id` from collection_name
9.
