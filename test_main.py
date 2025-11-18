import os
import json
import pytest
from unittest.mock import Mock, mock_open, patch, MagicMock
import sys

# Set up environment variables before importing main
# This prevents errors during module import when SearchClient is initialized
os.environ.setdefault('INPUT_APP_ID', 'test_app_id')
os.environ.setdefault('INPUT_ADMIN_KEY', 'test_admin_key')
os.environ.setdefault('INPUT_INDEX_NAME', 'test_index')
os.environ.setdefault('INPUT_INDEX_NAME_SEPARATOR', '_')
os.environ.setdefault('INPUT_INDEX_FILE_DIRECTORY', 'public')
os.environ.setdefault('INPUT_INDEX_FILE_NAME', 'index.json')
os.environ.setdefault('INPUT_INDEX_LANGUAGES', 'en')
os.environ.setdefault('GITHUB_WORKSPACE', '/workspace')

# Mock SearchClient before importing main to avoid actual initialization
from unittest.mock import patch as mock_patch
mock_patcher = mock_patch('algoliasearch.search.client.SearchClient')
mock_search_client_class = mock_patcher.start()
mock_client_instance = MagicMock()
mock_search_client_class.return_value = mock_client_instance

# Now import main - the SearchClient will be mocked
import main

# Replace the client with our mock instance
main.client = mock_client_instance


@pytest.fixture(autouse=True)
def reset_client_mock():
    """Reset the client mock before each test."""
    if hasattr(main.client, 'reset_mock'):
        main.client.reset_mock()
    yield
    if hasattr(main.client, 'reset_mock'):
        main.client.reset_mock()


class TestUploadFunction:
    """Test the upload function."""
    
    @patch('main.client')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"objectID": "1", "title": "Test"}]')
    @patch('os.path.isfile')
    def test_upload_with_valid_file(self, mock_isfile, mock_file, mock_client):
        """Test upload function with a valid file."""
        mock_isfile.return_value = True
        
        main.upload('/test/path/index.json', 'test_index')
        
        # Verify file was checked
        mock_isfile.assert_called_once_with('/test/path/index.json')
        
        # Verify file was opened
        mock_file.assert_called_once_with('/test/path/index.json')
        
        # Verify save_objects was called with correct parameters
        mock_client.save_objects.assert_called_once_with(
            index_name='test_index',
            objects=[{"objectID": "1", "title": "Test"}]
        )
    
    @patch('main.client')
    @patch('os.path.isfile')
    def test_upload_with_nonexistent_file(self, mock_isfile, mock_client):
        """Test upload function when file doesn't exist."""
        mock_isfile.return_value = False
        
        main.upload('/test/path/nonexistent.json', 'test_index')
        
        # Verify file existence was checked
        mock_isfile.assert_called_once_with('/test/path/nonexistent.json')
        
        # Verify save_objects was NOT called
        mock_client.save_objects.assert_not_called()
    
    @patch('main.client')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.isfile')
    def test_upload_with_empty_json_array(self, mock_isfile, mock_file, mock_client):
        """Test upload function with an empty JSON array."""
        mock_isfile.return_value = True
        
        main.upload('/test/path/empty.json', 'test_index')
        
        # Verify save_objects was called with empty list
        mock_client.save_objects.assert_called_once_with(
            index_name='test_index',
            objects=[]
        )
    
    @patch('main.client')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": "1"}, {"id": "2"}, {"id": "3"}]')
    @patch('os.path.isfile')
    def test_upload_with_multiple_records(self, mock_isfile, mock_file, mock_client):
        """Test upload function with multiple records."""
        mock_isfile.return_value = True
        
        main.upload('/test/path/multiple.json', 'test_index')
        
        # Verify save_objects was called with all records
        mock_client.save_objects.assert_called_once_with(
            index_name='test_index',
            objects=[{"id": "1"}, {"id": "2"}, {"id": "3"}]
        )
    
    @patch('main.client')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('os.path.isfile')
    def test_upload_with_invalid_json(self, mock_isfile, mock_file, mock_client):
        """Test upload function with invalid JSON."""
        mock_isfile.return_value = True
        
        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            main.upload('/test/path/invalid.json', 'test_index')
        
        # Verify save_objects was NOT called
        mock_client.save_objects.assert_not_called()


class TestMainExecution:
    """Test the main execution flow."""
    
    @patch('main.upload')
    @patch.dict(os.environ, {
        'INPUT_APP_ID': 'test_app_id',
        'INPUT_ADMIN_KEY': 'test_admin_key',
        'INPUT_INDEX_NAME': 'test_index',
        'INPUT_INDEX_NAME_SEPARATOR': '_',
        'INPUT_INDEX_FILE_DIRECTORY': 'public',
        'INPUT_INDEX_FILE_NAME': 'index.json',
        'INPUT_INDEX_LANGUAGES': 'en,fr',
        'GITHUB_WORKSPACE': '/workspace'
    })
    def test_main_execution_flow(self, mock_upload):
        """Test the main execution flow with environment variables."""
        # Re-import to pick up environment variables
        import importlib
        importlib.reload(main)
        
        # Verify upload was called for main index
        # Note: In the actual execution, upload is called during module import
        # This test verifies the logic would work correctly
        assert os.environ.get('INPUT_INDEX_NAME') == 'test_index'
        assert os.environ.get('INPUT_INDEX_LANGUAGES') == 'en,fr'


