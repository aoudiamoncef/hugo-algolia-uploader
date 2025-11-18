# Hugo Algolia Uploader

![build](https://github.com/aoudiamoncef/hugo-algolia-uploader/workflows/build/badge.svg)
![license](https://img.shields.io/github/license/aoudiamoncef/hugo-algolia-uploader)

Hugo Algolia Uploader enables you to upload your hugo algolia index file automatically.

For generic usage please see [Algolia Uploader ](https://github.com/wangchucheng/algolia-uploader).

## Requirements

This project requires Python 3.9+ and the following Python package:

- `algoliasearch>=4.0.0,<5.0.0` - Algolia Search API client library (v4)

You can install the dependencies using:

```bash
pip install -r requirements.txt
```

### Migration to v4

This project has been updated to use Algolia Python SDK v4, which includes:
- Updated import path: `from algoliasearch.search.client import SearchClient`
- Simplified client initialization: `SearchClient(app_id, api_key)`
- Direct method calls without `init_index()`
- Improved performance and modern API design

For more information, see the [Algolia Python SDK v4 documentation](https://www.algolia.com/doc/api-client/getting-started/install/python/).

## Development

### Running Tests

This project includes comprehensive unit tests to ensure code quality and reliability.

#### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

#### Run Tests

Run all tests:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=main --cov-report=term-missing
```

Run tests in verbose mode:

```bash
pytest -v
```

#### Test Coverage

The test suite covers:
- File upload functionality with various scenarios
- JSON parsing and validation
- Path construction logic
- Index name generation with multiple languages
- Environment variable handling
- Error cases (missing files, invalid JSON)

Coverage reports are generated in:
- Terminal output
- HTML format in `htmlcov/` directory
- XML format in `coverage.xml`

## Try Hugo Algolia Uploader

You can use the following example as a template to create a new file with any name under `.github/workflows/`.

```yaml
name: <action_name>

on: 
  - push

jobs:
  upload_hugo_algolia_index:
    runs-on: ubuntu-latest
    name: Upload Hugo Algolia Index
    steps:
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0
    - uses: aoudiamoncef/hugo-algolia-uploader@main
      with:
        # Such as `LAHZOUZT15`. Required
        app_id: <your_app_id>
        # You can store token in your project's 'Setting > Secrets' and reference the name here. Such as ${{ secrets.ALGOLIA_ADMIN_KEY }} . Required
        admin_key: <your_admin_key>
        # The index name. Required
        index_name: <your_index_name>
        # The index name separator. If multi languages is enabled. Default value is`_` 
        index_name_separator: <your_index_name_separator>
        # The index file directory relative to repo root. Default value is `public`
        index_file_directory: <your_index_file_directory>
        # The index file name. Default value is `index.json`
        index_file_name: <your_index_file_name>
        # The indexes i18next language codes comma separated. Ex: en,fr,tzm will upload to 3 indexes with predefined suffix: 'your_index_name + index_name_separator + your_index_language'
        index_languages: <your_index_languages>
```
