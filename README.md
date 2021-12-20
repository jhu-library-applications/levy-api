# Levy Sheet Music Drupal Sites

Test Instance: https://levy-test.mse.jhu.edu (Can only access while on VPN)

Production Instance: https://levysheetmusic.mse.jhu.edu/

## Drupal settings required for these scripts

Install [JSON:API module](https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/api-overview)
 - Go to www.example.edu/admin/modules, navigate to Web Services, and check `JSON:API`
 - Got to www.example.edu/admin/config/services/jsonapi and click "Accept all JSON:API create, read, update, and delete operations."

Install [Paragraph Type Permissions sub-module](https://www.drupal.org/project/paragraphs)
 - Go to www.example.edu/admin/modules, navigate to Paragraphs, and check `Paragraphs Type Permissions`
 - Go to www.example.edu/admin/people/permissions, navigate to Paragraph Type Permissions, and check View Content for the paragraph types to change.

## Authentication

In your /post folder, please create a `secrets.py` file that contains the following information. This information will be used in the scripts that require authentication to post to Drupal.

```python
username='username'
password='password'
```

In order to ensure that this file is not uploaded to GitHub, add `secrets.py` to  your `.gitignore`.

## Wiki
Please see the [wiki](https://github.com/mjanowiecki/levy-api/wiki) for instructions and more information about the API.