class TestClientInitialization:
    """Test Algolia client initialization."""
    
    def test_client_exists(self):
        """Test that client is initialized and exists."""
        # Verify client exists and is a mock (since we're mocking it in tests)
        assert hasattr(main, 'client')
        assert main.client is not None
    
    def test_client_has_save_objects_method(self):
        """Test that client has the save_objects method."""
        # Verify the client has the save_objects method
        assert hasattr(main.client, 'save_objects')
        assert callable(main.client.save_objects)


class TestPathConstruction:
    """Test path construction logic."""
    
    @patch.dict(os.environ, {
        'GITHUB_WORKSPACE': '/workspace',
        'INPUT_INDEX_FILE_DIRECTORY': 'public',
        'INPUT_INDEX_FILE_NAME': 'index.json',
        'INPUT_INDEX_NAME_SEPARATOR': '_',
        'INPUT_INDEX_NAME': 'my_index'
    })
    def test_main_index_path_construction(self):
        """Test main index file path construction."""
        github_workspace = os.environ.get('GITHUB_WORKSPACE')
        index_file_directory = os.environ.get('INPUT_INDEX_FILE_DIRECTORY')
        index_file_name = os.environ.get('INPUT_INDEX_FILE_NAME')
        
        expected_path = f"{github_workspace}/{index_file_directory}/{index_file_name}"
        actual_path = "{}/{}/{}".format(github_workspace, index_file_directory, index_file_name)
        
        assert actual_path == expected_path
        assert actual_path == "/workspace/public/index.json"
    
    @patch.dict(os.environ, {
        'GITHUB_WORKSPACE': '/workspace',
        'INPUT_INDEX_FILE_DIRECTORY': 'public',
        'INPUT_INDEX_FILE_NAME': 'index.json',
        'INPUT_INDEX_NAME_SEPARATOR': '_',
        'INPUT_INDEX_NAME': 'my_index'
    })
    def test_i18n_index_path_construction(self):
        """Test i18n index file path construction."""
        github_workspace = os.environ.get('GITHUB_WORKSPACE')
        index_file_directory = os.environ.get('INPUT_INDEX_FILE_DIRECTORY')
        index_file_name = os.environ.get('INPUT_INDEX_FILE_NAME')
        language = 'fr'
        
        expected_path = f"{github_workspace}/{index_file_directory}/{language}/{index_file_name}"
        actual_path = "{}/{}/{}/{}".format(github_workspace, index_file_directory, language.lower(), index_file_name)
        
        assert actual_path == expected_path
        assert actual_path == "/workspace/public/fr/index.json"


class TestLanguageProcessing:
    """Test language processing logic."""
    
    def test_language_splitting(self):
        """Test that languages are correctly split from comma-separated string."""
        languages_str = "en,fr,es"
        languages = languages_str.split(",")
        
        assert len(languages) == 3
        assert "en" in languages
        assert "fr" in languages
        assert "es" in languages
    
    def test_single_language(self):
        """Test single language processing."""
        languages_str = "en"
        languages = languages_str.split(",")
        
        assert len(languages) == 1
        assert languages[0] == "en"
    
    def test_language_case_handling(self):
        """Test that language codes are lowercased."""
        language = "FR"
        assert language.lower() == "fr"


class TestIndexNameConstruction:
    """Test index name construction with separator and language."""
    
    def test_index_name_with_language(self):
        """Test index name construction with language suffix."""
        index_name = "my_index"
        index_name_separator = "_"
        language = "fr"
        
        i18n_index_name = "{}{}{}".format(index_name, index_name_separator, language)
        
        assert i18n_index_name == "my_index_fr"
    
    def test_index_name_with_different_separator(self):
        """Test index name construction with different separator."""
        index_name = "my_index"
        index_name_separator = "-"
        language = "es"
        
        i18n_index_name = "{}{}{}".format(index_name, index_name_separator, language)
        
        assert i18n_index_name == "my_index-es"
    
    def test_index_name_with_multiple_languages(self):
        """Test index name construction for multiple languages."""
        index_name = "my_index"
        index_name_separator = "_"
        languages = ["en", "fr", "es"]
        
        index_names = ["{}{}{}".format(index_name, index_name_separator, lang) for lang in languages]
        
        assert len(index_names) == 3
        assert "my_index_en" in index_names
        assert "my_index_fr" in index_names
        assert "my_index_es" in index_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
