import os
import json
import asyncio

from algoliasearch.search.client import SearchClient

client = SearchClient(os.environ.get("INPUT_APP_ID"), os.environ.get("INPUT_ADMIN_KEY"))
index_name = os.environ.get("INPUT_INDEX_NAME")
index_name_separator = os.environ.get("INPUT_INDEX_NAME_SEPARATOR")
index_file_directory = os.environ.get("INPUT_INDEX_FILE_DIRECTORY")
index_file_name = os.environ.get("INPUT_INDEX_FILE_NAME")
languages = os.environ.get("INPUT_INDEX_LANGUAGES").split(",")
github_workspace = os.environ.get("GITHUB_WORKSPACE")


async def upload(path, index_name_to_upload):
    if os.path.isfile(path):
        with open(path) as f:
            records = json.load(f)
            await client.save_objects(
                index_name=index_name_to_upload,
                objects=records
            )


async def main():
    await upload("{}/{}/{}".format(github_workspace, index_file_directory, index_file_name), index_name)

    for language in languages:
        i18n_index_name = "{}{}{}".format(index_name, index_name_separator, language)
        await upload("{}/{}/{}/{}".format(github_workspace, index_file_directory, language.lower(), index_file_name), i18n_index_name)


if __name__ == "__main__":
    asyncio.run(main())
